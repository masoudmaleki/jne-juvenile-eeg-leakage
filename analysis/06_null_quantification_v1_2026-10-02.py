"""06 - Null sonucun nicelenmesi (plan: 04_05_PLAN_v2_2026-10-01.md, 06; CLAUDE.md).

Suçlu (sg+sg2, 69) vs cg (66), 135 denek; 03 ile aynı 14 öznitelik ve pipeline
(medyan imputasyon -> StandardScaler -> L2 LR balanced; dış stratified 5-fold x 20 tekrar, iç 5-fold, C ∈ logspace(-3,3,13)).
GA: deneğin dış-kat olasılığı 20 tekrarın ortalaması -> sınıf içi tabakalı denek bootstrap'ı (2000, percentile); çapraz kontrol DeLong.
Sınırlılık: bu GA model eğitimi oynaklığını içermez; tekrarlar arası 2,5–97,5 ayrıca raporlanır.
"Dışlanabilen en küçük etki": GA üst sınırı U -> "AUC > U %95 güvenle dışlanır"; eşdeğer Cohen d = sqrt(2) * Φ^-1(U).
Okur:  analysis/02_features_v3_2026-10-01_roi.csv (+ 03'ün load() girdileri)
Yazar: analysis/06_null_quantification_v1_2026-10-02_{oof,results}.csv
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import importlib, sys, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.stats import norm
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, balanced_accuracy_score

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
os.environ["PYTHONPATH"] = str(OUT) + os.pathsep + os.environ.get("PYTHONPATH", "")
M3 = importlib.import_module("03_batch_negcontrol_v1_2026-10-01")   # build(), make_search(), sabitler (03 ile aynı)
STEM = "06_null_quantification_v1_2026-10-02"
N_BOOT = 2000


def one_rep(X, y, r):
    warnings.filterwarnings("ignore")
    oof = np.zeros(len(y))
    for f, (tr, te) in enumerate(StratifiedKFold(M3.K_OUT, shuffle=True, random_state=M3.SEED + r).split(X, y)):
        gs = M3.make_search(0, M3.SEED + 1000 * r + f).fit(X[tr], y[tr])
        oof[te] = gs.predict_proba(X[te])[:, 1]
    return oof


def delong_ci(y, s, alpha=0.05):
    pos, neg = s[y == 1], s[y == 0]
    m, n = len(pos), len(neg)
    psi = (pos[:, None] > neg[None, :]).astype(float) + 0.5 * (pos[:, None] == neg[None, :])
    auc = psi.mean(); v10 = psi.mean(1); v01 = psi.mean(0)
    se = np.sqrt(v10.var(ddof=1) / m + v01.var(ddof=1) / n)
    z = norm.ppf(1 - alpha / 2)
    return auc, auc - z * se, auc + z * se, se


def main():
    roi, qc, part, rec = M3.load()
    w = M3.build(roi)                                               # 135 x 14, full / primary
    g = M3.groups(w.index)
    y = (g != "cg").astype(int).values; X = w.values.astype(float)
    assert len(y) == 135 and y.sum() == 69, (len(y), y.sum())
    oofs = np.array(Parallel(n_jobs=15)(delayed(one_rep)(X, y, r) for r in range(M3.REPS)))   # (20, 135)
    rep_auc = np.array([roc_auc_score(y, o) for o in oofs]); rep_ba = np.array([balanced_accuracy_score(y, o >= 0.5) for o in oofs])
    s = oofs.mean(0)
    pd.DataFrame(dict(subject=w.index, group=g.values, offender=y, p_mean=s, p_sd=oofs.std(0))).to_csv(
        OUT / f"{STEM}_oof.csv", index=False, encoding="utf-8-sig")
    auc_mean_prob = roc_auc_score(y, s)
    rng = np.random.default_rng(M3.SEED); ip, ineg = np.where(y == 1)[0], np.where(y == 0)[0]
    boot = np.array([roc_auc_score(np.r_[np.ones(len(ip)), np.zeros(len(ineg))],
                                   np.r_[s[rng.choice(ip, len(ip))], s[rng.choice(ineg, len(ineg))]]) for _ in range(N_BOOT)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    d_auc, d_lo, d_hi, d_se = delong_ci(y, s)
    d_eq = lambda a: float(np.sqrt(2) * norm.ppf(a))
    res = pd.DataFrame([dict(
        n_offender=int(y.sum()), n_cg=int((y == 0).sum()), n_reps=len(rep_auc),
        auc_rep_mean=rep_auc.mean(), auc_rep_p2_5=np.percentile(rep_auc, 2.5), auc_rep_p97_5=np.percentile(rep_auc, 97.5),
        ba_rep_mean=rep_ba.mean(), auc_mean_prob=auc_mean_prob,
        boot_ci_low=lo, boot_ci_high=hi, delong_ci_low=d_lo, delong_ci_high=d_hi, delong_se=d_se,
        U_excluded_boot=hi, cohen_d_at_U_boot=d_eq(hi), U_excluded_delong=d_hi, cohen_d_at_U_delong=d_eq(d_hi),
        lower_bound_boot=lo, cohen_d_at_lower_boot=d_eq(lo))])
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 200); print(res.round(4).T); print("yazıldı:", STEM)


if __name__ == "__main__":
    main()
