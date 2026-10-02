"""02 - ROI dosyası v3: denek düzeyi QC kuralı (CLAUDE.md, 2026-10-01).

Kural: v2'de kanalların > %25'i dışlanan denek -> atypical_spectrum = True. Bu deneklerde yalnız EMG kuralı
(robust z > 3) uygulanır, R² kuralı uygulanmaz; ROI kalan tüm kanallarla yeniden hesaplanır.
Diğer deneklerin ROI satırları v2'den değiştirilmeden kopyalanır (betik bunu doğrular).
Okur:  analysis/02_features_v2_2026-10-01_roi.csv, _subject_qc.csv; bayraklı denekler için v1.0.0 .set
Yazar: analysis/02_features_v3_2026-10-01_roi.csv  (yalnız bu dosya; channels/ta/qc v2'de kalır)
"""
from pathlib import Path
import importlib.util
import numpy as np, pandas as pd

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v2", OUT / "02_features_v2_2026-10-01.py")
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
ATYP_FRAC = 0.25


def roi_rows_emg_only(sub, grp):
    x, sr, labels, meta = v2.load_block(sub)
    h = x.shape[1] // 2
    spectra = {k: v2.psd(v, sr) for k, v in {"full": x, "H1": x[:, :h], "H2": x[:, h:]}.items()}
    f, pfull = spectra["full"]
    keep = ~(v2.robust_z(v2.emg_feats(f, pfull)["emg_slope_30_40"]) > v2.EMG_Z_MAX)
    rows = []
    for seg, (fs, ps) in spectra.items():
        for roi, chs in v2.ROIS.items():
            idx = np.arange(len(labels)) if chs is None else np.array([labels.index(c) for c in chs])
            idx_keep = idx[keep[idx]]
            p = ps[idx_keep].mean(0)
            b = {k: float(v) for k, v in v2.band_feats(fs, p).items()}
            e = {k: float(v) for k, v in v2.emg_feats(fs, p).items()}
            for model in v2.MODELS:
                rows.append(dict(subject=sub, group=grp, segment=seg, model=model, roi=roi,
                                 n_ch_roi=len(idx), n_ch_used=len(idx_keep), **b, **e, **v2.fit(fs, p, model)))
    return pd.DataFrame(rows), int((~keep).sum())


def main():
    roi = pd.read_csv(OUT / "02_features_v2_2026-10-01_roi.csv")
    qc = pd.read_csv(OUT / "02_features_v2_2026-10-01_subject_qc.csv")
    n_ch = 128
    flagged = qc.loc[qc.n_excluded > ATYP_FRAC * n_ch, ["subject", "group", "n_excluded"]]
    print("atipik spektrum bayrağı:", flagged.to_dict("records"))
    new_parts, info = [], {}
    for _, r in flagged.iterrows():
        df, n_ex = roi_rows_emg_only(r.subject, r.group)
        new_parts.append(df); info[r.subject] = n_ex
        print(f"  {r.subject}: v2 dışlanan {r.n_excluded} -> v3 (yalnız EMG) {n_ex}")
    keep_old = roi[~roi.subject.isin(flagged.subject)]
    out = pd.concat([keep_old] + new_parts, ignore_index=True)
    out["atypical_spectrum"] = out.subject.isin(flagged.subject)
    out["channel_rule"] = np.where(out.atypical_spectrum, "emg_only", "r2_or_emg")
    out = out.sort_values(["subject", "segment", "model", "roi"], kind="stable")[list(roi.columns) + ["atypical_spectrum", "channel_rule"]]
    # Doğrulama: bayraksız deneklerin satırları v2 ile birebir aynı
    a = roi[~roi.subject.isin(flagged.subject)].sort_values(["subject", "segment", "model", "roi"]).reset_index(drop=True)
    b = out[~out.atypical_spectrum].drop(columns=["atypical_spectrum", "channel_rule"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)
    assert len(out) == len(roi), (len(out), len(roi))
    fn = OUT / "02_features_v3_2026-10-01_roi.csv"
    out.to_csv(fn, index=False, encoding="utf-8-sig")
    print("doğrulama geçti: bayraksız satırlar v2 ile aynı; satır sayısı", len(out)); print("yazıldı:", fn)


if __name__ == "__main__":
    main()
