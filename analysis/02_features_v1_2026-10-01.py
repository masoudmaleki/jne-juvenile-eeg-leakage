"""02 - Uzun göz kapalı bloktan öznitelik çıkarma (salt okuma, sınıflandırma yok).

Kaynak: v1.0.0/sub-*/eeg/*_desc-preprocessed_eeg.set (128 Hz, 128 EEG, ortalama referans).
Blok: 3. göz kapalı işaretinden (kod 64) BLOCK_SKIP_S sonra başlayan sabit BLOCK_LEN_S saniye.
      Sabit uzunluk: cg'de uzun blok 500-510 s, suçlularda ~481 s; süre farkı özniteliğe sızmasın.
Öznitelikler (kanal başına + ROI ortalama spektrumu):
  - Welch PSD (4 s Hann, %50 örtüşme, 0,25 Hz çözünürlük)
  - Göreli bant güçleri (bant / 1-40 Hz toplam) + log10 mutlak toplam güç (yalnız bilgi için)
  - FOOOF (fooof 1.x = specparam'ın önceki adı) 2-40 Hz, aperiodik 'fixed': offset, üs, R², hata
  - Alfa tepe frekansı (IAF): FOOOF'un 7-14 Hz'deki en güçlü tepesi; çapraz kontrol için PSD argmax
Kullanım: python 02_features_v1_2026-10-01.py [--subjects sub-A sub-B ...] [--tag pilot]
"""
from pathlib import Path
import argparse, re, warnings
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.signal import welch
from fooof import FOOOF

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "v1.0.0"
OUT = ROOT / "analysis"
DATE = "2026-10-01"

BLOCK_SKIP_S = 5.0      # göz kapama geçişini at (acq-epochs ile aynı 5 s ofset)
BLOCK_LEN_S = 465.0     # en kısa kullanılabilir blok 474 s (sub-2019cg) - 5 s
WIN_S, OVERLAP = 4.0, 0.5
TOTAL_BAND = (1.0, 40.0)
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30), "gamma": (30, 40)}
FOOOF_RANGE = (2.0, 40.0)
FOOOF_KW = dict(peak_width_limits=(1.0, 8.0), max_n_peaks=6, min_peak_height=0.1, aperiodic_mode="fixed", verbose=False)
ALPHA_SEARCH = (7.0, 14.0)
ROIS = {  # Biosemi 128 ABCD -> 10-20 yaklaşığı (channels.tsv açıklamalarından)
    "posterior": ["A15", "A23", "A28", "A10", "B7", "A21", "A17", "A30", "A19"],   # O1 Oz O2 PO7 PO8 POz PO3 PO4 Pz
    "central":   ["A1", "D19", "B22", "A3", "D14", "B20"],                          # Cz C3 C4 CPz C1 C2
    "frontal":   ["C21", "D4", "C4", "C23", "C25", "C12", "C19"],                   # Fz F3 F4 FCz F1 F2 AFz
    "global":    None,                                                              # 128 kanal ortalaması
}


def load_block(sub):
    p = DS / sub / "eeg" / f"{sub}_task-restingstate_desc-preprocessed_eeg.set"
    E = loadmat(p, squeeze_me=True, struct_as_record=False, simplify_cells=True)
    if isinstance(E["data"], str):
        raise RuntimeError(f"veri harici dosyada: {E['data']}")
    sr = float(E["srate"]); x = np.asarray(E["data"], dtype=np.float64)
    labels = [c["labels"] for c in E["chanlocs"]]
    pos = np.array([[c["radius"] * np.sin(np.deg2rad(c["theta"])), c["radius"] * np.cos(np.deg2rad(c["theta"]))] for c in E["chanlocs"]], dtype=float)
    evs = E["event"] if isinstance(E["event"], (list, np.ndarray)) else [E["event"]]
    co = [(int(e["edftype"]), float(e["latency"])) for e in evs if str(e.get("edftype")) in ("64", "128")]
    closed = [i for i, (c, _) in enumerate(co) if c == 64]
    if len(closed) < 3:
        raise RuntimeError("3. göz kapalı işareti yok")
    j = closed[2]
    blk_start = co[j][1] - 1
    blk_end = co[j + 1][1] - 1 if j + 1 < len(co) else x.shape[1]
    s0 = int(round(blk_start + BLOCK_SKIP_S * sr)); s1 = s0 + int(round(BLOCK_LEN_S * sr))
    if s1 > blk_end:
        raise RuntimeError(f"blok kısa: {(blk_end - blk_start) / sr:.1f} s")
    meta = dict(block_marker_s=round(blk_start / sr, 2), block_avail_s=round((blk_end - blk_start) / sr, 1),
                seg_start_s=round(s0 / sr, 2), seg_end_s=round(s1 / sr, 2))
    return x[:, s0:s1], sr, labels, pos, meta


