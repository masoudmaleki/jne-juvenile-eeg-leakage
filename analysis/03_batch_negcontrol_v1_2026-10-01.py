"""03 - Batch negatif kontrolü (plan: 03_batch_negatif_kontrol_PLAN_v2_2026-10-01.md).

(a) sg vs sg2: iç içe CV (dış 5-fold x 20 tekrar, iç 5-fold C seçimi), ROC-AUC + dengeli doğruluk, 1000 permütasyon.
(b) sg + cg eğitimi; her dış katta aynı model held-out cg vs 24 sg2'yi skorlar; kat-içi transfer AUC'si,
    katlar üzerinden ortalama (skor ortalaması yok); 1000 permütasyon (eğitim etiketleri karıştırılır).
Pipeline: medyan imputasyon -> [kovaryat kalıntılama] -> StandardScaler -> LogisticRegression(L2, balanced).
Okur:  analysis/02_features_v3_2026-10-01_roi.csv, analysis/02_features_v2_2026-10-01_subject_qc.csv,
       analysis/01_data_audit_v2_2026-10-01.csv (kayıt tarihi), v1.0.0/participants.tsv (yaş)
Yazar: analysis/03_batch_negcontrol_v1_2026-10-01_{results,sensitivity,transfer_folds,coefs,heldout_scores}.csv, _perm_null.npz
Kullanım: python 03_batch_negcontrol_v1_2026-10-01.py [--n-perm 1000] [--jobs 15] [--timing]
"""
from pathlib import Path
import argparse, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, balanced_accuracy_score

ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "analysis"
STEM = "03_batch_negcontrol_v1_2026-10-01"
SEED = 20261001
REPS, PERM_REPS, K_OUT, K_IN = 20, 5, 5, 5
CS = np.logspace(-3, 3, 13)
FEATS = ["rel_delta", "rel_theta", "rel_alpha", "rel_beta", "ap_exponent", "ap_offset", "iaf_fooof"]
ROIS = ["posterior", "global"]
ATYPICAL = ["sub-1105sg2", "sub-1114sg2"]


class Residualizer(BaseEstimator, TransformerMixin):
    """Son n_cov sütun kovaryattır; özniteliklerden eğitim verisinde OLS ile kalıntılanır, kovaryatlar düşülür."""
    def __init__(self, n_cov=0):
        self.n_cov = n_cov

    def fit(self, X, y=None):
        if self.n_cov:
            F, C = X[:, :-self.n_cov], X[:, -self.n_cov:]
            A = np.c_[np.ones(len(C)), C]
            self.beta_ = np.linalg.lstsq(A, F, rcond=None)[0]
        return self

    def transform(self, X):
        if not self.n_cov:
            return X
        F, C = X[:, :-self.n_cov], X[:, -self.n_cov:]
        return F - np.c_[np.ones(len(C)), C] @ self.beta_


def make_search(n_cov, rs):
    pipe = Pipeline([("imp", SimpleImputer(strategy="median")), ("res", Residualizer(n_cov)),
                     ("sc", StandardScaler()),
                     ("lr", LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000))])
    return GridSearchCV(pipe, {"lr__C": CS}, scoring="roc_auc", refit=True,
                        cv=StratifiedKFold(K_IN, shuffle=True, random_state=rs), n_jobs=1)


def run_a(X, y, reps, seed, n_cov=0, keep_details=False):
    aucs, bas, coefs = [], [], []
    for r in range(reps):
        oof = np.zeros(len(y))
        for f, (tr, te) in enumerate(StratifiedKFold(K_OUT, shuffle=True, random_state=seed + r).split(X, y)):
            gs = make_search(n_cov, seed + 1000 * r + f).fit(X[tr], y[tr])
            oof[te] = gs.predict_proba(X[te])[:, 1]
            if keep_details:
                coefs.append(gs.best_estimator_["lr"].coef_[0])
        aucs.append(roc_auc_score(y, oof)); bas.append(balanced_accuracy_score(y, oof >= 0.5))
    return np.array(aucs), np.array(bas), coefs


