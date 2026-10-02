"""02 - Uzun göz kapalı bloktan öznitelik çıkarma, v2 (salt okuma, sınıflandırma yok, grup testi yok).

Önceden belirlenmiş birincil analiz: CLAUDE.md "Önceden belirlenmiş birincil analiz" bölümü (2026-10-01).
Kaynak: v1.0.0/sub-*/eeg/*_desc-preprocessed_eeg.set (128 Hz, 128 EEG, ortalama referans).

v1 -> v2 değişiklikleri
  - Göreli güç paydası 1-30 Hz; gama öznitelik değil.
  - FOOOF birincil 'fixed' 3-30 Hz; duyarlılık 'knee' 2-30 Hz (model sütunu: primary / knee).
  - IAF: birincil FOOOF tepesi (7-13 Hz), ikincil düzleştirilmiş spektrumda 7-13 Hz CoG; argmax kaldırıldı.
  - EMG indeksi (log-log eğim 30-40 Hz) ve kanal dışlama: R² < 0,9 veya EMG robust z > 3 (tam kesitte belirlenir).
  - ROI öznitelikleri yalnız kalan kanalların ortalama spektrumundan.
  - Segmentler: full (465 s), H1, H2 (232,5 s); 30 s pencerelerde teta/alfa zaman serisi ve eğimi.

Çıktılar (analysis/):
  02_features_v2_2026-10-01_channels.csv     denek x segment x model x kanal
  02_features_v2_2026-10-01_roi.csv          denek x segment x model x ROI
  02_features_v2_2026-10-01_ta_timeseries.csv denek x ROI x 30 s pencere
  02_features_v2_2026-10-01_subject_qc.csv   denek başına QC özeti
  02_features_v2_2026-10-01_skipped.csv      işlenemeyen denekler ve nedeni
  02_features_v2_2026-10-01_psd_full.npz     tam kesit kanal PSD'leri
  02_descriptive_by_group_v2_2026-10-01.csv / .md  yalnız betimsel grup tablosu
Kullanım: python 02_features_v2_2026-10-01.py [--subjects sub-A ...] [--workers 8]
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse, re, warnings
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.signal import welch

warnings.filterwarnings("ignore", category=DeprecationWarning)
from fooof import FOOOF  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "v1.0.0"
OUT = ROOT / "analysis"
STEM = "02_features_v2_2026-10-01"

# ---- Önceden belirlenmiş parametreler (CLAUDE.md) ----
BLOCK_SKIP_S, BLOCK_LEN_S = 5.0, 465.0
WIN_S, OVERLAP = 4.0, 0.5
TOTAL_BAND = (1.0, 30.0)
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
MODELS = {"primary": dict(aperiodic_mode="fixed", freq_range=(3.0, 30.0)),
          "knee": dict(aperiodic_mode="knee", freq_range=(2.0, 30.0))}
FOOOF_KW = dict(peak_width_limits=(1.0, 8.0), max_n_peaks=6, min_peak_height=0.1, verbose=False)
ALPHA_RANGE = (7.0, 13.0)
EMG_RANGE = (30.0, 40.0)
R2_MIN, EMG_Z_MAX = 0.9, 3.0
TA_WIN_S = 30.0
ROIS = {  # Biosemi 128 ABCD -> 10-20 yaklaşığı (channels.tsv açıklamalarından)
    "posterior": ["A15", "A23", "A28", "A10", "B7", "A21", "A17", "A30", "A19"],   # O1 Oz O2 PO7 PO8 POz PO3 PO4 Pz
    "central":   ["A1", "D19", "B22", "A3", "D14", "B20"],                          # Cz C3 C4 CPz C1 C2
    "frontal":   ["C21", "D4", "C4", "C23", "C25", "C12", "C19"],                   # Fz F3 F4 FCz F1 F2 AFz
    "global":    None,
}


def load_block(sub):
    p = DS / sub / "eeg" / f"{sub}_task-restingstate_desc-preprocessed_eeg.set"
    E = loadmat(p, squeeze_me=True, struct_as_record=False, simplify_cells=True)
    if isinstance(E["data"], str):
        raise RuntimeError(f"veri harici dosyada ve dosya yok: {E['data']}")
    sr = float(E["srate"]); x = np.asarray(E["data"], dtype=np.float64)
    labels = [c["labels"] for c in E["chanlocs"]]
    evs = E["event"] if isinstance(E["event"], (list, np.ndarray)) else [E["event"]]
    co = [(int(e["edftype"]), float(e["latency"])) for e in evs if str(e.get("edftype")) in ("64", "128")]
    closed = [i for i, (c, _) in enumerate(co) if c == 64]
    if len(closed) < 3:
        raise RuntimeError("3. göz kapalı işareti yok (uzun blok yok)")
    j = closed[2]
    blk_start = co[j][1] - 1
    blk_end = co[j + 1][1] - 1 if j + 1 < len(co) else x.shape[1]
    s0 = int(round(blk_start + BLOCK_SKIP_S * sr)); s1 = s0 + int(round(BLOCK_LEN_S * sr))
    if s1 > blk_end:
        raise RuntimeError(f"blok kısa: {(blk_end - blk_start) / sr:.1f} s")
    meta = dict(block_marker_s=round(blk_start / sr, 2), block_avail_s=round((blk_end - blk_start) / sr, 1),
                seg_start_s=round(s0 / sr, 2), seg_end_s=round(s1 / sr, 2))
    return x[:, s0:s1], sr, labels, meta


def psd(x, sr):
    n = int(WIN_S * sr)
    return welch(x, fs=sr, window="hann", nperseg=n, noverlap=int(n * OVERLAP), detrend="constant", axis=-1)


def band_feats(f, p):
    """p: (..., nfreq). Göreli güç 1-30 Hz toplamına göre."""
    df = f[1] - f[0]
    tot = p[..., (f >= TOTAL_BAND[0]) & (f < TOTAL_BAND[1])].sum(-1) * df
    out = {"log10_power_1_30": np.log10(tot)}
    for b, (lo, hi) in BANDS.items():
        out[f"rel_{b}"] = p[..., (f >= lo) & (f < hi)].sum(-1) * df / tot
    return out


def emg_feats(f, p):
    """EMG indeksi = log10 PSD - log10 f eğimi, 30-40 Hz (vektörel). Ek: 30-40 / 1-40 Hz güç oranı."""
    m = (f >= EMG_RANGE[0]) & (f <= EMG_RANGE[1])
    lx = np.log10(f[m]); ly = np.log10(p[..., m])
    lxc = lx - lx.mean()
    slope = (ly - ly.mean(-1, keepdims=True)) @ lxc / (lxc @ lxc)
    df = f[1] - f[0]
    ratio = p[..., m].sum(-1) / p[..., (f >= 1) & (f <= 40)].sum(-1)
    return {"emg_slope_30_40": slope, "emg_ratio_30_40": ratio * 1.0}


def fit(f, p, model):
    cfg = MODELS[model]
    fm = FOOOF(aperiodic_mode=cfg["aperiodic_mode"], **FOOOF_KW)
    nan = dict(ap_offset=np.nan, ap_knee=np.nan, ap_exponent=np.nan, fooof_r2=np.nan, fooof_error=np.nan,
               n_peaks=np.nan, iaf_fooof=np.nan, alpha_pw=np.nan, alpha_bw=np.nan, iaf_cog=np.nan, fit_ok=False)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fm.fit(f, p, cfg["freq_range"])
    except Exception:  # noqa
        return nan
    if not fm.has_model or not np.all(np.isfinite(fm.aperiodic_params_)):
        return nan
    ap = fm.aperiodic_params_
    off, exp = ap[0], ap[-1]; knee = ap[1] if len(ap) == 3 else np.nan
    pk = fm.peak_params_ if fm.peak_params_.size else np.empty((0, 3))
    a = pk[(pk[:, 0] >= ALPHA_RANGE[0]) & (pk[:, 0] <= ALPHA_RANGE[1])] if len(pk) else pk
    cf, pw, bw = a[np.argmax(a[:, 1])] if len(a) else (np.nan, np.nan, np.nan)
    # İkincil IAF: düzleştirilmiş (aperiodik çıkarılmış, log10) spektrumda pozitif artığın ağırlık merkezi
    fr = fm.freqs; flat = np.clip(fm._spectrum_flat, 0, None)
    m = (fr >= ALPHA_RANGE[0]) & (fr <= ALPHA_RANGE[1])
    cog = float((fr[m] * flat[m]).sum() / flat[m].sum()) if flat[m].sum() > 0 else np.nan
    return dict(ap_offset=off, ap_knee=knee, ap_exponent=exp, fooof_r2=fm.r_squared_, fooof_error=fm.error_,
                n_peaks=len(pk), iaf_fooof=cf, alpha_pw=pw, alpha_bw=bw, iaf_cog=cog, fit_ok=True)


def robust_z(v):
    med = np.median(v); mad = 1.4826 * np.median(np.abs(v - med))
    return (v - med) / mad if mad > 0 else np.zeros_like(v)


def process(sub):
    grp = re.search(r"(sg2|sg|cg)$", sub).group(1)
    x, sr, labels, meta = load_block(sub)
    N = x.shape[1]; h = N // 2
    segs = {"full": x, "H1": x[:, :h], "H2": x[:, h:]}
    spectra = {k: psd(v, sr) for k, v in segs.items()}
    f, pfull = spectra["full"]

    # --- Kanal dışlama (tam kesit, birincil model) ---
    emg_full = emg_feats(f, pfull)
    prim_full = [fit(f, pfull[i], "primary") for i in range(len(labels))]
    r2 = np.array([d["fooof_r2"] for d in prim_full])
    ez = robust_z(emg_full["emg_slope_30_40"])
    excl_r2 = ~(r2 >= R2_MIN)          # NaN (başarısız fit) da dışlanır
    excl_emg = ez > EMG_Z_MAX
    excluded = excl_r2 | excl_emg
    keep = ~excluded

    ch_rows, roi_rows = [], []
    for seg, (fs, ps) in spectra.items():
        bf = band_feats(fs, ps); ef = emg_feats(fs, ps)
        for model in MODELS:
            fits = prim_full if (seg == "full" and model == "primary") else [fit(fs, ps[i], model) for i in range(len(labels))]
            for i, lab in enumerate(labels):
                ch_rows.append(dict(subject=sub, group=grp, segment=seg, model=model, channel=lab,
                                    excluded=bool(excluded[i]), excl_r2=bool(excl_r2[i]), excl_emg=bool(excl_emg[i]),
                                    emg_robust_z_full=float(ez[i]),
                                    **{k: float(v[i]) for k, v in bf.items()}, **{k: float(v[i]) for k, v in ef.items()},
                                    **fits[i]))
        for roi, chs in ROIS.items():
            idx = np.arange(len(labels)) if chs is None else np.array([labels.index(c) for c in chs])
            idx_keep = idx[keep[idx]]
            if len(idx_keep) == 0:
                for model in MODELS:
                    roi_rows.append(dict(subject=sub, group=grp, segment=seg, model=model, roi=roi,
                                         n_ch_roi=len(idx), n_ch_used=0))
                continue
            p = ps[idx_keep].mean(0)
            b = {k: float(v) for k, v in band_feats(fs, p).items()}
            e = {k: float(v) for k, v in emg_feats(fs, p).items()}
            for model in MODELS:
                roi_rows.append(dict(subject=sub, group=grp, segment=seg, model=model, roi=roi,
                                     n_ch_roi=len(idx), n_ch_used=len(idx_keep), **b, **e, **fit(fs, p, model)))

    # --- Teta/alfa zaman serisi: ardışık, örtüşmesiz 30 s pencereler ---
    wn = int(TA_WIN_S * sr); nw = N // wn
    ta_rows = []
    for w in range(nw):
        fw, pw_ = psd(x[:, w * wn:(w + 1) * wn], sr)
        df = fw[1] - fw[0]
        th = pw_[:, (fw >= 4) & (fw < 8)].sum(-1) * df
        al = pw_[:, (fw >= 8) & (fw < 13)].sum(-1) * df
        for roi, chs in ROIS.items():
            idx = np.arange(len(labels)) if chs is None else np.array([labels.index(c) for c in chs])
            idx = idx[keep[idx]]
            if len(idx) == 0:
                continue
            t, a = th[idx].mean(), al[idx].mean()
            ta_rows.append(dict(subject=sub, group=grp, roi=roi, window=w + 1,
                                t_mid_min=round((w + 0.5) * TA_WIN_S / 60, 3),
                                theta_power=t, alpha_power=a, ta_ratio=t / a, log10_ta=np.log10(t / a)))
    ta = pd.DataFrame(ta_rows)
    slopes = {}
    for roi, g in ta.groupby("roi"):
        slopes[roi] = float(np.polyfit(g.t_mid_min, g.log10_ta, 1)[0]) if len(g) >= 3 else np.nan

    roi = pd.DataFrame(roi_rows)
    rp = roi[(roi.segment == "full") & (roi.model == "primary")].set_index("roi")
    qc = dict(subject=sub, group=grp, **meta, n_ta_windows=nw,
              n_excluded=int(excluded.sum()), n_excl_r2=int(excl_r2.sum()), n_excl_emg=int(excl_emg.sum()),
              n_excl_both=int((excl_r2 & excl_emg).sum()),
              emg_slope_median_all=float(np.median(emg_full["emg_slope_30_40"])),
              emg_slope_median_kept=float(np.median(emg_full["emg_slope_30_40"][keep])) if keep.any() else np.nan,
              emg_ratio_median_all=float(np.median(emg_full["emg_ratio_30_40"])),
              r2_median_all_ch=float(np.nanmedian(r2)), r2_min_ch=float(np.nanmin(r2)),
              n_fit_failed_ch=int(np.isnan(r2).sum()),
              r2_roi_posterior=float(rp.loc["posterior", "fooof_r2"]) if "fooof_r2" in rp else np.nan,
              r2_roi_global=float(rp.loc["global", "fooof_r2"]) if "fooof_r2" in rp else np.nan,
              n_ch_used_posterior=int(rp.loc["posterior", "n_ch_used"]),
              ta_slope_global=slopes.get("global", np.nan), ta_slope_posterior=slopes.get("posterior", np.nan),
              ta_slope_frontal=slopes.get("frontal", np.nan), ta_slope_central=slopes.get("central", np.nan))
    return dict(sub=sub, ch=pd.DataFrame(ch_rows), roi=roi, ta=ta, qc=qc,
                f=f, pfull=pfull.astype(np.float32), labels=labels)


def describe_by_group(qc):
    metrics = {
        "emg_slope_median_all": "EMG indeksi: kanal medyanı, 30-40 Hz log-log eğim (tüm 128 kanal)",
        "emg_ratio_median_all": "EMG oranı: kanal medyanı, güç 30-40 / 1-40 Hz (tüm kanallar)",
        "n_excluded": "Dışlanan kanal sayısı (toplam)",
        "n_excl_r2": "  ...FOOOF R² < 0,9 nedeniyle",
        "n_excl_emg": "  ...EMG robust z > 3 nedeniyle",
        "r2_median_all_ch": "FOOOF R² (birincil): kanal medyanı",
        "r2_roi_posterior": "FOOOF R² (birincil): posterior ROI",
        "r2_roi_global": "FOOOF R² (birincil): global ROI",
        "ta_slope_global": "Teta/alfa eğimi (log10 oran / dk), global",
        "ta_slope_posterior": "Teta/alfa eğimi (log10 oran / dk), posterior",
    }
    rows = []
    for m, desc in metrics.items():
        for g in ["sg", "sg2", "cg"]:
            v = qc.loc[qc.group == g, m].dropna()
            rows.append(dict(metric=m, description=desc.strip(" ."), group=g, n=len(v), mean=v.mean(), sd=v.std(),
                             median=v.median(), q1=v.quantile(.25), q3=v.quantile(.75), min=v.min(), max=v.max()))
    return pd.DataFrame(rows), metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", nargs="*")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--outdir", default=None, help="test çalıştırmaları için farklı çıktı klasörü")
    a = ap.parse_args()
    global OUT
    if a.outdir:
        OUT = Path(a.outdir); OUT.mkdir(parents=True, exist_ok=True)
    subs = a.subjects or sorted(p.name for p in DS.glob("sub-*") if p.is_dir())
    res, skipped = [], []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(process, s): s for s in subs}
        for k, fu in enumerate(as_completed(futs), 1):
            s = futs[fu]
            try:
                res.append(fu.result()); print(f"[{k}/{len(subs)}] {s} ok", flush=True)
            except Exception as e:  # noqa
                skipped.append(dict(subject=s, reason=str(e))); print(f"[{k}/{len(subs)}] {s} ATLANDI: {e}", flush=True)
    res.sort(key=lambda r: r["sub"])
    pd.concat([r["ch"] for r in res]).to_csv(OUT / f"{STEM}_channels.csv", index=False, encoding="utf-8-sig")
    pd.concat([r["roi"] for r in res]).to_csv(OUT / f"{STEM}_roi.csv", index=False, encoding="utf-8-sig")
    pd.concat([r["ta"] for r in res]).to_csv(OUT / f"{STEM}_ta_timeseries.csv", index=False, encoding="utf-8-sig")
    qc = pd.DataFrame([r["qc"] for r in res]); qc.to_csv(OUT / f"{STEM}_subject_qc.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(skipped, columns=["subject", "reason"]).to_csv(OUT / f"{STEM}_skipped.csv", index=False, encoding="utf-8-sig")
    np.savez_compressed(OUT / f"{STEM}_psd_full.npz", freqs=res[0]["f"], subjects=np.array([r["sub"] for r in res]),
                        channels=np.array(res[0]["labels"]), psd=np.stack([r["pfull"] for r in res]))
    desc, metrics = describe_by_group(qc)
    dstem = "02_descriptive_by_group_v2_2026-10-01"
    desc.to_csv(OUT / f"{dstem}.csv", index=False, encoding="utf-8-sig")
    lines = ["# Grup bazında betimsel QC tablosu (grup farkı testi YOK)", "",
             f"Kaynak: `{STEM}_subject_qc.csv`. Tam kesit (465 s), birincil FOOOF (fixed, 3-30 Hz).",
             f"İşlenen denek: {len(qc)} ({', '.join(f'{g} {(qc.group == g).sum()}' for g in ['sg', 'sg2', 'cg'])}); "
             f"atlanan: {len(skipped)}.", "",
             "| Metrik | Grup | n | Ortalama (SD) | Medyan [Q1–Q3] | Min–Maks |", "|---|---|---|---|---|---|"]
    for _, r in desc.iterrows():
        lines.append(f"| {r.description} | {r.group} | {r.n} | {r['mean']:.3f} ({r.sd:.3f}) | "
                     f"{r['median']:.3f} [{r.q1:.3f}–{r.q3:.3f}] | {r['min']:.3f}–{r['max']:.3f} |")
    (OUT / f"{dstem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("yazıldı:", STEM, "+", dstem)


if __name__ == "__main__":
    main()