def band_features(f, pxx):
    df = f[1] - f[0]
    tot_m = (f >= TOTAL_BAND[0]) & (f < TOTAL_BAND[1])
    tot = pxx[..., tot_m].sum(-1) * df
    out = {"log10_total_power": np.log10(tot)}
    for b, (lo, hi) in BANDS.items():
        m = (f >= lo) & (f < hi)
        out[f"rel_{b}"] = pxx[..., m].sum(-1) * df / tot
    return out


def fooof_features(f, p):
    fm = FOOOF(**FOOOF_KW)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fm.fit(f, p, FOOOF_RANGE)
    off, exp = fm.aperiodic_params_
    pk = fm.peak_params_ if fm.peak_params_.size else np.empty((0, 3))
    a = pk[(pk[:, 0] >= ALPHA_SEARCH[0]) & (pk[:, 0] <= ALPHA_SEARCH[1])] if len(pk) else pk
    if len(a):
        cf, pw, bw = a[np.argmax(a[:, 1])]
    else:
        cf = pw = bw = np.nan
    m = (f >= ALPHA_SEARCH[0]) & (f <= ALPHA_SEARCH[1])
    return dict(ap_offset=off, ap_exponent=exp, fooof_r2=fm.r_squared_, fooof_error=fm.error_,
                n_peaks=len(pk), iaf_fooof=cf, alpha_pw=pw, alpha_bw=bw,
                iaf_psd_argmax=f[m][np.argmax(p[m])]), fm


def process(sub):
    grp = re.search(r"(sg2|sg|cg)$", sub).group(1)
    x, sr, labels, pos, meta = load_block(sub)
    nper = int(WIN_S * sr)
    f, pxx = welch(x, fs=sr, window="hann", nperseg=nper, noverlap=int(nper * OVERLAP), detrend="constant", axis=-1)
    n_win = 1 + (x.shape[1] - nper) // (nper - int(nper * OVERLAP))
    rows, fits = [], {}
    units = [(l, pxx[i]) for i, l in enumerate(labels)]
    for roi, chs in ROIS.items():
        idx = list(range(len(labels))) if chs is None else [labels.index(c) for c in chs]
        units.append((f"ROI_{roi}", pxx[idx].mean(0)))
    for name, p in units:
        bf = {k: float(v) for k, v in band_features(f, p).items()}
        ff, fm = fooof_features(f, p)
        rows.append(dict(subject=sub, group=grp, unit=name, n_welch_windows=n_win, **meta, **bf, **ff))
        if name.startswith("ROI_"):
            fits[name] = fm
    return pd.DataFrame(rows), f, pxx, labels, pos, fits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", nargs="*")
    ap.add_argument("--tag", default="all")
    a = ap.parse_args()
    subs = a.subjects or sorted(p.name for p in DS.glob("sub-*") if p.is_dir())
    feats, psds, skipped = [], {}, []
    for i, s in enumerate(subs, 1):
        try:
            df, f, pxx, labels, pos, fits = process(s)
            feats.append(df); psds[s] = (f, pxx, labels, pos, fits)
            print(f"[{i}/{len(subs)}] {s} ok", flush=True)
        except Exception as e:  # noqa
            skipped.append(dict(subject=s, reason=str(e))); print(f"[{i}/{len(subs)}] {s} ATLANDI: {e}", flush=True)
    feat = pd.concat(feats, ignore_index=True)
    stem = f"02_features_{a.tag}_v1_{DATE}"
    feat.to_csv(OUT / f"{stem}.csv", index=False, encoding="utf-8-sig")
    if skipped:
        pd.DataFrame(skipped).to_csv(OUT / f"{stem}_skipped.csv", index=False, encoding="utf-8-sig")
    f0 = next(iter(psds.values()))[0]
    np.savez_compressed(OUT / f"{stem}_psd.npz", freqs=f0, subjects=np.array(list(psds)),
                        psd=np.stack([v[1] for v in psds.values()]), channels=np.array(next(iter(psds.values()))[2]))
    print("yazıldı:", OUT / f"{stem}.csv", OUT / f"{stem}_psd.npz")
    return feat, psds, stem


if __name__ == "__main__":
    main()