def run_b(Xtr, ytr, is_cg, Xsg2, reps, seed, n_cov=0, keep_details=False):
    """ytr: 1 = sg, 0 = cg (permütasyonda karıştırılmış olabilir); is_cg: gerçek cg kimliği (held-out seçimi için)."""
    fold_rows, sgcg_auc, coefs, heldout = [], [], [], []
    for r in range(reps):
        oof = np.zeros(len(ytr))
        for f, (tr, te) in enumerate(StratifiedKFold(K_OUT, shuffle=True, random_state=seed + r).split(Xtr, ytr)):
            gs = make_search(n_cov, seed + 1000 * r + f).fit(Xtr[tr], ytr[tr])
            oof[te] = gs.predict_proba(Xtr[te])[:, 1]
            cg_te = te[is_cg[te]]
            s_cg = gs.predict_proba(Xtr[cg_te])[:, 1]; s_sg2 = gs.predict_proba(Xsg2)[:, 1]
            auc = roc_auc_score(np.r_[np.zeros(len(s_cg)), np.ones(len(s_sg2))], np.r_[s_cg, s_sg2])
            fold_rows.append(dict(rep=r, fold=f, n_cg_heldout=len(cg_te), transfer_auc=auc,
                                  frac_sg2_offender=float((s_sg2 >= 0.5).mean()), best_C=gs.best_params_["lr__C"]))
            if keep_details:
                coefs.append(gs.best_estimator_["lr"].coef_[0])
                heldout.append((r, f, cg_te, s_cg, s_sg2))
        sgcg_auc.append(roc_auc_score(ytr, oof))
    return pd.DataFrame(fold_rows), np.array(sgcg_auc), coefs, heldout


def load():
    roi = pd.read_csv(OUT / "02_features_v3_2026-10-01_roi.csv")
    qc = pd.read_csv(OUT / "02_features_v2_2026-10-01_subject_qc.csv").set_index("subject")
    part = pd.read_csv(ROOT / "v1.0.0" / "participants.tsv", sep="\t").set_index("participant_id")
    aud = pd.read_csv(OUT / "01_data_audit_v2_2026-10-01.csv")
    rec = pd.to_datetime(aud[aud.file == "preprocessed"].set_index("subject").rec_datetime)
    return roi, qc, part, rec


def build(roi, segment="full", model="primary", drop=()):
    d = roi[(roi.segment == segment) & (roi.model == model) & roi.roi.isin(ROIS)]
    w = d.pivot(index="subject", columns="roi", values=[f for f in FEATS if f not in drop])
    w.columns = [f"{r}_{f}" for f, r in w.columns]
    return w.sort_index()


def design(w, qc, part, subjects, covs):
    X = w.loc[subjects].values.astype(float)
    C = []
    if "emg_ta" in covs:
        C += [qc.loc[subjects, "emg_slope_median_all"].values, qc.loc[subjects, "ta_slope_global"].values]
    if "age" in covs:
        C += [part.loc[subjects, "Age"].values.astype(float)]
    return (np.c_[X, np.column_stack(C)] if C else X), len(C)


def groups(index):
    return pd.Series(index, index=index).str.extract(r"(sg2|sg|cg)$")[0]


def analyse(roi, qc, part, segment="full", model="primary", drop=(), covs=(), exclude=(), reps=REPS, details=False):
    w = build(roi, segment, model, drop)
    w = w[~w.index.isin(exclude)]
    g = groups(w.index)
    sa = list(w.index[g.isin(["sg", "sg2"])]); ya = (g[sa] == "sg2").astype(int).values
    Xa, nc = design(w, qc, part, sa, covs)
    a_auc, a_ba, a_coef = run_a(Xa, ya, reps, SEED, nc, details)
    sb = list(w.index[g.isin(["sg", "cg"])]); yb = (g[sb] == "sg").astype(int).values
    s2 = list(w.index[g == "sg2"])
    Xb, nc = design(w, qc, part, sb, covs); X2, _ = design(w, qc, part, s2, covs)
    fr, sgcg, b_coef, held = run_b(Xb, yb, (yb == 0), X2, reps, SEED, nc, details)
    return dict(w=w, sa=sa, ya=ya, Xa=Xa, sb=sb, yb=yb, Xb=Xb, s2=s2, X2=X2, nc=nc,
                a_auc=a_auc, a_ba=a_ba, a_coef=a_coef, folds=fr, sgcg=sgcg, b_coef=b_coef, held=held)


