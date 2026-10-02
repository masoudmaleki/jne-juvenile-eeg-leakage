"""04-A - Excel öznitelik bütünlük denetimi (salt okuma; sınıflandırma yok).

Okur:  v1.0.0/code/FR_Dats_band_*_EP_*_can_*.xlsx (2048), v1.0.0/code/CAR_FREC_DATS.mat,
       v1.0.0/participants.tsv, v1.0.0/sub-*/eeg/*_acq-epochs_eeg.set (yalnız kimlik doğrulaması)
Yazar: analysis/04a_excel_audit_v1_2026-10-01_{structure,columns,n_points,mat_vs_excel,ids,id_match}.csv
Denetimler:
  1 Yapı: dosya sayısı/şekli, sütunlar, denek sırası ve Label tutarlılığı, yinelenen satırlar
  2 Sütun kalitesi: NaN, sabit / neredeyse sabit sütunlar
  3 Kurtosis = 1,5: istatistikler kaç değer üzerinden? (n=3 testi: |çarpıklık| <= 1/sqrt(2); 3 değerin geri kurulması)
  4 CAR_FREC_DATS.mat ile Excel birebir aynı mı?
  5 Denek kimlikleri: participants.tsv eşleşmesi
  6 Kimlik doğrulaması (yalnız doğrulama, öznitelik değil): Excel log-Power profili vs acq-epochs'tan
    hesaplanan log bant gücü profili; denekler arası z-skor sonrası Pearson korelasyonu, en iyi eşleşme
"""
from pathlib import Path
import re, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.io import loadmat
from scipy.signal import welch

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]; DS = ROOT / "v1.0.0"; CODE = DS / "code"; OUT = ROOT / "analysis"
STEM = "04a_excel_audit_v1_2026-10-01"
NONFEAT = ["Subject", "Label"]
STATS = ["Power", "RMS", "Standarddesv", "Minimun", "Maximun", "Symetry", "Kurtosis"]
BANDS = {"DELTA": (1, 4), "THETA": (4, 8), "ALFA": (8, 13), "BETA": (13, 30)}
COND_EPOCH = {"C_1": 0, "O_1": 1, "C_2": 2, "O_2": 3}   # acq-epochs event sırası C,O,C,O
PAT = re.compile(r"FR_Dats_band_(?P<band>[A-Z]+)_EP_(?P<cond>[CO]_\d)_can_(?P<ch>[A-D]\d+)\.xlsx$")


def read_one(p):
    m = PAT.search(p.name)
    if p.stat().st_size == 0:          # yayımlanan zip'te de 0 bayt olan dosya(lar)
        return m["band"], m["cond"], m["ch"], None
    d = pd.read_excel(p, engine="openpyxl")
    return m["band"], m["cond"], m["ch"], d


def feature_columns(df):
    cols = [c for c in df.columns if c not in NONFEAT]
    assert "Label" not in cols and "Subject" not in cols, "Label/Subject öznitelik setine girmemeli"
    return cols


