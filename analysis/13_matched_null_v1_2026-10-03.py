"""13 v1 (2026-10-03) - K3 eşleşik sıfır dağılımı (tanım: CLAUDE.md, "2026-10-03 K3 Eşleşik sıfır dağılımı"; tanım commit'i ayrı).

Özgün sıfır dağılımındaki permütasyonların AYNISI (aynı etiket karıştırma üreteci ve sırası) 20 tekrara uzatılır:
permütasyon i, tekrar r = 0..19, katlama tohumu = özgün taban + 50·i + r (03(a): SEED + 100000; 07 ailesi: SEED + 700000).
r = 0..4 özgün tekrarlardır; ortalamaları kayıtlı sıfır değerine eşit olmalıdır (|fark| <= 1e-12), değilse o test için sonuç üretilmez.
Eşleşik sıfır istatistiği = r = 0..19 ortalaması; gözlenen = kayıtlı 20 tekrar ortalaması (değişmez); p = (k+1)/(N+1).

Kapsam (12 test): 03(a); 07 A, 07 B, 07a kapalı, 07a açık, 07b, 07e (kaynak: M7.nested);
                  07c, 07d A tüm, 07d B tüm, 07d B açık, 07f (transfer: M7C.transfer).
Fonksiyonlar özgün betiklerden içe aktarılır (kopyalanmaz, değiştirilmez): M3.run_a, M7.nested, M7.perm_labels, M7C.transfer,
M7C.select_rows, M7C.channel_labels. Veri seçimi özgün main() gövdelerindeki satırlarla aynıdır (doğrulama bunu da sınar).
Özgün kodda kaynak (nested) ve transfer (transfer) ayrı fonksiyonlardır; aynı geçişten çıkmadıkları için ayrı hesaplanır.
Her iş = (test, i): 20 tekrarın her biri kendi tohumuyla; sonuç işçi sayısına ve kaldığı yerden devam etmeye bağlı değildir.

Önce süre: her testin i = 0 permütasyonu (20 tekrar) çalıştırılıp süresi ölçülür, toplam tahmin edilir; 12 saati aşarsa durur.
Bu i = 0 değerleri ayrıca kayıtlı sıfırla karşılaştırılır (erken doğrulama).

Okur:  analysis/02_features_v3_*_roi.csv, 02_features_v2_*_subject_qc.csv, 01_data_audit_v2_*.csv, v1.0.0/participants.tsv (03 load),
       07_*_features.npz, 07abc_*_sg2_features.npz, 07de_*_{sg2_features,longblock_features}.npz, 07f_*_sg2_longblock_features.npz,
       v1.0.0/sub-1005sg/...acq-epochs_eeg.set (yalnız kanal adları), kayıtlı results.csv ve sıfır dağılımları (npz/jsonl). Hepsi SALT OKUMA.
Yazar: analysis/13_matched_null_v1_2026-10-03_{results.csv,null_values.csv,rapor.md,ckpt.jsonl,progress.log}
       (results/null_values/rapor var ise üzerine yazılmaz; ckpt ve log eklemelidir)
Kullanım: python 13_matched_null_v1_2026-10-03.py [--jobs 15]
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
import argparse, importlib, json, sys, time, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent; ROOT = OUT.parent
sys.path.insert(0, str(OUT)); sys.dont_write_bytecode = True
os.environ["PYTHONPATH"] = str(OUT) + os.pathsep + os.environ.get("PYTHONPATH", "")
M3 = importlib.import_module("03_batch_negcontrol_v1_2026-10-01")
M7 = importlib.import_module("07_amplitude_decomp_v1_2026-10-02")
M7C = importlib.import_module("07abc_source_decomp_v1_2026-10-02")

STEM = "13_matched_null_v1_2026-10-03"
CK, LOG = OUT / f"{STEM}_ckpt.jsonl", OUT / f"{STEM}_progress.log"
F_RES, F_VAL, F_MD = OUT / f"{STEM}_results.csv", OUT / f"{STEM}_null_values.csv", OUT / f"{STEM}_rapor.md"
REPS, ORIG_REPS, TOL, LIMIT_H = 20, 5, 1e-12, 12.0
BASE03, BASE07 = 100000, 700000
S03, S07 = "03_batch_negcontrol_v1_2026-10-01", "07_amplitude_decomp_v1_2026-10-02"
S7C, SDE, S7F = "07abc_source_decomp_v1_2026-10-02", "07de_transfer_longblock_v1_2026-10-02", "07f_longblock_transfer_v1_2026-10-02"
ORDER = ["03(a)", "07 A", "07 B", "07a closed", "07a open", "07b", "07e", "07c", "07d A all", "07d B all", "07d B open", "07f"]
COMPARISON = {"03(a)": "sg vs sg2 (ROI features)", **{t: "sg vs cg" for t in ORDER[1:7]}, **{t: "held-out cg vs sg2 (transfer)" for t in ORDER[7:]}}


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")


def jl(name):
    return [json.loads(l) for l in (OUT / name).read_text(encoding="utf-8").splitlines()]


# ---------------------------------------------------------------- işler (her (i, r) kendi tohumuyla)
def job_03a(test, Xa, ya, nc, i):
    t0 = time.time()
    rng = np.random.default_rng(M3.SEED + 7 + i)                       # özgün perm_a ile aynı üreteç
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        aucs = M3.run_a(Xa, rng.permutation(ya), REPS, M3.SEED + BASE03 + 50 * i, nc)[0]   # tekrar r: random_state = taban + 50·i + r
    return dict(test=test, i=i, vals=[float(v) for v in aucs], sec=time.time() - t0)


def job_nested(test, X, y, g, i):
    t0 = time.time()
    yp = M7.perm_labels(y, g, i)
    vals = [float(M7.nested(X, yp, g, M7.SEED + BASE07 + 50 * i + r)["subj_auc"]) for r in range(REPS)]
    return dict(test=test, i=i, vals=vals, sec=time.time() - t0)


def job_transfer(test, Xtr, ytr, gtr, Xs2, gs2, i):
    t0 = time.time()
    yp = M7.perm_labels(ytr, gtr, i)
    vals = [float(np.mean([d["auc_sg2_24"] for d in M7C.transfer(Xtr, yp, gtr, ytr == 0, Xs2, gs2, M7.SEED + BASE07 + 50 * i + r)]))
            for r in range(REPS)]
    return dict(test=test, i=i, vals=vals, sec=time.time() - t0)


# ---------------------------------------------------------------- veri (özgün main() gövdeleriyle aynı seçim)
def build_tests():
    T = {}
    # 03(a)
    roi, qc, part, rec = M3.load()
    w = M3.build(roi); g = M3.groups(w.index)
    sa = list(w.index[g.isin(["sg", "sg2"])]); ya = (g[sa] == "sg2").astype(int).values
    Xa, nc = M3.design(w, qc, part, sa, ())
    r03 = pd.read_csv(OUT / f"{S03}_results.csv")
    T["03(a)"] = dict(fn=job_03a, args=(Xa, ya, nc), N=1000, alpha=0.025, q=97.5, observed=float(r03.iloc[0]["mean"]),
                      saved=np.load(OUT / f"{S03}_perm_null.npz")["null_a"], p_saved=float(r03.iloc[0].p_perm))
    # 07 ailesi
    z = np.load(OUT / f"{S07}_features.npz")
    A, B, y, groups, subs = z["A"], z["B"], z["y"], z["groups"], list(z["subjects"])
    r07 = pd.read_csv(OUT / f"{S07}_results.csv").set_index("set"); n07 = pd.DataFrame(jl(f"{S07}_ckpt_null.jsonl"))
    r7c = pd.read_csv(OUT / f"{S7C}_results.csv").set_index("set")
    n7c, tn7c = pd.DataFrame(jl(f"{S7C}_ckpt_null.jsonl")), pd.DataFrame(jl(f"{S7C}_ckpt_tr_null.jsonl"))
    rde = pd.read_csv(OUT / f"{SDE}_results.csv").set_index("set")
    nde, tnde = pd.DataFrame(jl(f"{SDE}_ckpt_null.jsonl")), pd.DataFrame(jl(f"{SDE}_ckpt_tr_null.jsonl"))
    r7f = pd.read_csv(OUT / f"{S7F}_results.csv").iloc[0]; tn7f = pd.DataFrame(jl(f"{S7F}_ckpt_tr_null.jsonl"))

    def sv(df, name, col):
        d = df[df.set == name].sort_values("perm")
        assert list(d.perm) == list(range(M7.N_PERM)), name
        return d[col].to_numpy(float)

    def add(test, fn, args, observed, saved, p_saved):
        T[test] = dict(fn=fn, args=args, N=M7.N_PERM, alpha=0.05, q=95.0, observed=float(observed), saved=saved, p_saved=float(p_saved))

    add("07 A", job_nested, (A, y, groups), r07.loc["A_log_abs", "subj_auc"], sv(n07, "A_log_abs", "subj_auc"), r07.loc["A_log_abs", "p_perm"])
    add("07 B", job_nested, (B, y, groups), r07.loc["B_relative", "subj_auc"], sv(n07, "B_relative", "subj_auc"), r07.loc["B_relative", "p_perm"])
    # 07abc main(): göz kapalı / açık satırlar, C bloğu çıkarılmış sütunlar, sg2 göz kapalı
    labels = M7C.channel_labels()
    nonC = np.array([not l.startswith("C") for l in labels * len(M7C.BANDS)]); assert nonC.sum() == 384
    Xc, yc, gc = M7C.select_rows(B, y, groups, M7C.CLOSED); Xo, yo, go = M7C.select_rows(B, y, groups, M7C.OPEN)
    zs = np.load(OUT / f"{S7C}_sg2_features.npz"); B2c, s2 = zs["B"], list(zs["subjects"])
    g2c = np.repeat(s2, 4); m2 = np.isin(np.tile(np.arange(4), len(s2)), M7C.CLOSED)
    add("07a closed", job_nested, (Xc, yc, gc), r7c.loc["07a_closed", "auc"], sv(n7c, "07a_closed", "subj_auc"), r7c.loc["07a_closed", "p_perm"])
    add("07a open", job_nested, (Xo, yo, go), r7c.loc["07a_open", "auc"], sv(n7c, "07a_open", "subj_auc"), r7c.loc["07a_open", "p_perm"])
    add("07b", job_nested, (Xc[:, nonC], yc, gc), r7c.loc["07b_closed_noC", "auc"], sv(n7c, "07b_closed_noC", "subj_auc"), r7c.loc["07b_closed_noC", "p_perm"])
    add("07c", job_transfer, (Xc, yc, gc, B2c[m2], g2c[m2]), r7c.loc["07c_transfer", "auc"], sv(tn7c, "07c_transfer", "auc_sg2_24"), r7c.loc["07c_transfer", "p_perm"])
    # 07de main(): uzun blok, sg2 A/B
    z2 = np.load(OUT / f"{SDE}_sg2_features.npz"); A2, B2 = z2["A"], z2["B"]; g2 = np.repeat(list(z2["subjects"]), 4)
    zl = np.load(OUT / f"{SDE}_longblock_features.npz"); L = zl["B"]; assert list(zl["subjects"]) == subs and L.shape == (400, 512)
    yL = np.repeat(y[::4], 4); gL = np.repeat(np.arange(len(subs)), 4); assert (yL == y).all()
    add("07e", job_nested, (L, yL, gL), rde.loc["07e_longblock", "auc"], sv(nde, "07e_longblock", "subj_auc"), rde.loc["07e_longblock", "p_perm"])
    ALL, OPEN = [0, 1, 2, 3], [1, 3]
    for test, name, (X, X2, ep) in [("07d A all", "07d_A_all", (A, A2, ALL)), ("07d B all", "07d_B_all", (B, B2, ALL)), ("07d B open", "07d_B_open", (B, B2, OPEN))]:
        m = np.isin(np.tile(np.arange(4), len(X) // 4), ep); mm = np.isin(np.tile(np.arange(4), len(X2) // 4), ep)
        add(test, job_transfer, (X[m], y[m], groups[m], X2[mm], g2[mm]), rde.loc[name, "auc"], sv(tnde, name, "auc_sg2_24"), rde.loc[name, "p_perm"])
    # 07f main(): sg2 uzun blok (24 denek)
    zf = np.load(OUT / f"{S7F}_sg2_longblock_features.npz"); X2f = zf["B"]; sg2f = list(zf["subjects"])
    assert X2f.shape == (96, 512) and len(sg2f) == 24 and "sub-1084sg2" not in sg2f
    add("07f", job_transfer, (L, yL, gL, X2f, np.repeat(sg2f, 4)), r7f.auc, sv(tn7f, "07f_longblock_transfer", "auc_sg2_24"), r7f.p_perm)
    assert list(T) and set(T) == set(ORDER)
    for t, d in T.items():                                             # özgün p, kayıtlı sıfır ve gözlenenden yeniden üretilebilmeli
        assert len(d["saved"]) == d["N"], t
        p = (np.sum(d["saved"] >= d["observed"]) + 1) / (d["N"] + 1)
        assert abs(p - d["p_saved"]) < 1e-12, (t, p, d["p_saved"])
    return T


def read_ck():
    done = {}
    if CK.exists():
        for l in CK.read_text(encoding="utf-8").splitlines():
            d = json.loads(l); done[(d["test"], d["i"])] = d
    return done


def run(tasks, T, jobs, tag):
    done = read_ck()
    todo = [(t, i) for t, i in tasks if (t, i) not in done]
    log(f"[{tag}] toplam {len(tasks)}, checkpoint'te {len(tasks) - len(todo)}, kalan {len(todo)}")
    t0, n = time.time(), 0
    if todo:
        for res in Parallel(n_jobs=jobs, return_as="generator_unordered")(delayed(T[t]["fn"])(t, *T[t]["args"], i) for t, i in todo):
            with open(CK, "a", encoding="utf-8") as f: f.write(json.dumps(res) + "\n")
            n += 1
            if n % max(1, len(todo) // 40) == 0 or n == len(todo):
                el = time.time() - t0; log(f"[{tag}] {n}/{len(todo)}; geçen {el / 60:.1f} dk, kalan ~{el / n * (len(todo) - n) / 60:.1f} dk")
    return time.time() - t0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=15); a = ap.parse_args()
    for p in (F_RES, F_VAL, F_MD):
        if p.exists():
            sys.exit(f"DUR: {p.name} zaten var; üzerine yazılmaz.")
    log(f"K3 başladı ({a.jobs} işçi)")
    T = build_tests()
    # ---------------- süre tahmini: her testin i = 0 permütasyonu (20 tekrar)
    wall = run([(t, 0) for t in ORDER], T, a.jobs, "süre ölçümü (i = 0)")
    ck = read_ck()
    est = sum(ck[(t, 0)]["sec"] * T[t]["N"] for t in ORDER) / a.jobs / 3600
    log("1 permütasyon (20 tekrar) süresi, s: " + "; ".join(f"{t} {ck[(t, 0)]['sec']:.0f}" for t in ORDER))
    log(f"TAHMİNİ TOPLAM SÜRE: {est:.2f} saat ({a.jobs} işçi; sınır {LIMIT_H:.0f} saat)")
    if est > LIMIT_H:
        log("DUR: tahmini süre sınırı aşıyor; çalıştırılmadı."); sys.exit(2)
    early = {t: abs(float(np.mean(ck[(t, 0)]["vals"][:ORIG_REPS])) - T[t]["saved"][0]) for t in ORDER}
    log("erken doğrulama (i = 0, |r = 0..4 ortalaması − kayıtlı|): " + "; ".join(f"{t} {v:.1e}" for t, v in early.items()))
    bad_early = [t for t, v in early.items() if v > TOL]
    if bad_early:
        log(f"UYARI: i = 0'da kayıtlı sıfırla uyuşmayan testler çalıştırılmayacak: {bad_early}")
    run_tests = [t for t in ORDER if t not in bad_early]
    # ---------------- tam çalışma (kısa işler önce karışmasın diye permütasyon sırasıyla dönüşümlü)
    tasks = [(t, i) for i in range(1, 1000) for t in run_tests if i < T[t]["N"]]
    wall += run(tasks, T, a.jobs, "eşleşik sıfır")
    ck = read_ck()

    # ---------------- doğrulama, sonuç
    rows, vals = [], []
    for t in ORDER:
        d = T[t]; N = d["N"]
        if t in bad_early:
            rows.append(dict(test=t, comparison=COMPARISON[t], N=N, observed=d["observed"], result="NOT PRODUCED (validation failed at i = 0)",
                             validation_max_abs_diff=early[t])); continue
        V = np.array([ck[(t, i)]["vals"] for i in range(N)])                       # (N, 20)
        assert V.shape == (N, REPS)
        re5 = np.array([float(np.mean(v[:ORIG_REPS])) for v in V]); m20 = np.array([float(np.mean(v)) for v in V])
        diff = np.abs(re5 - d["saved"]); ok = bool(diff.max() <= TOL)
        vals += [dict(test=t, i=i, saved_5rep=d["saved"][i], recomputed_5rep=re5[i], matched_20rep=m20[i]) for i in range(N)]
        obs, al = d["observed"], d["alpha"]
        p0 = (np.sum(d["saved"] >= obs) + 1) / (N + 1); p1 = (np.sum(m20 >= obs) + 1) / (N + 1)
        row = dict(test=t, comparison=COMPARISON[t], N=N, observed=obs, alpha=al, threshold_percentile=d["q"],
                   orig_null_mean=d["saved"].mean(), orig_threshold=np.percentile(d["saved"], d["q"]), orig_p=p0, orig_k=int(np.sum(d["saved"] >= obs)),
                   orig_decision="p < alpha" if p0 < al else "p >= alpha",
                   validation_max_abs_diff=float(diff.max()), validation_ok=ok,
                   cpu_seconds=float(sum(ck[(t, i)]["sec"] for i in range(N))))
        if ok:
            row.update(matched_null_mean=m20.mean(), matched_null_sd=m20.std(ddof=1), orig_null_sd=d["saved"].std(ddof=1),
                       matched_threshold=np.percentile(m20, d["q"]), matched_p=p1, matched_k=int(np.sum(m20 >= obs)),
                       matched_decision="p < alpha" if p1 < al else "p >= alpha", decision_changed=bool((p0 < al) != (p1 < al)), result="ok")
        else:
            row.update(result=f"NOT PRODUCED (validation failed: {int((diff > TOL).sum())} of {N} permutations)")
        rows.append(row)
    res = pd.DataFrame(rows); res["wall_hours_total"] = wall / 3600
    res.to_csv(F_RES, index=False, encoding="utf-8-sig")
    pd.DataFrame(vals).to_csv(F_VAL, index=False, encoding="utf-8-sig")

    okr = res[res.result == "ok"]; ch = okr[okr.decision_changed == True]   # noqa: E712
    fmt = lambda p, N: f"≤ {1 / (N + 1):.3f}" if abs(p - 1 / (N + 1)) < 1e-12 else f"{p:.4f}"
    md = ["# K3 eşleşik sıfır dağılımı (13 v1, 2026-10-03)", "",
          "Tanım: CLAUDE.md, \"2026-10-03 K3 Eşleşik sıfır dağılımı\" (ayrı commit, çalıştırmadan önce).", "",
          "## Kararı değişen testler", ""]
    md += ([f"- **{r.test}**: özgün p {fmt(r.orig_p, r.N)}, eşleşik p {fmt(r.matched_p, r.N)} (α = {r.alpha}); "
            f"{r.orig_decision} → {r.matched_decision}." for r in ch.itertuples()] or ["Yok."])
    md += ["", "## Doğrulama", "",
           f"{len(okr)}/{len(res)} testte her permütasyonun r = 0..4 ortalaması kayıtlı sıfır değerine eşit (|fark| ≤ 1e-12); "
           f"en büyük |fark| {res.validation_max_abs_diff.max():.2e}."]
    md += [f"- {r.test}: SONUÇ ÜRETİLMEDİ ({r.result})" for r in res[res.result != "ok"].itertuples()]
    md += ["", "## Sonuçlar", "",
           "| Test | N | Gözlenen | Özgün sıfır: ort. | eşik | p | Eşleşik sıfır: ort. | eşik | p | α | Karar değişti mi | Doğrulama maks. fark |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in okr.itertuples():
        md.append(f"| {r.test} | {r.N} | {r.observed:.3f} | {r.orig_null_mean:.3f} | {r.orig_threshold:.3f} | {fmt(r.orig_p, r.N)} | "
                  f"{r.matched_null_mean:.3f} | {r.matched_threshold:.3f} | {fmt(r.matched_p, r.N)} | {r.alpha} | "
                  f"{'EVET' if r.decision_changed else 'hayır'} | {r.validation_max_abs_diff:.1e} |")
    md += ["", "Eşik: sıfır dağılımının tek yönlü %95'liği (03(a): %97,5'liği). Sıfır SD'si (özgün → eşleşik): "
           + "; ".join(f"{r.test} {r.orig_null_sd:.3f} → {r.matched_null_sd:.3f}" for r in okr.itertuples()) + ".", "",
           "## Süre", "",
           f"Duvar saati toplamı {wall / 3600:.2f} saat ({a.jobs} işçi); önceden tahmin {est:.2f} saat. Test başına işlemci süresi (s): "
           + "; ".join(f"{r.test} {r.cpu_seconds:.0f}" for r in okr.itertuples()) + "."]
    F_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    log("bitti"); print("\n".join(md))


if __name__ == "__main__":
    main()