def perm_a(Xa, ya, nc, i):
    rng = np.random.default_rng(SEED + 7 + i)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return run_a(Xa, rng.permutation(ya), PERM_REPS, SEED + 100000 + 50 * i, nc)[0].mean()


def perm_b(Xb, yb, X2, nc, i):
    rng = np.random.default_rng(SEED + 9 + i)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fr = run_b(Xb, rng.permutation(yb), (yb == 0), X2, PERM_REPS, SEED + 200000 + 50 * i, nc)[0]
    return fr.transfer_auc.mean()


def summ(v):
    return dict(mean=float(np.mean(v)), p2_5=float(np.percentile(v, 2.5)), p97_5=float(np.percentile(v, 97.5)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--jobs", type=int, default=15)
    ap.add_argument("--timing", action="store_true")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    roi, qc, part, rec = load()

    if a.timing:
        m = analyse(roi, qc, part, reps=1)
        t = time.time(); perm_a(m["Xa"], m["ya"], m["nc"], 0); ta = time.time() - t
        t = time.time(); perm_b(m["Xb"], m["yb"], m["X2"], m["nc"], 0); tb = time.time() - t
        print(f"1 permütasyon: (a) {ta:.1f} s, (b) {tb:.1f} s; tahmini toplam {(ta + tb) * a.n_perm / a.jobs / 60:.1f} dk ({a.jobs} iş)")
        return

    t0 = time.time()
    m = analyse(roi, qc, part, details=True)
    print(f"birincil bitti ({time.time() - t0:.0f} s): (a) AUC {m['a_auc'].mean():.3f}; (b) transfer {m['folds'].transfer_auc.mean():.3f}, sg-cg {m['sgcg'].mean():.3f}", flush=True)

    # ---- Duyarlılık (yalnız gerçek değer) ----
    variants = {"1_no_atypical": dict(exclude=ATYPICAL), "2_resid_emg_ta": dict(covs=("emg_ta",)),
                "3_resid_age": dict(covs=("age",)), "4_H1_segment": dict(segment="H1"),
                "5_no_ap_offset": dict(drop=("ap_offset",)), "6_knee_model": dict(model="knee")}
    sens = []
    for name, kw in [("0_primary", {})] + list(variants.items()):
        s = m if name == "0_primary" else analyse(roi, qc, part, **kw)
        sens.append(dict(variant=name, n_sg=int((s["ya"] == 0).sum()), n_sg2=int((s["ya"] == 1).sum()), n_cg=int((s["yb"] == 0).sum()),
                         **{f"a_auc_{k}": v for k, v in summ(s["a_auc"]).items()}, a_ba_mean=float(s["a_ba"].mean()),
                         **{f"b_transfer_auc_{k}": v for k, v in summ(s["folds"].transfer_auc).items()},
                         b_frac_sg2_offender=float(s["folds"].frac_sg2_offender.mean()),
                         **{f"b_sgcg_auc_{k}": v for k, v in summ(s["sgcg"]).items()}))
        print(f"  duyarlılık {name}: (a) {s['a_auc'].mean():.3f}  (b) {s['folds'].transfer_auc.mean():.3f}", flush=True)
    pd.DataFrame(sens).to_csv(OUT / f"{STEM}_sensitivity.csv", index=False, encoding="utf-8-sig")

    # ---- Ayrıntılar: transfer katları, katsayılar, held-out skorlar (betimsel) ----
    m["folds"].to_csv(OUT / f"{STEM}_transfer_folds.csv", index=False, encoding="utf-8-sig")
    cols = list(m["w"].columns)
    crow = []
    for an, cf in [("a_sg_vs_sg2", m["a_coef"]), ("b_sg_vs_cg", m["b_coef"])]:
        c = np.array(cf)
        for j, n in enumerate(cols):
            crow.append(dict(analysis=an, feature=n, coef_mean=c[:, j].mean(), coef_sd=c[:, j].std(),
                             frac_positive=(c[:, j] > 0).mean(), n_folds=len(c)))
    pd.DataFrame(crow).to_csv(OUT / f"{STEM}_coefs.csv", index=False, encoding="utf-8-sig")
    hrow = []
    for r, f, cg_te, s_cg, s_sg2 in m["held"]:
        hrow += [dict(rep=r, fold=f, subject=m["sb"][i], group="cg", p_offender=p) for i, p in zip(cg_te, s_cg)]
        hrow += [dict(rep=r, fold=f, subject=s, group="sg2", p_offender=p) for s, p in zip(m["s2"], s_sg2)]
    h = pd.DataFrame(hrow)
    h["rec_date"] = rec.reindex(h.subject).values
    h["cg_time_overlap_MayJun2022"] = (h.group == "cg") & (pd.to_datetime(h.rec_date) >= "2022-05-01") & (pd.to_datetime(h.rec_date) < "2022-07-01")
    h.to_csv(OUT / f"{STEM}_heldout_scores.csv", index=False, encoding="utf-8-sig")

    # ---- Permütasyonlar ----
    t0 = time.time()
    null_a = np.array(Parallel(n_jobs=a.jobs)(delayed(perm_a)(m["Xa"], m["ya"], m["nc"], i) for i in range(a.n_perm)))
    print(f"permütasyon (a) bitti ({(time.time() - t0) / 60:.1f} dk)", flush=True)
    t0 = time.time()
    null_b = np.array(Parallel(n_jobs=a.jobs)(delayed(perm_b)(m["Xb"], m["yb"], m["X2"], m["nc"], i) for i in range(a.n_perm)))
    print(f"permütasyon (b) bitti ({(time.time() - t0) / 60:.1f} dk)", flush=True)
    np.savez_compressed(OUT / f"{STEM}_perm_null.npz", null_a=null_a, null_b=null_b)

    obs_a, obs_b = m["a_auc"].mean(), m["folds"].transfer_auc.mean()
    p_a = (np.sum(null_a >= obs_a) + 1) / (len(null_a) + 1)
    p_b = (np.sum(null_b >= obs_b) + 1) / (len(null_b) + 1)
    res = pd.DataFrame([
        dict(test="(a) sg vs sg2", metric="ROC-AUC (20 tekrar)", n=f"sg {int((m['ya'] == 0).sum())} / sg2 {int((m['ya'] == 1).sum())}",
             **summ(m["a_auc"]), null_mean=null_a.mean(), null_p97_5=np.percentile(null_a, 97.5), p_perm=p_a, alpha=0.025),
        dict(test="(a) sg vs sg2", metric="dengeli doğruluk", **summ(m["a_ba"])),
        dict(test="(b) transfer: held-out cg vs sg2", metric="kat-içi ROC-AUC (100 kat)", n=f"cg {int((m['yb'] == 0).sum())} / sg2 {len(m['s2'])}",
             **summ(m["folds"].transfer_auc), null_mean=null_b.mean(), null_p97_5=np.percentile(null_b, 97.5), p_perm=p_b, alpha=0.025),
        dict(test="(b) transfer", metric="sg2 'suçlu' sınıflanma oranı (eşik 0,5)", **summ(m["folds"].frac_sg2_offender)),
        dict(test="(b) referans: sg vs cg", metric="ROC-AUC (20 tekrar)", n=f"sg {int((m['yb'] == 1).sum())} / cg {int((m['yb'] == 0).sum())}", **summ(m["sgcg"])),
    ])
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
    print(res.round(4).to_string()); print("yazıldı:", STEM)


if __name__ == "__main__":
    main()
