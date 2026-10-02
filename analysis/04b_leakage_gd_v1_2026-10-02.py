"""04-B ek: Golden Distance sütunu (yalnız gerçek değerler; permütasyon yok).

04b_leakage_v1_2026-10-01.py'deki hücreler aynı seed'lerle yeniden çalıştırılır, tahminlerden GD [ACC, Sen, Spe, F1]
(analysis/metrics_gd.py) satır ve denek düzeyinde hesaplanır. Yeniden üretilebilirlik kontrolü: AUC'ler kayıtlı
04b_leakage_v1_2026-10-01_reps.csv ile birebir karşılaştırılır.
Okur:  v1.0.0/code/CAR_FREC_DATS.mat (04b load()), analysis/04b_leakage_v1_2026-10-01_reps.csv
Yazar: analysis/04b_leakage_gd_v1_2026-10-02_{reps,results}.csv, _progress.log
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import importlib, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, balanced_accuracy_score, accuracy_score

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
os.environ["PYTHONPATH"] = str(OUT) + os.pathsep + os.environ.get("PYTHONPATH", "")
from metrics_gd import gd_from_predictions  # noqa: E402
L = importlib.import_module("04b_leakage_v1_2026-10-01")   # load(), sabitler (aynı tanımlar)
STEM = "04b_leakage_gd_v1_2026-10-02"
LOG = OUT / f"{STEM}_progress.log"


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")


def model(name, seed, C=1.0):
    return SVC(kernel="rbf", C=C, gamma="scale") if name == "SVM" else RandomForestClassifier(n_estimators=500, random_state=seed, n_jobs=1)


def metrics(y, groups, s, thr):
    sub = pd.DataFrame(dict(g=groups, y=y, s=s)).groupby("g").agg(y=("y", "first"), s=("s", "mean"))
    gr = gd_from_predictions(y, (s >= thr).astype(int))                       # 04-B ile aynı eşik kuralı (>=)
    gs = gd_from_predictions(sub.y.values, (sub.s.values >= thr).astype(int))
    return dict(row_auc=roc_auc_score(y, s), row_acc=accuracy_score(y, s >= thr), row_ba=balanced_accuracy_score(y, s >= thr),
                subj_auc=roc_auc_score(sub.y, sub.s), subj_ba=balanced_accuracy_score(sub.y, sub.s >= thr),
                row_GD=gr["gd_gd"], row_Sen=gr["Sensitivity"], row_Spe=gr["Specificity"], row_F1=gr["F1"],
                subj_GD=gs["gd_gd"], subj_ACC=gs["ACC"], subj_Sen=gs["Sensitivity"], subj_Spe=gs["Specificity"], subj_F1=gs["F1"])


def run_simple(cell, mname, X, y, groups, seed):
    global_sel = cell in ("N1", "N3")
    Xw = SelectKBest(f_classif, k=L.K_NAIVE).fit(X, y).transform(X) if global_sel else X
    splits = (StratifiedKFold(L.NAIVE_FOLDS, shuffle=True, random_state=seed).split(Xw, y) if cell in ("N1", "N2")
              else StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(Xw, y, groups))
    s = np.zeros(len(y))
    for tr, te in splits:
        steps = [("sc", StandardScaler())] + ([] if global_sel else [("sel", SelectKBest(f_classif, k=L.K_NAIVE))]) + [("m", model(mname, seed))]
        p = Pipeline(steps).fit(Xw[tr], y[tr])
        s[te] = p.decision_function(Xw[te]) if mname == "SVM" else p.predict_proba(Xw[te])[:, 1]
    return metrics(y, groups, s, 0.0 if mname == "SVM" else 0.5)


def run_nested(mname, X, y, groups, seed):
    s = np.zeros(len(y))
    for f, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y, groups)):
        pipe = Pipeline([("sc", StandardScaler()), ("sel", SelectKBest(f_classif)), ("m", model(mname, seed))])
        grid = {"sel__k": L.K_GRID} | ({"m__C": L.C_GRID} if mname == "SVM" else {})
        gs = GridSearchCV(pipe, grid, scoring="roc_auc", n_jobs=1,
                          cv=StratifiedGroupKFold(5, shuffle=True, random_state=seed + 17 * f)).fit(X[tr], y[tr], groups=groups[tr])
        s[te] = gs.decision_function(X[te]) if mname == "SVM" else gs.predict_proba(X[te])[:, 1]
    return metrics(y, groups, s, 0.0 if mname == "SVM" else 0.5)


def task(variant, cell, mname, r, X, y, groups):
    d = run_simple(cell, mname, X, y, groups, L.SEED + r) if cell != "P" else run_nested(mname, X, y, groups, L.SEED + r)
    return dict(variant=variant, cell=cell, model=mname, rep=r, **d)


def main():
    log("04-B GD ek çalıştırması başladı")
    X, y, groups, cond, subj, names = L.load()
    keep_v = ~np.isin(subj[groups], L.UNVERIFIED); gv = pd.factorize(groups[keep_v])[0]
    nok = np.array([not n.endswith("_Kurtosis") for n in names]); closed = np.isin(cond, ["C_1", "C_2"])
    variants = {"primary": (X, y, groups), "verified_100": (X[keep_v], y[keep_v], gv),
                "no_kurtosis": (X[:, nok], y, groups), "closed_only": (X[closed], y[closed], groups[closed])}
    tasks = [(v, c, m, r) for v in variants for c in ["N1", "N2", "N3", "N4"] for m in ["SVM", "RF"] for r in range(L.NAIVE_REPS)]
    tasks += [(v, "P", m, r) for v in variants for m in ["SVM", "RF"] for r in range(L.P_REPS)]
    out, t0 = [], time.time()
    for i, d in enumerate(Parallel(n_jobs=15, return_as="generator_unordered")(delayed(task)(*t, *variants[t[0]]) for t in tasks), 1):
        out.append(d)
        if i % 40 == 0 or i == len(tasks):
            el = time.time() - t0; log(f"{i}/{len(tasks)} bitti; geçen {el / 60:.1f} dk, kalan ~{el / i * (len(tasks) - i) / 60:.1f} dk")
    reps = pd.DataFrame(out).sort_values(["variant", "cell", "model", "rep"])
    reps.to_csv(OUT / f"{STEM}_reps.csv", index=False, encoding="utf-8-sig")
    old = pd.read_csv(OUT / "04b_leakage_v1_2026-10-01_reps.csv")
    mg = reps.merge(old, on=["variant", "cell", "model", "rep"], suffixes=("", "_old"))
    dmax = max((mg.row_auc - mg.row_auc_old).abs().max(), (mg.subj_auc - mg.subj_auc_old).abs().max())
    log(f"yeniden üretilebilirlik: {len(mg)}/{len(reps)} eşleşen satır, maks AUC farkı {dmax:.2e}")
    res = reps.groupby(["variant", "cell", "model"]).agg(
        n_reps=("rep", "size"), row_auc=("row_auc", "mean"), row_acc=("row_acc", "mean"), row_GD=("row_GD", "mean"),
        subj_auc=("subj_auc", "mean"), subj_ba=("subj_ba", "mean"), subj_GD=("subj_GD", "mean"),
        subj_Sen=("subj_Sen", "mean"), subj_Spe=("subj_Spe", "mean"), subj_F1=("subj_F1", "mean")).reset_index()
    res["repro_max_auc_diff"] = dmax
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    log("yazıldı: " + STEM)


if __name__ == "__main__":
    main()
