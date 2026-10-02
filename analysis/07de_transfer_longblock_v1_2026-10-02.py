"""07d–e (KEŞİFSEL; tanım: CLAUDE.md "07d–e", sonuç görülmeden 2026-10-02; kaynak DENETIM_RAPORU bölüm 7).

07d: en güçlü üç modelin sg2'ye kat-içi transferi (07c yöntemi aynen): A tüm epoklar, B tüm epoklar, B göz açık.
07e: 465 s uzun göz kapalı blok -> 4 x 116,25 s parça; B seti; kanal dışlaması yok; 07 P pipeline.
Karar: permütasyon p < 0,05 (tek ölçüt). Düzeltme yok.
Fonksiyonlar birebir: 07 (nested, perm_labels, subject_features, sabitler), 07abc (transfer), 02 v2 (load_block).
Okur:  analysis/07_amplitude_decomp_v1_2026-10-02_features.npz, v1.0.0 acq-epochs (sg2) ve desc-preprocessed (100 denek)
Yazar: analysis/07de_transfer_longblock_v1_2026-10-02_{sg2_features.npz,longblock_features.npz,ckpt_*.jsonl,progress.log,results.csv,transfer_folds.csv}
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import importlib, json, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.signal import welch

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent; ROOT = OUT.parent; DS = ROOT / "v1.0.0"
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
os.environ["PYTHONPATH"] = str(OUT) + os.pathsep + os.environ.get("PYTHONPATH", "")
M7 = importlib.import_module("07_amplitude_decomp_v1_2026-10-02")
M7C = importlib.import_module("07abc_source_decomp_v1_2026-10-02")
M2 = importlib.import_module("02_features_v2_2026-10-01")
STEM = "07de_transfer_longblock_v1_2026-10-02"
LOG = OUT / f"{STEM}_progress.log"
ALL, OPEN = [0, 1, 2, 3], [1, 3]
N_SEG = 4


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")


def longblock_B(sub):
    x, sr, labels, meta = M2.load_block(sub)                       # (128, 59520) = 465 s, 3. C + 5 s
    n = x.shape[1] // N_SEG
    assert n * N_SEG == x.shape[1] == int(round(465 * sr)), (sub, x.shape)
    rows = []
    for s in range(N_SEG):
        f, P = welch(x[:, s * n:(s + 1) * n], fs=sr, window="hann", nperseg=512, noverlap=256, axis=1)
        df = f[1] - f[0]
        bp = np.stack([P[:, (f >= lo) & (f < hi)].sum(1) * df for lo, hi in M7.BANDS.values()], axis=0)   # (band, ch)
        tot = P[:, (f >= M7.TOTAL[0]) & (f < M7.TOTAL[1])].sum(1) * df
        rows.append((bp / tot[None, :]).reshape(-1))               # sütun = bant*128 + kanal (07 ile aynı düzen)
    return np.array(rows)


def sel(X, g, nsub_rows, epochs):
    ep = np.tile(np.arange(nsub_rows), len(X) // nsub_rows)
    m = np.isin(ep, epochs); return X[m], g[m]


def job_tr_real(name, Xtr, ytr, gtr, Xs2, gs2, r):
    rows = M7C.transfer(Xtr, ytr, gtr, ytr == 0, Xs2, gs2, M7.SEED + r)
    return dict(set=name, rep=r, folds=rows, auc_sg2_24=float(np.mean([d["auc_sg2_24"] for d in rows])))


def job_tr_null(name, Xtr, ytr, gtr, Xs2, gs2, i):
    yp = M7.perm_labels(ytr, gtr, i)
    a = [np.mean([d["auc_sg2_24"] for d in M7C.transfer(Xtr, yp, gtr, ytr == 0, Xs2, gs2, M7.SEED + 700000 + 50 * i + r)])
         for r in range(M7.PERM_REPS)]
    return dict(set=name, perm=i, auc_sg2_24=float(np.mean(a)))


def job_real(name, X, y, g, r):
    return dict(set=name, rep=r, **{k: v for k, v in M7.nested(X, y, g, M7.SEED + r).items() if k != "chosen"})


def job_null(name, X, y, g, i):
    yp = M7.perm_labels(y, g, i)
    return dict(set=name, perm=i, subj_auc=float(np.mean([M7.nested(X, yp, g, M7.SEED + 700000 + 50 * i + r)["subj_auc"]
                                                         for r in range(M7.PERM_REPS)])))


def run_ckpt(name, tasks, fn, key):
    ck = OUT / f"{STEM}_ckpt_{name}.jsonl"; done = set()
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


def summ(real, null, metric, name):
    rv = np.array([d[metric] for d in real if d["set"] == name]); nv = np.array([d[metric] for d in null if d["set"] == name])
    obs = rv.mean(); p = (np.sum(nv >= obs) + 1) / (len(nv) + 1)
    return dict(set=name, auc=obs, auc_p2_5=np.percentile(rv, 2.5), auc_p97_5=np.percentile(rv, 97.5), n_reps=len(rv),
                null_mean=nv.mean(), null_p2_5=np.percentile(nv, 2.5), null_p97_5=np.percentile(nv, 97.5), n_perm=len(nv), p_perm=p,
                decision=("p < 0,05" if p < 0.05 else "p ≥ 0,05"))


def main():
    log("07d–e başladı")
    z = np.load(OUT / "07_amplitude_decomp_v1_2026-10-02_features.npz")
    A, B, y, g, subs = z["A"], z["B"], z["y"], z["groups"], list(z["subjects"])
    aud = pd.read_csv(OUT / "01_data_audit_v2_2026-10-01.csv").query("file=='epochs'").set_index("subject")
    sg2 = sorted(p.name for p in DS.glob("sub-*sg2") if p.is_dir())
    assert (aud.loc[subs + sg2, "co_seq"] == "COCO").all()
    # sg2 A ve B (4 epok)
    f2 = OUT / f"{STEM}_sg2_features.npz"
    if not f2.exists():
        res = Parallel(n_jobs=15)(delayed(M7.subject_features)(s) for s in sg2)
        np.savez_compressed(f2, A=np.concatenate([r[0] for r in res]), B=np.concatenate([r[1] for r in res]), subjects=np.array(sg2))
        log(f"sg2 A/B öznitelikleri: {len(sg2)} denek")
    z2 = np.load(f2); A2, B2 = z2["A"], z2["B"]; g2 = np.repeat(list(z2["subjects"]), 4)
    # 07e uzun blok B
    fl = OUT / f"{STEM}_longblock_features.npz"
    if not fl.exists():
        res = Parallel(n_jobs=15)(delayed(longblock_B)(s) for s in subs)
        L = np.concatenate(res); np.savez_compressed(fl, B=L, subjects=np.array(subs))
        log(f"uzun blok öznitelikleri: {L.shape}")
    L = np.load(fl)["B"]
    assert L.shape == (400, 512) and np.isfinite(L).all()
    yL = np.repeat(y[::4], N_SEG); gL = np.repeat(np.arange(len(subs)), N_SEG)
    assert (yL == y).all()  # 07'de de denek başına 4 satır, aynı sıra

    tsets = {"07d_A_all": (A, y, g, A2, g2, ALL), "07d_B_all": (B, y, g, B2, g2, ALL), "07d_B_open": (B, y, g, B2, g2, OPEN)}
    targs = {}
    for k, (X, yy, gg, X2, gg2, ep) in tsets.items():
        m = np.isin(np.tile(np.arange(4), len(X) // 4), ep); m2 = np.isin(np.tile(np.arange(4), len(X2) // 4), ep)
        targs[k] = (X[m], yy[m], gg[m], X2[m2], gg2[m2])
    treal = run_ckpt("tr_real", [(k, r, (k, *a, r)) for k, a in targs.items() for r in range(M7.REPS)], job_tr_real, "rep")
    log("07d gerçek: " + "; ".join(f"{k} {np.mean([d['auc_sg2_24'] for d in treal if d['set'] == k]):.3f}" for k in targs))
    real = run_ckpt("real", [("07e_longblock", r, ("07e_longblock", L, yL, gL, r)) for r in range(M7.REPS)], job_real, "rep")
    log(f"07e gerçek: {np.mean([d['subj_auc'] for d in real]):.3f}")
    tnull = run_ckpt("tr_null", [(k, i, (k, *a, i)) for k, a in targs.items() for i in range(M7.N_PERM)], job_tr_null, "perm")
    null = run_ckpt("null", [("07e_longblock", i, ("07e_longblock", L, yL, gL, i)) for i in range(M7.N_PERM)], job_null, "perm")

    rows = [summ(treal, tnull, "auc_sg2_24", k) for k in targs] + [summ(real, null, "subj_auc", "07e_longblock")]
    res = pd.DataFrame(rows)
    folds = pd.DataFrame([dict(set=d["set"], rep=d["rep"], **f) for d in treal for f in d["folds"]])
    folds.to_csv(OUT / f"{STEM}_transfer_folds.csv", index=False, encoding="utf-8-sig")
    for k in targs:
        ff = folds[folds.set == k]
        res.loc[res.set == k, "auc_sg2_25"] = ff.auc_sg2_25.mean()
        res.loc[res.set == k, "frac_sg2_offender_24"] = ff.frac_offender_sg2_24.mean()
    g7e = pd.DataFrame(real)
    for c in ["subj_ba", "GD", "ACC", "Sensitivity", "Specificity", "F1"]:
        res.loc[res.set == "07e_longblock", c] = g7e[c].mean()
    res["interpretation"] = [("transfer ediyor" if p < 0.05 else "transfer etmiyor") if s.startswith("07d") else
                             ("uzun blokta da ayrışma var → 06 null ROI/model seçimine özgü" if p < 0.05 else "ayrışma oturum başı kapalı/açık epoklarla sınırlı")
                             for s, p in zip(res.set, res.p_perm)]
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    any_tr = any(res[res.set.str.startswith("07d")].p_perm < 0.05)
    log("SONUÇ: " + " | ".join(f"{r.set}: AUC {r.auc:.3f}, p {r.p_perm:.3f} → {r.interpretation}" for r in res.itertuples()))
    log("BAŞLIK KURALI: " + ("en az bir model transfer ediyor → 'genellenmiyor' iddiası DARALTILIR" if any_tr else "hiçbir model transfer etmiyor → 'genellenmiyor' iddiası korunur"))
    pd.set_option("display.width", 250); print(res.round(4).to_string())


if __name__ == "__main__":
    main()
