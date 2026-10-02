"""07g (YALNIZ NİCELENDİRME; tanım: CLAUDE.md "07g", commit e81e61b, sonuç görülmeden; kaynak DENETIM_RAPORU_3 bölüm 3).

Keşifsel AUC'lerin %95 GA'ları. Karar kuralı yok.
Kaynak modeller (6): 07 A/B tüm epoklar, 07a kapalı/açık, 07b, 07e -> gerçek çalıştırma aynı seed'lerle tekrarlanır,
  denek skorları kaydedilir; tekrar AUC'leri checkpoint'tekiyle |fark| <= 1e-12 olmalı (değilse DUR).
  GA: sınıf içi tabakalı denek bootstrap'ı (06 ile aynı), 2000, default_rng(20261001), percentile.
Transfer modelleri (5): 07c, 07d x 3, 07f -> kat skorları kaydedilir; kat AUC'leri transfer_folds CSV'leriyle |fark| <= 1e-12 olmalı.
  GA: ağırlıklı denek bootstrap'ı (cg 55, sg2 24 çok terimli çarpanlar; ağırlıklı Mann-Whitney kat AUC'si; 100 kat ortalaması), 2000.
Betimsel duyarlılık: sub-1105sg2 ve sub-1114sg2 hariç (22 sg2) transfer AUC'leri (yeniden eğitim yok).
Fonksiyonlar: M7.nested ve M7C.transfer'in birebir kopyaları (yalnız skorları da döndürür); öznitelikler kayıtlı npz'lerden.
Okur:  analysis/07_..._features.npz, 07abc_..._sg2_features.npz, 07de_..._{sg2_features,longblock_features}.npz,
       07f_..._sg2_longblock_features.npz, 07*_ckpt_real.jsonl, 07*_transfer_folds.csv, 01_data_audit_v2_2026-10-01.csv, 1 .set (kanal adları)
Yazar: analysis/07g_auc_ci_v1_2026-10-02_{scores.pkl,verify.csv,results.csv,progress.log}
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import importlib, json, pickle, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
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
M7C = importlib.import_module("07abc_source_decomp_v1_2026-10-02")
STEM = "07g_auc_ci_v1_2026-10-02"
LOG = OUT / f"{STEM}_progress.log"
N_BOOT, BOOT_SEED, TOL = 2000, 20261001, 1e-12
ATYPICAL = ["sub-1105sg2", "sub-1114sg2"]


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")


def nested_scores(X, y, groups, seed):
    """M7.nested ile birebir aynı; ek olarak denek skorlarını döndürür."""
    s = np.zeros(len(y))
    for f, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y, groups)):
        pipe = Pipeline([("sc", StandardScaler()), ("sel", SelectKBest(f_classif)), ("m", SVC(kernel="rbf", gamma="scale"))])
        gs = GridSearchCV(pipe, {"sel__k": M7.K_GRID, "m__C": M7.C_GRID}, scoring="roc_auc", n_jobs=1,
                          cv=StratifiedGroupKFold(5, shuffle=True, random_state=seed + 17 * f)).fit(X[tr], y[tr], groups=groups[tr])
        s[te] = gs.decision_function(X[te])
    sub = pd.DataFrame(dict(g=groups, y=y, s=s)).groupby("g").agg(y=("y", "first"), s=("s", "mean"))
    return dict(subj_auc=roc_auc_score(sub.y, sub.s), g=sub.index.values, y=sub.y.values, s=sub.s.values)


def transfer_scores(Xtr, ytr, gtr, is_cg, Xs2, gs2, seed):
    """M7C.transfer ile birebir aynı; ek olarak kat skorlarını döndürür."""
    rows = []
    for f, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(Xtr, ytr, gtr)):
        pipe = Pipeline([("sc", StandardScaler()), ("sel", SelectKBest(f_classif)), ("m", SVC(kernel="rbf", gamma="scale"))])
        gs = GridSearchCV(pipe, {"sel__k": M7.K_GRID, "m__C": M7.C_GRID}, scoring="roc_auc", n_jobs=1,
                          cv=StratifiedGroupKFold(5, shuffle=True, random_state=seed + 17 * f)).fit(Xtr[tr], ytr[tr], groups=gtr[tr])
        te_cg = te[is_cg[te]]
        sc = pd.Series(gs.decision_function(Xtr[te_cg])).groupby(gtr[te_cg]).mean()
        s_cg = sc.values
        s2 = pd.Series(gs.decision_function(Xs2)).groupby(gs2).mean()
        out = dict(fold=f, cg_ids=sc.index.values, s_cg=s_cg, sg2_ids=s2.index.values, s_sg2=s2.values)
        for tag, sel in [("sg2_24", s2.index != "sub-1084sg2"), ("sg2_25", np.ones(len(s2), bool))]:
            v = s2.values[sel]
            out[f"auc_{tag}"] = roc_auc_score(np.r_[np.zeros(len(s_cg)), np.ones(len(v))], np.r_[s_cg, v])
        rows.append(out)
    return rows


def job_src(name, X, y, g, r):
    return name, r, nested_scores(X, y, g, M7.SEED + r)


def job_tr(name, Xtr, ytr, gtr, Xs2, gs2, r):
    return name, r, transfer_scores(Xtr, ytr, gtr, ytr == 0, Xs2, gs2, M7.SEED + r)


def wauc(s_cg, w_cg, s_p, w_p):
    """Ağırlıklı Mann-Whitney AUC: P(s_sg2 > s_cg) + ½ P(eşit)."""
    W = w_cg.sum() * w_p.sum()
    if W == 0:
        return np.nan
    gt = (s_p[None, :] > s_cg[:, None]) + 0.5 * (s_p[None, :] == s_cg[:, None])
    return float(w_cg @ gt @ w_p) / W


def main():
    log("07g başladı")
    z = np.load(OUT / "07_amplitude_decomp_v1_2026-10-02_features.npz")
    A, B, y, g, subs = z["A"], z["B"], z["y"], z["groups"], list(z["subjects"])
    aud = pd.read_csv(OUT / "01_data_audit_v2_2026-10-01.csv").query("file=='epochs'").set_index("subject")
    assert (aud.loc[subs, "co_seq"] == "COCO").all()
    labels = M7C.channel_labels()
    nonC = np.array([not l.startswith("C") for l in labels * 4]); assert nonC.sum() == 384
    Xc, yc, gc = M7C.select_rows(B, y, g, M7C.CLOSED); Xo, yo, go = M7C.select_rows(B, y, g, M7C.OPEN)
    L = np.load(OUT / "07de_transfer_longblock_v1_2026-10-02_longblock_features.npz")
    assert list(L["subjects"]) == subs
    XL = L["B"]; yL = np.repeat(y[::4], 4); gL = np.repeat(np.arange(len(subs)), 4)
    src = {"07_A_log_abs": (A, y, g), "07_B_relative": (B, y, g), "07a_closed": (Xc, yc, gc), "07a_open": (Xo, yo, go),
           "07b_closed_noC": (Xc[:, nonC], yc, gc), "07e_longblock": (XL, yL, gL)}
    stored_src = {}
    for fn, mp in [("07_amplitude_decomp_v1_2026-10-02_ckpt_real.jsonl", {"A_log_abs": "07_A_log_abs", "B_relative": "07_B_relative"}),
                   ("07abc_source_decomp_v1_2026-10-02_ckpt_real.jsonl", {k: k for k in ["07a_closed", "07a_open", "07b_closed_noC"]}),
                   ("07de_transfer_longblock_v1_2026-10-02_ckpt_real.jsonl", {"07e_longblock": "07e_longblock"})]:
        for l in (OUT / fn).read_text(encoding="utf-8").splitlines():
            d = json.loads(l)
            if d["set"] in mp: stored_src[(mp[d["set"]], d["rep"])] = d["subj_auc"]
    assert len(stored_src) == 6 * M7.REPS

    # transfer girdileri (07abc / 07de / 07f ile birebir)
    zc = np.load(OUT / "07abc_source_decomp_v1_2026-10-02_sg2_features.npz"); s2c = list(zc["subjects"])
    g2c = np.repeat(s2c, 4); m2c = np.isin(np.tile(np.arange(4), len(s2c)), M7C.CLOSED)
    z2 = np.load(OUT / "07de_transfer_longblock_v1_2026-10-02_sg2_features.npz"); g2 = np.repeat(list(z2["subjects"]), 4)

    def ep(X, eps):
        return np.isin(np.tile(np.arange(4), len(X) // 4), eps)
    ALL, OPEN = [0, 1, 2, 3], [1, 3]
    zf = np.load(OUT / "07f_longblock_transfer_v1_2026-10-02_sg2_longblock_features.npz"); sf = list(zf["subjects"])
    tr = {"07c_B_closed": (Xc, yc, gc, zc["B"][m2c], g2c[m2c]),
          "07d_A_all": (A[ep(A, ALL)], y[ep(A, ALL)], g[ep(A, ALL)], z2["A"][ep(z2["A"], ALL)], g2[ep(z2["A"], ALL)]),
          "07d_B_all": (B[ep(B, ALL)], y[ep(B, ALL)], g[ep(B, ALL)], z2["B"][ep(z2["B"], ALL)], g2[ep(z2["B"], ALL)]),
          "07d_B_open": (B[ep(B, OPEN)], y[ep(B, OPEN)], g[ep(B, OPEN)], z2["B"][ep(z2["B"], OPEN)], g2[ep(z2["B"], OPEN)]),
          "07f_B_longblock": (XL, yL, gL, zf["B"], np.repeat(sf, 4))}
    fcsv = {"07c_B_closed": pd.read_csv(OUT / "07abc_source_decomp_v1_2026-10-02_transfer_folds.csv").assign(set="07c_transfer")}
    d7de = pd.read_csv(OUT / "07de_transfer_longblock_v1_2026-10-02_transfer_folds.csv")
    for k in ["07d_A_all", "07d_B_all", "07d_B_open"]: fcsv[k] = d7de[d7de.set == k]
    fcsv["07f_B_longblock"] = pd.read_csv(OUT / "07f_longblock_transfer_v1_2026-10-02_transfer_folds.csv")

    ck = OUT / f"{STEM}_scores.pkl"
    if ck.exists():
        res_src, res_tr = pickle.loads(ck.read_bytes()); log("skorlar checkpoint'ten okundu")
    else:
        t0 = time.time()
        jobs = [delayed(job_src)(k, *a, r) for k, a in src.items() for r in range(M7.REPS)] + \
               [delayed(job_tr)(k, *a, r) for k, a in tr.items() for r in range(M7.REPS)]
        log(f"{len(jobs)} iş başlıyor (15 işçi)")
        out = Parallel(n_jobs=15, verbose=0)(jobs)
        res_src = {(k, r): v for k, r, v in out if k in src}
        res_tr = {(k, r): v for k, r, v in out if k in tr}
        ck.write_bytes(pickle.dumps((res_src, res_tr)))
        log(f"yeniden çalıştırma bitti; {(time.time() - t0) / 60:.1f} dk")

    # --- doğrulama: birebir aynı mı? ---
    ver = []
    for (k, r), v in res_src.items():
        ver.append(dict(set=k, rep=r, fold=-1, metric="subj_auc", stored=stored_src[(k, r)], recomputed=v["subj_auc"]))
    for (k, r), rows in res_tr.items():
        st = fcsv[k].set_index(["rep", "fold"])
        for d in rows:
            for m in ["auc_sg2_24", "auc_sg2_25"]:
                ver.append(dict(set=k, rep=r, fold=d["fold"], metric=m, stored=st.loc[(r, d["fold"]), m], recomputed=d[m]))
    ver = pd.DataFrame(ver); ver["absdiff"] = (ver.stored - ver.recomputed).abs()
    ver.to_csv(OUT / f"{STEM}_verify.csv", index=False, encoding="utf-8-sig")
    mx = ver.groupby("set").absdiff.max()
    log("doğrulama, set başına maks |fark|: " + "; ".join(f"{k} {v:.2e}" for k, v in mx.items()))
    log(f"doğrulama: {len(ver)} değer karşılaştırıldı (kaynak {int((ver.fold == -1).sum())}, transfer kat {int((ver.fold >= 0).sum())})")
    if not (ver.absdiff <= TOL).all():
        log(f"DUR: {int((ver.absdiff > TOL).sum())} değer kayıtlıyla birebir aynı değil (> {TOL}). GA hesaplanmadı.")
        sys.exit(1)
    log("doğrulama GEÇTİ: tüm AUC'ler kayıtlı değerlerle birebir aynı (≤ 1e-12)")

    rows = []
    # --- kaynak modeller: sınıf içi tabakalı denek bootstrap'ı (06 ile aynı) ---
    for k in src:
        reps = [res_src[(k, r)] for r in range(M7.REPS)]
        gg = reps[0]["g"]; yy = reps[0]["y"]
        assert all((d["g"] == gg).all() for d in reps)
        s = np.mean([d["s"] for d in reps], axis=0)
        rng = np.random.default_rng(BOOT_SEED); ip, ineg = np.where(yy == 1)[0], np.where(yy == 0)[0]
        boot = np.array([roc_auc_score(np.r_[np.ones(len(ip)), np.zeros(len(ineg))],
                                       np.r_[s[rng.choice(ip, len(ip))], s[rng.choice(ineg, len(ineg))]]) for _ in range(N_BOOT)])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        rows.append(dict(kind="kaynak", set=k, n_pos=len(ip), n_neg=len(ineg),
                         auc_stored=np.mean([stored_src[(k, r)] for r in range(M7.REPS)]),
                         auc_meanscore=roc_auc_score(yy, s), ci_low=lo, ci_high=hi, boot_sd=boot.std(ddof=1)))
    # --- transfer modelleri: ağırlıklı denek bootstrap'ı ---
    cg_all = np.array(sorted(np.where(y[::4] == 0)[0]))           # 55 cg denek indeksi (07 sırası)
    assert len(cg_all) == 55
    for k in tr:
        folds = [d for r in range(M7.REPS) for d in res_tr[(k, r)]]
        sg2_ids = list(folds[0]["sg2_ids"]); assert all(list(d["sg2_ids"]) == sg2_ids for d in folds)
        keep24 = np.array([s != "sub-1084sg2" for s in sg2_ids]); assert keep24.sum() == 24
        ids24 = [s for s, kk in zip(sg2_ids, keep24) if kk]
        cpos = {c: i for i, c in enumerate(cg_all)}
        F = [(np.array([cpos[c] for c in d["cg_ids"]]), d["s_cg"], d["s_sg2"][keep24]) for d in folds]
        point = np.mean([d["auc_sg2_24"] for d in folds])
        assert abs(point - np.mean([wauc(sc, np.ones(len(sc)), sp, np.ones(len(sp))) for _, sc, sp in F])) < 1e-12
        rng = np.random.default_rng(BOOT_SEED); boot = np.empty(N_BOOT); n_skip = 0
        for b in range(N_BOOT):
            wc = rng.multinomial(55, np.full(55, 1 / 55)).astype(float); wp = rng.multinomial(24, np.full(24, 1 / 24)).astype(float)
            a = np.array([wauc(sc, wc[ci], sp, wp) for ci, sc, sp in F]); n_skip += int(np.isnan(a).sum())
            boot[b] = np.nanmean(a)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        ex = np.array([s not in ATYPICAL for s in ids24]); assert ex.sum() == 22
        sens = np.mean([wauc(sc, np.ones(len(sc)), sp[ex], np.ones(ex.sum())) for _, sc, sp in F])
        rows.append(dict(kind="transfer", set=k, n_pos=24, n_neg=55, auc_stored=point, auc_meanscore=np.nan, ci_low=lo, ci_high=hi,
                         boot_sd=boot.std(ddof=1), n_folds=len(F), skipped_fold_evals=n_skip, auc_excl_atypical_22=sens))
    res = pd.DataFrame(rows)
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    log("SONUÇ: " + " | ".join(f"{r.set}: {r.auc_stored:.3f} (GA {r.ci_low:.3f}–{r.ci_high:.3f})" for r in res.itertuples()))
    pd.set_option("display.width", 250); print(res.round(4).to_string())


if __name__ == "__main__":
    main()
