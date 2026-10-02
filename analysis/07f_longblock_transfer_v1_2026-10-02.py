"""07f (KEŞİFSEL; tanım: CLAUDE.md "07f", commit 6a4439c, sonuç görülmeden; kaynak DENETIM_RAPORU_2 bölüm 4).

07e uzun blok modelinin (B seti, 4 x 116,25 s, kanal dışlaması yok; sg 45 + cg 55) sg2'ye kat-içi transferi (07c yöntemi aynen).
Test kümesi: sg2 uzun blok, 24 denek (sub-1084sg2'nin uzun bloğu yok). Karar: permütasyon p < 0,05 (tek ölçüt).
Fonksiyonlar birebir: 07de (longblock_B, job_tr_real, job_tr_null), 07 (sabitler), 07abc (transfer).
Okur:  analysis/07de_transfer_longblock_v1_2026-10-02_longblock_features.npz (sg + cg; 07e ile aynı), v1.0.0 sg2 desc-preprocessed
Yazar: analysis/07f_longblock_transfer_v1_2026-10-02_{sg2_longblock_features.npz,ckpt_*.jsonl,progress.log,results.csv,transfer_folds.csv}
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import importlib, json, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent; ROOT = OUT.parent; DS = ROOT / "v1.0.0"
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
os.environ["PYTHONPATH"] = str(OUT) + os.pathsep + os.environ.get("PYTHONPATH", "")
M7 = importlib.import_module("07_amplitude_decomp_v1_2026-10-02")
MDE = importlib.import_module("07de_transfer_longblock_v1_2026-10-02")
STEM = "07f_longblock_transfer_v1_2026-10-02"
LOG = OUT / f"{STEM}_progress.log"
NAME = "07f_longblock_transfer"


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")


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


def main():
    log("07f başladı")
    z7 = np.load(OUT / "07_amplitude_decomp_v1_2026-10-02_features.npz")
    y7, subs = z7["y"], list(z7["subjects"])
    L = np.load(OUT / "07de_transfer_longblock_v1_2026-10-02_longblock_features.npz")
    assert list(L["subjects"]) == subs
    X = L["B"]; y = np.repeat(y7[::4], MDE.N_SEG); g = np.repeat(np.arange(len(subs)), MDE.N_SEG)
    sg2 = [s for s in sorted(p.name for p in DS.glob("sub-*sg2") if p.is_dir()) if s != "sub-1084sg2"]
    assert len(sg2) == 24
    f2 = OUT / f"{STEM}_sg2_longblock_features.npz"
    if not f2.exists():
        res = Parallel(n_jobs=15)(delayed(MDE.longblock_B)(s) for s in sg2)
        np.savez_compressed(f2, B=np.concatenate(res), subjects=np.array(sg2))
        log(f"sg2 uzun blok öznitelikleri: {len(sg2)} denek")
    X2 = np.load(f2)["B"]; g2 = np.repeat(sg2, MDE.N_SEG)
    assert X2.shape == (96, 512) and np.isfinite(X2).all()
    treal = run_ckpt("tr_real", [(NAME, r, (NAME, X, y, g, X2, g2, r)) for r in range(M7.REPS)], MDE.job_tr_real, "rep")
    log(f"07f gerçek transfer AUC: {np.mean([d['auc_sg2_24'] for d in treal]):.3f}")
    tnull = run_ckpt("tr_null", [(NAME, i, (NAME, X, y, g, X2, g2, i)) for i in range(M7.N_PERM)], MDE.job_tr_null, "perm")
    res = pd.DataFrame([MDE.summ(treal, tnull, "auc_sg2_24", NAME)])
    folds = pd.DataFrame([dict(set=d["set"], rep=d["rep"], **f) for d in treal for f in d["folds"]])
    folds.to_csv(OUT / f"{STEM}_transfer_folds.csv", index=False, encoding="utf-8-sig")
    res["frac_sg2_offender_24"] = folds.frac_offender_sg2_24.mean()
    res["interpretation"] = np.where(res.p_perm < 0.05, "transfer ediyor → iddia daraltılır",
                                     "transfer kanıtı yok → iddia beş modelin hepsi için geçerli")
    res.to_csv(OUT / f"{STEM}_results.csv", index=False, encoding="utf-8-sig")
    r = res.iloc[0]
    log(f"SONUÇ: transfer AUC {r.auc:.3f} (tekrarlar {r.auc_p2_5:.3f}–{r.auc_p97_5:.3f}), sıfır {r.null_mean:.3f} [{r.null_p2_5:.3f}–{r.null_p97_5:.3f}], p {r.p_perm:.4f} → {r.interpretation}")
    pd.set_option("display.width", 250); print(res.round(4).T)


if __name__ == "__main__":
    main()
