"""04-B - Sızıntı gösterimi (plan: 04b_sizinti_PLAN_v1_2026-10-01.md, ONAYLANDI).

Veri: v1.0.0/code/CAR_FREC_DATS.mat (Excel ile birebir aynı; boş B12 dosyasını da içerir).
Satır = denek x koşul-epok (C_1, O_1, C_2, O_2) -> 448 satır; öznitelik = 4 bant x 128 kanal x 7 istatistik = 3584.
Hücreler:
  N1 naif: tüm veride SelectKBest(k=100) -> satır bazlı StratifiedKFold(10, shuffle) ; scaler CV içinde
  N2 satır bazlı CV, seçim CV içinde        N3 denek bazlı CV, seçim tüm veride      N4 denek bazlı CV, seçim CV içinde
  P  Kol 2: denek bazlı iç içe CV (dış StratifiedGroupKFold 5 x 20 tekrar; iç 5; k ve SVM C seçimi)
Modeller: SVM (RBF, C=1, gamma='scale'; skor = decision_function), RF (500 ağaç; skor = predict_proba).
Denek skoru = deneğin satır skorlarının ortalaması. Sıfır: denek düzeyinde etiket karıştırma x 200 (N1 SVM+RF, P yalnız SVM).
Yazar: analysis/04b_leakage_v1_2026-10-01_{results,sensitivity}.csv, _null.npz
"""
from pathlib import Path
import argparse, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.io import loadmat
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, balanced_accuracy_score, accuracy_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "analysis"
STEM = "04b_leakage_v1_2026-10-01"
SEED = 20261001
BANDS = ["DELTA", "THETA", "ALFA", "BETA"]; CONDS = ["C_1", "O_1", "C_2", "O_2"]
STATS = ["Power", "RMS", "Standarddesv", "Minimun", "Maximun", "Symetry", "Kurtosis"]
NONFEAT = {"Subject", "Label"}
K_NAIVE, NAIVE_FOLDS, NAIVE_REPS = 100, 10, 10
P_REPS, P_PERM_REPS, N_PERM = 20, 5, 200
K_GRID = [10, 50, 100, 500]; C_GRID = [0.1, 1, 10]
UNVERIFIED = ["cg_rs_2013", "cg_rs_2024", "cg_rs_2025", "cg_rs_2027", "cg_rs_2035", "cg_rs_2039", "cg_rs_2041",
              "cg_rs_2058", "cg_rs_2069", "cg_rs_2073", "cg_rs_2076", "sg_rs_1011"]


def load():
    M = loadmat(ROOT / "v1.0.0" / "code" / "CAR_FREC_DATS.mat", squeeze_me=True, struct_as_record=False, simplify_cells=True)["Datos"]
    chans = list(M["DELTA"]["C_1"].keys())
    subj = [r["Subject"] for r in M["DELTA"]["C_1"][chans[0]]]
    label = np.array([r["Label"] for r in M["DELTA"]["C_1"][chans[0]]], dtype=int)
    rows, names = [], [f"{b}_{h}_{s}" for b in BANDS for h in chans for s in STATS]
    assert not (NONFEAT & set(STATS)), "Label/Subject öznitelik olamaz"
    for c in CONDS:
        blocks = []
        for b in BANDS:
            for h in chans:
                recs = M[b][c][h]
                assert [r["Subject"] for r in recs] == subj and [r["Label"] for r in recs] == list(label)
                blocks.append(np.array([[r[s] for s in STATS] for r in recs], dtype=float))
        rows.append(np.concatenate(blocks, axis=1))                      # (112, 3584)
    X = np.concatenate(rows, axis=0)                                      # satır sırası: koşul bloğu x denek
    groups = np.tile(np.arange(len(subj)), len(CONDS))
    y = np.tile(label, len(CONDS))
    cond = np.repeat(CONDS, len(subj))
    assert X.shape == (448, 3584) and len(names) == X.shape[1]
    assert not any(n.split("_")[-1] in NONFEAT for n in names)
    assert all(len(set(y[groups == g])) == 1 for g in np.unique(groups)), "bir deneğin satırları aynı etikette olmalı"
    assert np.isfinite(X).all()
    pref = pd.Series(subj).str.extract(r"^(cg|sg)_")[0].map({"cg": 0, "sg": 1}).values
    assert (pref == label).all(), "Label ile önek uyuşmuyor"
    return X, y, groups, cond, np.array(subj), np.array(names)