def main():
    files = sorted(CODE.glob("FR_Dats_band_*.xlsx"))
    print("excel dosyası:", len(files), flush=True)
    res_all = Parallel(n_jobs=15)(delayed(read_one)(p) for p in files)
    empty = [(b, c, h) for b, c, h, d in res_all if d is None]
    print("boş (0 bayt) dosya:", empty)
    res = [r for r in res_all if r[3] is not None]

    # ---- 1 Yapı ----
    ref = res[0][3]
    srows = [dict(band=b, cond=c, channel=h, n_rows=0, empty_file=True) for b, c, h in empty]
    for band, cond, ch, d in res:
        srows.append(dict(band=band, cond=cond, channel=ch, n_rows=len(d), empty_file=False, n_cols=d.shape[1],
                          columns_ok=list(d.columns) == list(ref.columns),
                          subject_order_same=d.Subject.tolist() == ref.Subject.tolist(),
                          label_same=d.Label.tolist() == ref.Label.tolist(),
                          dup_subjects=int(d.Subject.duplicated().sum()),
                          dup_feature_rows=int(d[feature_columns(d)].duplicated().sum())))
    struct = pd.DataFrame(srows); struct.to_csv(OUT / f"{STEM}_structure.csv", index=False, encoding="utf-8-sig")
    grp = ref.Subject.str.extract(r"^(sg2|sg|cg)_rs_\d+$")[0]
    label_vs_prefix = pd.crosstab(grp, ref.Label)
    ne = struct[~struct.empty_file]
    print("kombinasyon x kanal:", struct.groupby(["band", "cond"]).size().unique(), "| satır:", ne.n_rows.unique(),
          "| sütun:", list(ref.columns))
    print("tüm dosyalarda aynı sütun/sıra/label:", ne.columns_ok.all(), ne.subject_order_same.all(), ne.label_same.all(),
          "| yinelenen denek:", struct.dup_subjects.sum(), "| yinelenen öznitelik satırı:", struct.dup_feature_rows.sum())
    print("Label x önek:\n", label_vs_prefix)

    # Uzun tablo
    long = pd.concat([d.assign(band=b, cond=c, channel=h) for b, c, h, d in res], ignore_index=True)
    feats = feature_columns(ref)
    assert set(feats) == set(STATS), feats

    # ---- 2 Sütun kalitesi (her dosya x istatistik = 14.336 sütun) ----
    g = long.groupby(["band", "cond", "channel"])
    col = pd.concat({s: pd.DataFrame(dict(n_nan=g[s].apply(lambda v: v.isna().sum()), mean=g[s].mean(), sd=g[s].std(),
                                          min=g[s].min(), max=g[s].max())) for s in STATS}, names=["stat"]).reset_index()
    col["rel_sd"] = col.sd / col["mean"].abs().replace(0, np.nan)
    col["constant"] = col.sd == 0
    col["near_constant"] = col.rel_sd < 1e-6
    col.to_csv(OUT / f"{STEM}_columns.csv", index=False, encoding="utf-8-sig")
    print("\n14.336 sütun:", len(col), "| NaN içeren:", int((col.n_nan > 0).sum()),
          "| tam sabit:", int(col.constant.sum()), "| neredeyse sabit (rel SD<1e-6):", int(col.near_constant.sum()))
    print(col.groupby("stat")[["constant", "near_constant"]].sum())
    print("Kurtosis bant bazında min/max:", long.groupby("band").Kurtosis.agg(["min", "max"]).to_dict("index"))

    # ---- 3 Kaç değer? ----
    S = long
    bound = 1 / np.sqrt(2)
    rows = []
    for ddof, name in [(0, "SD populasyon"), (1, "SD örneklem (n-1)")]:
        var_pop = S.Standarddesv ** 2 * ((3 - ddof) / 3)          # n=3 varsayımı altında popülasyon varyansı
        mean = np.sqrt(np.clip(S.RMS ** 2 - var_pop, 0, None))      # değerler pozitif (Min > 0) -> ortalama pozitif
        mid = 3 * mean - S.Minimun - S.Maximun
        trip = np.c_[S.Minimun, mid, S.Maximun]
        dev = trip - trip.mean(1, keepdims=True)
        m2 = (dev ** 2).mean(1); m3 = (dev ** 3).mean(1)
        skew_rec = m3 / m2 ** 1.5
        rows.append(dict(sd_convention=name,
                         mid_within_min_max=float(((mid >= S.Minimun - 1e-4) & (mid <= S.Maximun + 1e-4)).mean()),
                         skew_abs_err_median=float(np.nanmedian(np.abs(skew_rec - S.Symetry))),
                         skew_abs_err_p99=float(np.nanpercentile(np.abs(skew_rec - S.Symetry), 99)),
                         sd_rec_rel_err_median=float(np.nanmedian(np.abs(np.sqrt(m2 * 3 / (3 - ddof)) - S.Standarddesv) / S.Standarddesv))))
    npts = pd.DataFrame(rows)
    npts["frac_abs_skew_le_1_over_sqrt2"] = float((S.Symetry.abs() <= bound + 1e-6).mean())
    npts["max_abs_skew"] = float(S.Symetry.abs().max())
    npts["kurtosis_min"], npts["kurtosis_max"] = float(S.Kurtosis.min()), float(S.Kurtosis.max())
    npts["min_value_overall"] = float(S.Minimun.min())
    pw = S.Power / S.RMS ** 2
    npts["power_over_rms2_median"], npts["power_over_rms2_iqr"] = float(pw.median()), float(pw.quantile(.75) - pw.quantile(.25))
    npts["corr_log_power_log_rms"] = float(np.corrcoef(np.log(S.Power), np.log(S.RMS))[0, 1])
    npts.to_csv(OUT / f"{STEM}_n_points.csv", index=False, encoding="utf-8-sig")
    print("\nn=3 testi:\n", npts.T)

    # ---- 4 .mat vs Excel ----
    M = loadmat(CODE / "CAR_FREC_DATS.mat", squeeze_me=True, struct_as_record=False, simplify_cells=True)["Datos"]
    mrows = []
    for b, c, h, d in res:
        md = pd.DataFrame(M[b][c][h])
        same_subj = md.Subject.tolist() == d.Subject.tolist()
        diff = np.abs(md[STATS].values.astype(float) - d[STATS].values.astype(float))
        rel = diff / np.maximum(np.abs(d[STATS].values.astype(float)), 1e-12)
        mrows.append(dict(band=b, cond=c, channel=h, n_mat=len(md), same_subjects=same_subj,
                          label_same=md.Label.tolist() == d.Label.tolist(), max_abs_diff=diff.max(), max_rel_diff=rel.max()))
    for b, c, h in empty:
        md = pd.DataFrame(M[b][c][h])
        mrows.append(dict(band=b, cond=c, channel=h, n_mat=len(md), same_subjects=md.Subject.tolist() == ref.Subject.tolist(),
                          label_same=md.Label.tolist() == ref.Label.tolist(), max_abs_diff=np.nan, max_rel_diff=np.nan,
                          note="Excel 0 bayt; .mat'ta mevcut"))
    mv = pd.DataFrame(mrows); mv.to_csv(OUT / f"{STEM}_mat_vs_excel.csv", index=False, encoding="utf-8-sig")
    print("\n.mat: bantlar", list(M), "| eşleşen dosya:", len(mv), "| aynı denek/label:", mv.same_subjects.all(), mv.label_same.all(),
          "| max mutlak fark:", mv.max_abs_diff.max(), "| max göreli fark:", mv.max_rel_diff.max())

    # ---- 5 Kimlikler ----
    part = pd.read_csv(DS / "participants.tsv", sep="\t")
    ex = ref.Subject.str.extract(r"^(?P<g>sg2|sg|cg)_rs_(?P<n>\d+)$")
    ex_ids = ("sub-" + ex.n + ex.g).tolist()
    ds_ids = sorted(p.name for p in DS.glob("sub-*") if p.is_dir())
    ids = pd.DataFrame(dict(excel_subject=ref.Subject, bids_id=ex_ids, label=ref.Label,
                            in_participants=[i in set(part.participant_id) for i in ex_ids],
                            in_dataset_dirs=[i in set(ds_ids) for i in ex_ids]))
    not_in_excel = [i for i in ds_ids if i not in set(ex_ids)]
    print("\nExcel denekleri:", ids.label.value_counts().to_dict(), "| participants.tsv'de olmayan:", int((~ids.in_participants).sum()),
          ids.loc[~ids.in_participants, "bids_id"].tolist())
    print("Veri setinde olup Excel'de olmayan:", len(not_in_excel), pd.Series(not_in_excel).str.extract(r"(sg2|sg|cg)$")[0].value_counts().to_dict())
    print("  cg/sg olanlar:", [i for i in not_in_excel if not i.endswith("sg2")])

    # ---- 6 Kimlik doğrulaması ----
    def ds_profile(sub):
        p = DS / sub / "eeg" / f"{sub}_task-restingstate_acq-epochs_eeg.set"
        E = loadmat(p, squeeze_me=True, struct_as_record=False, simplify_cells=True)
        x = np.asarray(E["data"], dtype=np.float64)
        if x.ndim == 2: x = x[:, :, None]
        labels = [c["labels"] for c in E["chanlocs"]]
        f, P = welch(x, fs=float(E["srate"]), nperseg=512, noverlap=256, axis=1)   # (ch, freq, epoch)
        out = {}
        for b, (lo, hi) in BANDS.items():
            bp = P[:, (f >= lo) & (f < hi), :].sum(1)
            for c, e in COND_EPOCH.items():
                if e < bp.shape[1]:
                    for i, h in enumerate(labels): out[(b, c, h)] = np.log10(bp[i, e])
        return sub, out
    prof = dict(Parallel(n_jobs=15)(delayed(ds_profile)(s) for s in ds_ids))
    keys = sorted({k for v in prof.values() for k in v})
    Y = pd.DataFrame({s: pd.Series(prof[s]) for s in ds_ids}).T.reindex(columns=keys)       # veri seti denekleri x öznitelik
    Xe = long.assign(lp=np.log10(long.Power)).pivot_table(index="Subject", columns=["band", "cond", "channel"], values="lp")
    Xe = Xe.reindex(columns=pd.MultiIndex.from_tuples(keys)).loc[ref.Subject]
    Xz = (Xe - Xe.mean()) / Xe.std(); Yz = (Y - Y.mean()) / Y.std()
    C = np.full((len(Xz), len(Yz)), np.nan)
    for i in range(len(Xz)):
        a = Xz.values[i]
        for j in range(len(Yz)):
            b = Yz.values[j]; m = np.isfinite(a) & np.isfinite(b)
            if m.sum() > 100: C[i, j] = np.corrcoef(a[m], b[m])[0, 1]
    Cdf = pd.DataFrame(C, index=ref.Subject, columns=Yz.index)
    mrows = []
    for i, (es, bid) in enumerate(zip(ref.Subject, ex_ids)):
        r = Cdf.loc[es].sort_values(ascending=False)
        self_r = Cdf.loc[es, bid] if bid in Cdf.columns else np.nan
        mrows.append(dict(excel_subject=es, bids_id=bid, in_participants=bid in set(part.participant_id),
                          r_same_id=self_r, best_match=r.index[0], r_best=r.iloc[0], second_match=r.index[1], r_second=r.iloc[1],
                          best_is_same_id=r.index[0] == bid, n_features_best=int((np.isfinite(Xz.loc[es].values) & np.isfinite(Yz.loc[r.index[0]].values)).sum())))
    mm = pd.DataFrame(mrows)
    mm.to_csv(OUT / f"{STEM}_id_match.csv", index=False, encoding="utf-8-sig")
    ids.to_csv(OUT / f"{STEM}_ids.csv", index=False, encoding="utf-8-sig")
    ok = mm[mm.in_participants]
    print("\nKimlik doğrulaması — ID'si tutan", len(ok), "denek: en iyi eşleşme kendisi:", int(ok.best_is_same_id.sum()),
          "| r_same median", round(ok.r_same_id.median(), 3), "| r_second median", round(ok.r_second.median(), 3))
    print(mm[~mm.in_participants | ~mm.best_is_same_id][["excel_subject", "bids_id", "in_participants", "r_same_id", "best_match", "r_best", "second_match", "r_second"]].round(3).to_string())
    print("yazıldı:", STEM)


if __name__ == "__main__":
    main()
