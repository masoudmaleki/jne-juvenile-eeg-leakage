"""05 - Alfa reaktivitesi: TEK birincil hipotez testi (plan: 04_05_PLAN_v2_2026-10-01.md; CLAUDE.md).

ARI = (C − O) / (C + O); C = (C1 + C2)/2, O = (O1 + O2)/2; C/O = posterior ROI mutlak alfa (8–13 Hz) gücü.
Veri: yayımlanan acq-epochs (her epok işaret + 5 s'den 50 s). Welch 4 s Hann, %50.
Posterior ROI: A15 A23 A28 A10 B7 A21 A17 A30 A19; dışlanan kanallar 02 v3 kuralından (atipik 2 denekte yalnız EMG kuralı);
02'de olmayan sub-1084sg2 için 9 kanalın hepsi.
Birincil: suçlu (sg+sg2) vs cg, Mann-Whitney U iki yönlü, α = 0,05; n = 136 (4 epoğu olan herkes).
Etki: rank-biserial r (suçlu > cg pozitif), Hodges–Lehmann kayması (suçlu − cg); tabakalı bootstrap %95 GA (2000).
Kovaryat duyarlılığı: OLS ARI ~ grup + yaş + EMG (HC3) ve aynı model rank(ARI) ile.
  EMG = 30–40 Hz log-log eğimi (4 epoğun ortalama PSD'si), posterior kullanılan kanalların medyanı.
Betimsel: sg / sg2 / cg medyanları (test yok). Duyarlılık n = 140: kısa kayıtlı 4 sg yalnız C1/O1 ile.
Okur:  v1.0.0/sub-*/eeg/*_acq-epochs_eeg.set, v1.0.0/participants.tsv,
       analysis/02_features_v2_2026-10-01_channels.csv (dışlama bayrakları), analysis/02_features_v3_2026-10-01_roi.csv (atipik bayrağı)
Yazar: analysis/05_alpha_reactivity_v1_2026-10-02_{subjects,results,descriptive}.csv
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.io import loadmat
from scipy.signal import welch
from scipy.stats import mannwhitneyu, rankdata
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]; DS = ROOT / "v1.0.0"; OUT = ROOT / "analysis"
STEM = "05_alpha_reactivity_v1_2026-10-02"
SEED = 20261001
POST = ["A15", "A23", "A28", "A10", "B7", "A21", "A17", "A30", "A19"]
ALPHA, EMG = (8, 13), (30, 40)
N_BOOT = 2000


def kept_channels():
    ch = pd.read_csv(OUT / "02_features_v2_2026-10-01_channels.csv",
                     usecols=["subject", "segment", "model", "channel", "excluded", "excl_emg"])
    ch = ch[(ch.segment == "full") & (ch.model == "primary") & ch.channel.isin(POST)]
    atyp = set(pd.read_csv(OUT / "02_features_v3_2026-10-01_roi.csv", usecols=["subject", "atypical_spectrum"])
               .query("atypical_spectrum").subject)
    ch["drop"] = np.where(ch.subject.isin(atyp), ch.excl_emg, ch.excluded)
    return {s: g.loc[~g["drop"], "channel"].tolist() for s, g in ch.groupby("subject")}, atyp


def subject_ari(sub, chans):
    E = loadmat(DS / sub / "eeg" / f"{sub}_task-restingstate_acq-epochs_eeg.set", squeeze_me=True,
                struct_as_record=False, simplify_cells=True)
    x = np.asarray(E["data"], dtype=np.float64)
    if x.ndim == 2: x = x[:, :, None]
    labels = [c["labels"] for c in E["chanlocs"]]
    evs = E["event"] if isinstance(E["event"], (list, np.ndarray)) else [E["event"]]
    types = [str(e["type"]) for e in evs if str(e["type"]) in ("PostClosed", "PostOpen")]
    assert len(types) == x.shape[2], (sub, types, x.shape)
    idx = [labels.index(c) for c in chans]
    f, P = welch(x[idx], fs=float(E["srate"]), window="hann", nperseg=512, noverlap=256, axis=1)   # (ch, freq, ep)
    df = f[1] - f[0]
    alpha = P[:, (f >= ALPHA[0]) & (f < ALPHA[1]), :].sum(1).mean(0) * df          # ROI ortalaması, epok başına
    C = np.mean([a for a, t in zip(alpha, types) if t == "PostClosed"])
    O = np.mean([a for a, t in zip(alpha, types) if t == "PostOpen"])
    m = (f >= EMG[0]) & (f <= EMG[1]); lx = np.log10(f[m]); lxc = lx - lx.mean()
    ly = np.log10(P.mean(2)[:, m]); slope = (ly - ly.mean(1, keepdims=True)) @ lxc / (lxc @ lxc)
    return dict(subject=sub, n_epochs=x.shape[2], epoch_types="".join(t[4] for t in types), n_post_ch=len(idx),
                alpha_C=C, alpha_O=O, ARI=(C - O) / (C + O), emg_slope=float(np.median(slope)))


def rank_biserial(a, b):
    U = mannwhitneyu(a, b, alternative="two-sided").statistic          # a'nın b'den büyük olduğu çiftler (+ yarım bağlar)
    return 2 * U / (len(a) * len(b)) - 1


def hodges_lehmann(a, b):
    return float(np.median(np.subtract.outer(a, b)))


def primary_test(d, label):
    a = d.loc[d.offender == 1, "ARI"].values; b = d.loc[d.offender == 0, "ARI"].values
    mw = mannwhitneyu(a, b, alternative="two-sided")
    rb, hl = rank_biserial(a, b), hodges_lehmann(a, b)
    rng = np.random.default_rng(SEED); bs_rb, bs_hl = [], []
    for _ in range(N_BOOT):
        aa, bb = rng.choice(a, len(a)), rng.choice(b, len(b))
        bs_rb.append(rank_biserial(aa, bb)); bs_hl.append(hodges_lehmann(aa, bb))
    return dict(analysis=label, n_offender=len(a), n_cg=len(b), median_offender=np.median(a), median_cg=np.median(b),
                U=mw.statistic, p=mw.pvalue, rank_biserial=rb, rb_ci_low=np.percentile(bs_rb, 2.5), rb_ci_high=np.percentile(bs_rb, 97.5),
                HL_shift=hl, HL_ci_low=np.percentile(bs_hl, 2.5), HL_ci_high=np.percentile(bs_hl, 97.5))


def main():
    kept, atyp = kept_channels()
    part = pd.read_csv(DS / "participants.tsv", sep="\t").set_index("participant_id")
    subs = sorted(p.name for p in DS.glob("sub-*") if p.is_dir())
    jobs = [(s, kept.get(s, POST)) for s in subs]
    rows = Parallel(n_jobs=15)(delayed(subject_ari)(s, c) for s, c in jobs)
    d = pd.DataFrame(rows)
    d["group"] = d.subject.str.extract(r"(sg2|sg|cg)$")[0]
    d["offender"] = (d.group != "cg").astype(int)
    d["age"] = part.loc[d.subject, "Age"].values.astype(float)
    d["channel_set"] = np.where(~d.subject.isin(kept), "all9 (02'de yok)", np.where(d.subject.isin(atyp), "02 v3 EMG-only", "02 v3"))
    d.to_csv(OUT / f"{STEM}_subjects.csv", index=False, encoding="utf-8-sig")

    prim = d[d.n_epochs == 4].copy()
    assert len(prim) == 136, len(prim)
    res = [primary_test(prim, "PRIMARY n=136 (Mann-Whitney)"), primary_test(d, "sensitivity n=140 (short 4 sg: C1/O1)")]
    cov = []
    for lab, formula, dd in [("OLS ARI ~ offender + age + EMG (HC3)", "ARI ~ offender + age + emg_slope", prim),
                             ("OLS rank(ARI) ~ offender + age + EMG (HC3)", "rARI ~ offender + age + emg_slope", prim.assign(rARI=rankdata(prim.ARI)))]:
        fit = smf.ols(formula, data=dd).fit(cov_type="HC3")
        ci = fit.conf_int().loc["offender"]
        cov.append(dict(analysis=lab, n=int(fit.nobs), coef_offender=fit.params["offender"], ci_low=ci[0], ci_high=ci[1],
                        p=fit.pvalues["offender"], coef_age=fit.params["age"], p_age=fit.pvalues["age"],
                        coef_emg=fit.params["emg_slope"], p_emg=fit.pvalues["emg_slope"]))
    out = pd.concat([pd.DataFrame(res), pd.DataFrame(cov)], ignore_index=True)
    out.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    desc = prim.groupby("group")[["ARI", "alpha_C", "alpha_O", "emg_slope", "age"]].describe(percentiles=[.25, .5, .75])
    desc.to_csv(OUT / f"{STEM}_descriptive.csv", encoding="utf-8-sig")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(out.round(4).to_string())
    print(prim.groupby("group").ARI.describe().round(3))
    print("yazıldı:", STEM)


if __name__ == "__main__":
    main()