def model(name, seed, C=1.0):
    if name == "SVM":
        return SVC(kernel="rbf", C=C, gamma="scale")
    return RandomForestClassifier(n_estimators=500, random_state=seed, n_jobs=1)


def metrics(y, groups, s, thr):
    sub = pd.DataFrame(dict(g=groups, y=y, s=s)).groupby("g").agg(y=("y", "first"), s=("s", "mean"))
    return dict(row_auc=roc_auc_score(y, s), row_acc=accuracy_score(y, s >= thr), row_ba=balanced_accuracy_score(y, s >= thr),
                subj_auc=roc_auc_score(sub.y, sub.s), subj_ba=balanced_accuracy_score(sub.y, sub.s >= thr))


def run_simple(cell, mname, X, y, groups, seed):
    """N1-N4: k=100 sabit, varsayılan parametreler, iç içe değil."""
    global_sel = cell in ("N1", "N3")
    Xw = SelectKBest(f_classif, k=K_NAIVE).fit(X, y).transform(X) if global_sel else X   # N1/N3: tüm veride seçim (SIZINTI)
    if cell in ("N1", "N2"):
        splits = StratifiedKFold(NAIVE_FOLDS, shuffle=True, random_state=seed).split(Xw, y)
    else:
        splits = StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(Xw, y, groups)
    s = np.zeros(len(y))
    for tr, te in splits:
        steps = [("sc", StandardScaler())] + ([] if global_sel else [("sel", SelectKBest(f_classif, k=K_NAIVE))]) + [("m", model(mname, seed))]
        p = Pipeline(steps).fit(Xw[tr], y[tr])
        s[te] = p.decision_function(Xw[te]) if mname == "SVM" else p.predict_proba(Xw[te])[:, 1]
    return metrics(y, groups, s, 0.0 if mname == "SVM" else 0.5)


def run_nested(mname, X, y, groups, seed):
    """Kol 2: denek bazlı iç içe CV (tek tekrar)."""
    s = np.zeros(len(y))
    for f, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y, groups)):
        pipe = Pipeline([("sc", StandardScaler()), ("sel", SelectKBest(f_classif)), ("m", model(mname, seed))])
        grid = {"sel__k": K_GRID} | ({"m__C": C_GRID} if mname == "SVM" else {})
        gs = GridSearchCV(pipe, grid, scoring="roc_auc", n_jobs=1,
                          cv=StratifiedGroupKFold(5, shuffle=True, random_state=seed + 17 * f)).fit(X[tr], y[tr], groups=groups[tr])
        s[te] = gs.decision_function(X[te]) if mname == "SVM" else gs.predict_proba(X[te])[:, 1]
    return metrics(y, groups, s, 0.0 if mname == "SVM" else 0.5)


def permute_subject_labels(y, groups, rng):
    g = np.unique(groups); lab = pd.Series(y, index=groups).groupby(level=0).first().loc[g].values
    perm = dict(zip(g, rng.permutation(lab)))
    return np.array([perm[k] for k in groups])


def null_job(kind, mname, X, y, groups, i):
    yp = permute_subject_labels(y, groups, np.random.default_rng(SEED + 31 * i + (0 if mname == "SVM" else 7)))
    if kind == "N1":
        return run_simple("N1", mname, X, yp, groups, SEED + 500000 + i)
    return pd.DataFrame([run_nested(mname, X, yp, groups, SEED + 700000 + 50 * i + r) for r in range(P_PERM_REPS)]).mean().to_dict()


