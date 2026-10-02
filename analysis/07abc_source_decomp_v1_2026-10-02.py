"""07a–c - B setinin (göreli bant gücü) kaynak ayrıştırması (KEŞİFSEL; tanım: CLAUDE.md "07a–c", sonuç görülmeden 2026-10-02).

07a: yalnız göz kapalı (C1+C2) ve yalnız göz açık (O1+O2) epoklar, ayrı ayrı.
07b: yalnız göz kapalı, frontal C bloğu (C1–C32) çıkarılmış.
07c: 07a göz kapalı modeli (sg+cg eğitimi); her dış katta held-out cg vs sg2 kat-içi transfer AUC'si (03 yöntemi).
Pipeline ve sabitler 07_amplitude_decomp_v1_2026-10-02.py'den (P: Scaler -> SelectKBest -> SVM; 20 tekrar; 200 perm x 5 tekrar).
Okur:  analysis/07_amplitude_decomp_v1_2026-10-02_features.npz, analysis/01_data_audit_v2_2026-10-01.csv (epok sırası kontrolü),
       v1.0.0/sub-*sg2/eeg/*_acq-epochs_eeg.set (sg2 öznitelikleri), 1 adet .set (kanal adları)
Yazar: analysis/07abc_source_decomp_v1_2026-10-02_{sg2_features.npz,ckpt_*.jsonl,progress.log,results.csv,transfer_folds.csv,descriptive.csv}
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import importlib, json, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.io import loadmat
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedGroupKFold, GridSearchCV
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent; ROOT = OUT.parent; DS = ROOT / "v1.0.0"
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
os.environ["PYTHONPATH"] = str(OUT) + os.pathsep + os.environ.get("PYTHONPATH", "")
M7 = importlib.import_module("07_amplitude_decomp_v1_2026-10-02")
STEM = "07abc_source_decomp_v1_2026-10-02"
LOG = OUT / f"{STEM}_progress.log"
CLOSED, OPEN = [0, 2], [1, 3]           # acq-epochs sırası C1, O1, C2, O2 (01 audit: tüm 4-epoklu deneklerde COCO)
BANDS = list(M7.BANDS)


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")


def channel_labels():
    E = loadmat(DS / "sub-1005sg" / "eeg" / "sub-1005sg_task-restingstate_acq-epochs_eeg.set", squeeze_me=True,
                struct_as_record=False, simplify_cells=True, variable_names=["chanlocs"])
    return [c["labels"] for c in E["chanlocs"]]


def select_rows(X, y, groups, epochs):
    ep = np.tile(np.arange(4), len(np.unique(groups)))
    m = np.isin(ep, epochs)
    return X[m], y[m], groups[m]


def transfer(Xtr, ytr, gtr, is_cg, Xs2, gs2, seed):
    """03 yöntemi: her dış katta held-out cg vs tüm sg2, aynı modelle; kat-içi AUC."""
    rows = []
    for f, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(Xtr, ytr, gtr)):
        pipe = Pipeline([("sc", StandardScaler()), ("sel", SelectKBest(f_classif)), ("m", SVC(kernel="rbf", gamma="scale"))])
        gs = GridSearchCV(pipe, {"sel__k": M7.K_GRID, "m__C": M7.C_GRID}, scoring="roc_auc", n_jobs=1,
                          cv=StratifiedGroupKFold(5, shuffle=True, random_state=seed + 17 * f)).fit(Xtr[tr], ytr[tr], groups=gtr[tr])
        te_cg = te[is_cg[te]]
        s_cg = pd.Series(gs.decision_function(Xtr[te_cg])).groupby(gtr[te_cg]).mean().values
        s2 = pd.Series(gs.decision_function(Xs2)).groupby(gs2).mean()
        out = dict(fold=f, n_cg_heldout=len(s_cg))
        for tag, sel in [("sg2_24", s2.index != "sub-1084sg2"), ("sg2_25", np.ones(len(s2), bool))]:
            v = s2.values[sel]
            out[f"auc_{tag}"] = roc_auc_score(np.r_[np.zeros(len(s_cg)), np.ones(len(v))], np.r_[s_cg, v])
            out[f"frac_offender_{tag}"] = float((v >= 0).mean())
        rows.append(out)
    return rows


def job_real(name, X, y, g, r):
    return dict(set=name, rep=r, **{k: v for k, v in M7.nested(X, y, g, M7.SEED + r).items() if k != "chosen"})


def job_null(name, X, y, g, i):
    yp = M7.perm_labels(y, g, i)
    rr = [M7.nested(X, yp, g, M7.SEED + 700000 + 50 * i + r)["subj_auc"] for r in range(M7.PERM_REPS)]
    return dict(set=name, perm=i, subj_auc=float(np.mean(rr)))


def job_tr_real(Xtr, ytr, gtr, Xs2, gs2, r):
    rows = transfer(Xtr, ytr, gtr, ytr == 0, Xs2, gs2, M7.SEED + r)
    return dict(set="07c_transfer", rep=r, folds=rows, auc_sg2_24=float(np.mean([d["auc_sg2_24"] for d in rows])))


def job_tr_null(Xtr, ytr, gtr, Xs2, gs2, i):
    yp = M7.perm_labels(ytr, gtr, i)
    a = [np.mean([d["auc_sg2_24"] for d in transfer(Xtr, yp, gtr, ytr == 0, Xs2, gs2, M7.SEED + 700000 + 50 * i + r)])
         for r in range(M7.PERM_REPS)]
    return dict(set="07c_transfer", perm=i, auc_sg2_24=float(np.mean(a)))


def run_ckpt(name, tasks, fn, key):
    ck = OUT / f"{STEM}_ckpt_{name}.jsonl"
    done = set()
    if ck.exists():
        for l in ck.read_text(encoding="utf-8").splitlines():
            d = json.loads(l); done.add((d["set"], d[key]))
    todo = [t for t in tasks if (t[0], t[1]) not in done]
    log(f"[{name}] toplam {len(tasks)}, checkpoint'te {len(done)}, kalan {len(todo)}")
    t0, n = time.time(), 0
    for res in Parallel(n_jobs=15, return_as="generator_unordered")(delayed(fn)(*t[2]) for t in todo):
        with open(ck, "a", encoding="utf-8") as f: f.write(json.dumps(res) + "\n")
        n += 1
        if n % max(1, len(todo) // 20) == 0 or n == len(todo):
            el = time.time() - t0; log(f"[{name}] {len(done) + n}/{len(tasks)}; geçen {el / 60:.1f} dk, kalan ~{el / n * (len(todo) - n) / 60:.1f} dk")
    return [json.loads(l) for l in ck.read_text(encoding="utf-8").splitlines()]


def summarize(real, null, metric, name):
    obs = np.mean([d[metric] for d in real if d["set"] == name]); nv = np.array([d[metric] for d in null if d["set"] == name])
    rv = [d[metric] for d in real if d["set"] == name]
    return dict(set=name, auc=obs, auc_p2_5=np.percentile(rv, 2.5), auc_p97_5=np.percentile(rv, 97.5), n_reps=len(rv),
                null_mean=nv.mean(), null_p97_5=np.percentile(nv, 97.5), n_perm=len(nv), p_perm=(np.sum(nv >= obs) + 1) / (len(nv) + 1),
                high=bool(obs >= 0.65 and (np.sum(nv >= obs) + 1) / (len(nv) + 1) < 0.05))


def main():
    log("07a–c başladı")
    z = np.load(OUT / "07_amplitude_decomp_v1_2026-10-02_features.npz")
    B, y, groups, subs = z["B"], z["y"], z["groups"], list(z["subjects"])
    aud = pd.read_csv(OUT / "01_data_audit_v2_2026-10-01.csv").query("file=='epochs'").set_index("subject")
    assert (aud.loc[subs, "co_seq"] == "COCO").all(), "epok sırası COCO değil"
    labels = channel_labels()
    nonC = np.array([not l.startswith("C") for l in labels * len(BANDS)])          # sütun = bant*128 + kanal
    assert nonC.sum() == 384
    Xc, yc, gc = select_rows(B, y, groups, CLOSED); Xo, yo, go = select_rows(B, y, groups, OPEN)
    sets = {"07a_closed": (Xc, yc, gc), "07a_open": (Xo, yo, go), "07b_closed_noC": (Xc[:, nonC], yc, gc)}

    # sg2 öznitelikleri (göz kapalı epoklar)
    fn = OUT / f"{STEM}_sg2_features.npz"
    sg2 = sorted(p.name for p in DS.glob("sub-*sg2") if p.is_dir())
    assert (aud.loc[sg2, "co_seq"] == "COCO").all()
    if not fn.exists():
        res = Parallel(n_jobs=15)(delayed(M7.subject_features)(s) for s in sg2)
        np.savez_compressed(fn, B=np.concatenate([r[1] for r in res]), subjects=np.array(sg2))
        log(f"sg2 öznitelikleri: {len(sg2)} denek")
    zs = np.load(fn); B2, s2 = zs["B"], list(zs["subjects"])
    g2 = np.repeat(s2, 4); ep2 = np.tile(np.arange(4), len(s2)); m2 = np.isin(ep2, CLOSED)
    Xs2, gs2 = B2[m2], g2[m2]

    real = run_ckpt("real", [(k, r, (k, X, yy, gg, r)) for k, (X, yy, gg) in sets.items() for r in range(M7.REPS)], job_real, "rep")
    log("gerçek: " + "; ".join(f"{k} {np.mean([d['subj_auc'] for d in real if d['set'] == k]):.3f}" for k in sets))
    treal = run_ckpt("tr_real", [("07c_transfer", r, (Xc, yc, gc, Xs2, gs2, r)) for r in range(M7.REPS)], job_tr_real, "rep")
    log(f"07c gerçek transfer AUC (sg2=24): {np.mean([d['auc_sg2_24'] for d in treal]):.3f}")
    null = run_ckpt("null", [(k, i, (k, X, yy, gg, i)) for k, (X, yy, gg) in sets.items() for i in range(M7.N_PERM)], job_null, "perm")
    tnull = run_ckpt("tr_null", [("07c_transfer", i, (Xc, yc, gc, Xs2, gs2, i)) for i in range(M7.N_PERM)], job_tr_null, "perm")

    rows = [summarize(real, null, "subj_auc", k) for k in sets] + [summarize(treal, tnull, "auc_sg2_24", "07c_transfer")]
    res = pd.DataFrame(rows)
    for k in sets:
        g = pd.DataFrame([d for d in real if d["set"] == k])
        for c in ["subj_ba", "GD", "ACC", "Sensitivity", "Specificity", "F1"]:
            res.loc[res.set == k, c] = g[c].mean()
    folds = pd.DataFrame([dict(rep=d["rep"], **f) for d in treal for f in d["folds"]])
    folds.to_csv(OUT / f"{STEM}_transfer_folds.csv", index=False, encoding="utf-8-sig")
    tr = res.set == "07c_transfer"
    res.loc[tr, "auc_sg2_25"] = folds.auc_sg2_25.mean()
    res.loc[tr, "frac_sg2_offender_24"] = folds.frac_offender_sg2_24.mean()
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")

    # Betimsel: göz kapalı göreli delta / alfa (denek ortalaması)
    def rel(Xm, gm, band, chmask):
        b = BANDS.index(band); cols = np.arange(b * 128, (b + 1) * 128)[chmask]
        return pd.Series(Xm[:, cols].mean(1)).groupby(gm).mean()
    isC = np.array([l.startswith("C") for l in labels]); isA = np.array([l.startswith("A") for l in labels]); allc = np.ones(128, bool)
    desc = []
    for grp, Xm, gm in [("sg", Xc[yc == 1], gc[yc == 1]), ("cg", Xc[yc == 0], gc[yc == 0]),
                        ("sg2_24", Xs2[gs2 != "sub-1084sg2"], gs2[gs2 != "sub-1084sg2"])]:
        for lab, band, mask in [("rel_delta_all", "delta", allc), ("rel_delta_frontalC", "delta", isC),
                                ("rel_alpha_all", "alpha", allc), ("rel_alpha_Ablock", "alpha", isA)]:
            v = rel(Xm, gm, band, mask)
            desc.append(dict(group=grp, measure=lab, n=len(v), median=v.median(), q1=v.quantile(.25), q3=v.quantile(.75)))
    pd.DataFrame(desc).to_csv(OUT / f"{STEM}_descriptive.csv", index=False, encoding="utf-8-sig")

    r = res.set_index("set")
    cl, op, nc, tc = r.loc["07a_closed"], r.loc["07a_open"], r.loc["07b_closed_noC"], r.loc["07c_transfer"]
    if cl.auc <= 0.60 and op.high:
        rule = "07a kapalı ≤ 0,60 ve açık yüksek → OKÜLER ARTEFAKT açıklaması"
    elif cl.high and nc.high:
        rule = "07a kapalı yüksek ve 07b korunuyor → GERÇEK SPEKTRAL FARK ihtimali; " + (
            "07c ≥ 0,60 ve p < 0,05 → batch açıklaması ZAYIF" if (tc.auc >= 0.60 and tc.p_perm < 0.05) else "07c < 0,60 veya p ≥ 0,05 → batch açıklaması GÜÇLÜ")
    else:
        rule = "BELİRSİZ (kapsanmayan durum)" + (" — kapalı yüksek ama 07b korunmuyor → frontal kaynaklı" if cl.high and not nc.high else "")
    log("SONUÇ: " + " | ".join(f"{k}: AUC {v.auc:.3f}, p {v.p_perm:.3f}" for k, v in r.iterrows()))
    log("KURAL: " + rule + "  → DUR (05 kullanıcı onayı bekliyor)")
    pd.set_option("display.width", 250); print(res.round(4).to_string()); print(pd.DataFrame(desc).round(4).to_string())


if __name__ == "__main__":
    main()
