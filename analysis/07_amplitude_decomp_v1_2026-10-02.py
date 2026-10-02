"""07 - Genlik ayrıştırması (KEŞİFSEL; tanım: CLAUDE.md "07 Genlik ayrıştırması", sonuç görülmeden 2026-10-02).

(A) log10 mutlak bant gücü vs (B) göreli bant gücü (1-30 Hz toplamına bölünmüş); 128 kanal x 4 bant = 512 öznitelik.
Örneklem: kimliği doğrulanmış 100 denek (04-A; cg 55, sg 45); veri: yayımlanan acq-epochs (4 epok) -> 400 satır.
Pipeline = 04-B P: Scaler -> SelectKBest(k) -> SVM RBF(C); dış StratifiedGroupKFold(5) x 20, iç 5; denek skoru = ortalama karar değeri.
Sıfır: denek düzeyinde etiket karıştırma x 200 (permütasyon başına 5 tekrar).
İlerleme: analysis/07_..._progress.log ; checkpoint: _ckpt_real.jsonl, _ckpt_null.jsonl (yeniden başlatınca tamamlananlar atlanır).
Okur:  analysis/04a_excel_audit_v1_2026-10-01_ids.csv, v1.0.0/sub-*/eeg/*_acq-epochs_eeg.set
Yazar: analysis/07_amplitude_decomp_v1_2026-10-02_{features.npz,results.csv,reps.csv,null.npz,progress.log,ckpt_*.jsonl}
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")          # işçi başına tek iş parçacığı (aşırı abonelik yok)
from pathlib import Path
import argparse, json, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.io import loadmat
from scipy.signal import welch
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedGroupKFold, GridSearchCV
from sklearn.metrics import roc_auc_score, balanced_accuracy_score

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "analysis"; DS = ROOT / "v1.0.0"
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
from metrics_gd import gd_from_predictions  # noqa: E402

STEM = "07_amplitude_decomp_v1_2026-10-02"
SEED = 20261001
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
TOTAL = (1, 30)
K_GRID, C_GRID = [10, 50, 100, 500], [0.1, 1, 10]
REPS, PERM_REPS, N_PERM = 20, 5, 200
LOG = OUT / f"{STEM}_progress.log"


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def subject_features(sub):
    E = loadmat(DS / sub / "eeg" / f"{sub}_task-restingstate_acq-epochs_eeg.set", squeeze_me=True,
                struct_as_record=False, simplify_cells=True)
    x = np.asarray(E["data"], dtype=np.float64)                     # (128, 6400, 4)
    assert x.ndim == 3 and x.shape[2] == 4, (sub, x.shape)
    f, P = welch(x, fs=float(E["srate"]), window="hann", nperseg=512, noverlap=256, axis=1)   # (ch, freq, ep)
    df = f[1] - f[0]
    bp = np.stack([P[:, (f >= lo) & (f < hi), :].sum(1) * df for lo, hi in BANDS.values()], axis=1)  # (ch, band, ep)
    tot = P[:, (f >= TOTAL[0]) & (f < TOTAL[1]), :].sum(1) * df                                       # (ch, ep)
    A = np.log10(bp).transpose(2, 1, 0).reshape(4, -1)                # (ep, band*ch)
    B = (bp / tot[:, None, :]).transpose(2, 1, 0).reshape(4, -1)
    return A, B


def build():
    fn = OUT / f"{STEM}_features.npz"
    if fn.exists():
        z = np.load(fn, allow_pickle=False); log(f"öznitelikler checkpoint'ten okundu: {fn.name}")
        return z["A"], z["B"], z["y"], z["groups"], z["subjects"]
    ids = pd.read_csv(OUT / "04a_excel_audit_v1_2026-10-01_ids.csv")
    ids = ids[ids.in_participants & ids.in_dataset_dirs]
    subs = ids.bids_id.tolist(); lab = ids.label.values.astype(int)
    assert len(subs) == 100 and (lab == ids.bids_id.str.endswith("sg").astype(int).values).all()
    res = Parallel(n_jobs=15)(delayed(subject_features)(s) for s in subs)
    A = np.concatenate([r[0] for r in res]); B = np.concatenate([r[1] for r in res])
    groups = np.repeat(np.arange(len(subs)), 4); y = np.repeat(lab, 4)
    assert A.shape == (400, 512) and np.isfinite(A).all() and np.isfinite(B).all()
    np.savez_compressed(fn, A=A, B=B, y=y, groups=groups, subjects=np.array(subs))
    log(f"öznitelikler hesaplandı: A {A.shape}, B {B.shape}; sg {int(lab.sum())}, cg {int((lab == 0).sum())}")
    return A, B, y, groups, np.array(subs)


def nested(X, y, groups, seed):
    s = np.zeros(len(y)); chosen = []
    for f, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y, groups)):
        pipe = Pipeline([("sc", StandardScaler()), ("sel", SelectKBest(f_classif)), ("m", SVC(kernel="rbf", gamma="scale"))])
        gs = GridSearchCV(pipe, {"sel__k": K_GRID, "m__C": C_GRID}, scoring="roc_auc", n_jobs=1,
                          cv=StratifiedGroupKFold(5, shuffle=True, random_state=seed + 17 * f)).fit(X[tr], y[tr], groups=groups[tr])
        s[te] = gs.decision_function(X[te]); chosen.append((gs.best_params_["sel__k"], gs.best_params_["m__C"]))
    sub = pd.DataFrame(dict(g=groups, y=y, s=s)).groupby("g").agg(y=("y", "first"), s=("s", "mean"))
    gd = gd_from_predictions(sub.y.values, (sub.s.values > 0).astype(int))
    return dict(subj_auc=roc_auc_score(sub.y, sub.s), subj_ba=balanced_accuracy_score(sub.y, sub.s > 0),
                row_auc=roc_auc_score(y, s), GD=gd["gd_gd"], ACC=gd["ACC"], Sensitivity=gd["Sensitivity"],
                Specificity=gd["Specificity"], F1=gd["F1"], chosen=json.dumps(chosen))


def perm_labels(y, groups, i):
    rng = np.random.default_rng(SEED + 31 * i)
    g = np.unique(groups); lab = pd.Series(y, index=groups).groupby(level=0).first().loc[g].values
    m = dict(zip(g, rng.permutation(lab))); return np.array([m[k] for k in groups])


def job_real(fs, X, y, groups, r):
    return dict(set=fs, rep=r, **nested(X, y, groups, SEED + r))


def job_null(fs, X, y, groups, i):
    yp = perm_labels(y, groups, i)
    rr = [nested(X, yp, groups, SEED + 700000 + 50 * i + r) for r in range(PERM_REPS)]
    return dict(set=fs, perm=i, subj_auc=float(np.mean([d["subj_auc"] for d in rr])), subj_ba=float(np.mean([d["subj_ba"] for d in rr])))


def run_ckpt(name, tasks, fn, key, jobs):
    ck = OUT / f"{STEM}_ckpt_{name}.jsonl"
    done = set()
    if ck.exists():
        for line in ck.read_text(encoding="utf-8").splitlines():
            d = json.loads(line); done.add((d["set"], d[key]))
    todo = [t for t in tasks if (t[0], t[-1]) not in done]
    log(f"[{name}] toplam {len(tasks)}, checkpoint'te {len(done)}, kalan {len(todo)}")
    t0 = time.time(); n = 0
    for res in Parallel(n_jobs=jobs, return_as="generator_unordered")(delayed(fn)(*t) for t in todo):
        with open(ck, "a", encoding="utf-8") as f:
            f.write(json.dumps(res) + "\n")
        n += 1
        if n % max(1, len(todo) // 20) == 0 or n == len(todo):
            el = time.time() - t0
            log(f"[{name}] {len(done) + n}/{len(tasks)} bitti; geçen {el / 60:.1f} dk, kalan ~{el / n * (len(todo) - n) / 60:.1f} dk")
    return pd.DataFrame([json.loads(l) for l in ck.read_text(encoding="utf-8").splitlines()])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=15); ap.add_argument("--n-perm", type=int, default=N_PERM)
    a = ap.parse_args()
    log("07 başladı")
    A, B, y, groups, subs = build()
    sets = {"A_log_abs": A, "B_relative": B}
    real = run_ckpt("real", [(k, X, y, groups, r) for k, X in sets.items() for r in range(REPS)], job_real, "rep", a.jobs)
    real.to_csv(OUT / f"{STEM}_reps.csv", index=False, encoding="utf-8-sig")
    log("gerçek değerler: " + "; ".join(f"{k} AUC {g.subj_auc.mean():.3f}" for k, g in real.groupby("set")))
    null = run_ckpt("null", [(k, X, y, groups, i) for k, X in sets.items() for i in range(a.n_perm)], job_null, "perm", a.jobs)
    rows = []
    for k, g in real.groupby("set"):
        nv = null[null.set == k].subj_auc.values; obs = g.subj_auc.mean()
        rows.append(dict(set=k, n_subjects=len(subs), n_reps=len(g), subj_auc=obs,
                         subj_auc_p2_5=np.percentile(g.subj_auc, 2.5), subj_auc_p97_5=np.percentile(g.subj_auc, 97.5),
                         subj_ba=g.subj_ba.mean(), row_auc=g.row_auc.mean(), GD=g.GD.mean(), ACC=g.ACC.mean(),
                         Sensitivity=g.Sensitivity.mean(), Specificity=g.Specificity.mean(), F1=g.F1.mean(),
                         n_perm=len(nv), null_mean=nv.mean(), null_p2_5=np.percentile(nv, 2.5), null_p97_5=np.percentile(nv, 97.5),
                         p_perm=(np.sum(nv >= obs) + 1) / (len(nv) + 1)))
    res = pd.DataFrame(rows)
    res["separation"] = np.where(res.p_perm < 0.05, "var", "≈ şans")
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    np.savez_compressed(OUT / f"{STEM}_null.npz", **{k: null[null.set == k].sort_values("perm").subj_auc.values for k in sets})
    sep = dict(zip(res.set, res.separation))
    rule = {("var", "≈ şans"): "A var, B ≈ şans → mutlak genlik kaynaklı → 05'e devam",
            ("var", "var"): "A ve B var → DUR, kullanıcıya dön",
            ("≈ şans", "var"): "A ≈ şans, B var → DUR, kullanıcıya dön",
            ("≈ şans", "≈ şans"): "ikisi de ≈ şans → kohorta özgü; 05'e devam"}[(sep["A_log_abs"], sep["B_relative"])]
    log("SONUÇ: " + " | ".join(f"{r.set}: AUC {r.subj_auc:.3f}, sıfır {r.null_mean:.3f}, p {r.p_perm:.4f}, GD {r.GD:.3f}" for r in res.itertuples()))
    log("KURAL: " + rule)
    print(res.round(4).to_string())


if __name__ == "__main__":
    main()