def evaluate(X, y, groups, jobs, tag, nested_models=("SVM", "RF")):
    tasks = [(c, m, r) for c in ["N1", "N2", "N3", "N4"] for m in ["SVM", "RF"] for r in range(NAIVE_REPS)]
    out = Parallel(n_jobs=jobs)(delayed(run_simple)(c, m, X, y, groups, SEED + r) for c, m, r in tasks)
    df = pd.DataFrame(out); df[["cell", "model", "rep"]] = tasks
    nt = [(m, r) for m in nested_models for r in range(P_REPS)]
    out2 = Parallel(n_jobs=jobs)(delayed(run_nested)(m, X, y, groups, SEED + r) for m, r in nt)
    d2 = pd.DataFrame(out2); d2["cell"] = "P"; d2[["model", "rep"]] = nt
    allr = pd.concat([df, d2], ignore_index=True); allr["variant"] = tag
    return allr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=15); ap.add_argument("--n-perm", type=int, default=N_PERM)
    a = ap.parse_args()
    X, y, groups, cond, subj, names = load()
    print(f"veri: {X.shape}, denek {len(np.unique(groups))} (sg {int(y[:112].sum())}, cg {int((y[:112] == 0).sum())})", flush=True)

    t0 = time.time()
    reps = [evaluate(X, y, groups, a.jobs, "primary")]
    print(f"birincil gerçek değerler ({(time.time() - t0) / 60:.1f} dk)", flush=True)
    print(reps[0].groupby(["cell", "model"])[["row_auc", "row_acc", "subj_auc", "subj_ba"]].mean().round(3), flush=True)

    # Duyarlılık
    keep_v = ~np.isin(subj[groups], UNVERIFIED)
    gv = pd.factorize(groups[keep_v])[0]
    nok = np.array([not n.endswith("_Kurtosis") for n in names])
    closed = np.isin(cond, ["C_1", "C_2"])
    for tag, (Xs, ys, gs) in {"verified_100": (X[keep_v], y[keep_v], gv),
                              "no_kurtosis": (X[:, nok], y, groups),
                              "closed_only": (X[closed], y[closed], groups[closed])}.items():
        t0 = time.time(); reps.append(evaluate(Xs, ys, gs, a.jobs, tag))
        print(f"duyarlılık {tag} ({(time.time() - t0) / 60:.1f} dk)", flush=True)
    allr = pd.concat(reps, ignore_index=True)
    allr.to_csv(OUT / f"{STEM}_reps.csv", index=False, encoding="utf-8-sig")

    # Sıfır dağılımları
    t0 = time.time()
    nulls = {}
    for kind, m in [("N1", "SVM"), ("N1", "RF"), ("P", "SVM")]:
        r = Parallel(n_jobs=a.jobs)(delayed(null_job)(kind, m, X, y, groups, i) for i in range(a.n_perm))
        nulls[f"{kind}_{m}"] = pd.DataFrame(r)
        print(f"sıfır {kind} {m} ({(time.time() - t0) / 60:.1f} dk)", flush=True)
    np.savez_compressed(OUT / f"{STEM}_null.npz", **{f"{k}__{c}": v[c].values for k, v in nulls.items() for c in v.columns})

    # Özet
    summ = allr.groupby(["variant", "cell", "model"]).agg(
        n_reps=("row_auc", "size"), row_auc=("row_auc", "mean"), row_acc=("row_acc", "mean"), row_ba=("row_ba", "mean"),
        subj_auc=("subj_auc", "mean"), subj_auc_p2_5=("subj_auc", lambda v: np.percentile(v, 2.5)),
        subj_auc_p97_5=("subj_auc", lambda v: np.percentile(v, 97.5)), subj_ba=("subj_ba", "mean")).reset_index()
    for key, metric in [("N1_SVM", "row_auc"), ("N1_RF", "row_auc"), ("P_SVM", "subj_auc")]:
        cell, m = key.split("_")
        obs = summ.query("variant=='primary' and cell==@cell and model==@m")[metric].iloc[0]
        nv = nulls[key][metric].values
        idx = summ.query("variant=='primary' and cell==@cell and model==@m").index
        summ.loc[idx, "null_metric"] = metric
        summ.loc[idx, "null_mean"] = nv.mean(); summ.loc[idx, "null_p2_5"] = np.percentile(nv, 2.5)
        summ.loc[idx, "null_p97_5"] = np.percentile(nv, 97.5); summ.loc[idx, "p_perm"] = (np.sum(nv >= obs) + 1) / (len(nv) + 1)
        for extra in ["row_acc", "subj_auc"]:
            summ.loc[idx, f"null_{extra}_mean"] = nulls[key][extra].mean()
    summ.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(summ.round(3).to_string()); print("yazıldı:", STEM)


if __name__ == "__main__":
    main()
