"""12 v1 (2026-10-03) - K2 eşleştirilmiş permütasyon p değerleri (tanım: CLAUDE.md, "2026-10-03 Gönderim öncesi kontroller").

Tanım: her permütasyon testinde gözlenen istatistik, sıfır dağılımında kullanılan tekrarlarla AYNI tekrarlar (aynı CV tohumları)
üzerinden yeniden hesaplanır; p = (k+1)/(N+1). Yeni model eğitimi YOK; yalnız kayıtlı değerler okunur.
Kural: tohumlar farklıysa ya da tekrar başına değer kayıtlı değilse eşleşik değer HESAPLANMAZ, nedeni yazılır.

Bu betik her test için
  1. kaynak betikte tohum ifadelerinin gerçekten beklenen satırlarda durduğunu doğrular (ifade bulunamazsa durur),
  2. gözlenen ve sıfır tekrarlarının CV tohum kümelerini sayısal olarak kurar ve kesişimine bakar,
  3. kayıtlı tekrar başına değerlerden ve kayıtlı sıfır dağılımından özgün gözlenen değeri ve p'yi yeniden üretip
     kayıtlı results.csv ile karşılaştırır (okuma doğrulaması),
  4. tohumlar aynıysa eşleşik gözlenen değeri ve p'yi hesaplar; değilse hesaplamaz.
Okur:  analysis/03_*, 04b_*, 07_*, 07abc_*, 07de_*, 07f_* betikleri (metin olarak), results.csv, reps/ckpt/null dosyaları
Yazar: analysis/12_matched_perm_p_v1_2026-10-03_results.csv, _rapor.md   (var olanın üzerine yazılmaz)
"""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

A = Path(__file__).resolve().parent
STEM = "12_matched_perm_p_v1_2026-10-03"
OUT_CSV, OUT_MD = A / f"{STEM}_results.csv", A / f"{STEM}_rapor.md"
SEED = 20261001

S03, S04, S07 = "03_batch_negcontrol_v1_2026-10-01", "04b_leakage_v1_2026-10-01", "07_amplitude_decomp_v1_2026-10-02"
S7C, SDE, S7F = "07abc_source_decomp_v1_2026-10-02", "07de_transfer_longblock_v1_2026-10-02", "07f_longblock_transfer_v1_2026-10-02"


def src(stem):
    return (A / f"{stem}.py").read_text(encoding="utf-8")


def need(stem, *snippets):
    """Tohum ifadeleri kaynak betikte aynen bulunmalı."""
    s = src(stem)
    for sn in snippets:
        if sn not in s:
            sys.exit(f"DUR: {stem}.py içinde beklenen ifade yok: {sn!r}")
    assert f"SEED = {SEED}" in src(S03) and f"SEED = {SEED}" in src(S04) and f"SEED = {SEED}" in src(S07)


def jl(name):
    return pd.DataFrame([json.loads(l) for l in (A / name).read_text(encoding="utf-8").splitlines()])


# ---------------------------------------------------------------- tohum kümeleri (koddan)
# 07 ailesi (07, 07abc, 07de, 07f): gözlenen nested/transfer(..., SEED + r), r = 0..19;
#                                   sıfır   nested/transfer(..., SEED + 700000 + 50 * i + r), i = 0..199, r = 0..4
need(S07, "REPS, PERM_REPS, N_PERM = 20, 5, 200", "nested(X, y, groups, SEED + r)", "nested(X, yp, groups, SEED + 700000 + 50 * i + r) for r in range(PERM_REPS)")
need(S7C, "M7.nested(X, y, g, M7.SEED + r)", "M7.nested(X, yp, g, M7.SEED + 700000 + 50 * i + r)",
     "transfer(Xtr, ytr, gtr, ytr == 0, Xs2, gs2, M7.SEED + r)", "transfer(Xtr, yp, gtr, ytr == 0, Xs2, gs2, M7.SEED + 700000 + 50 * i + r)")
need(SDE, "M7C.transfer(Xtr, ytr, gtr, ytr == 0, Xs2, gs2, M7.SEED + r)", "M7C.transfer(Xtr, yp, gtr, ytr == 0, Xs2, gs2, M7.SEED + 700000 + 50 * i + r)",
     "M7.nested(X, y, g, M7.SEED + r)", "M7.nested(X, yp, g, M7.SEED + 700000 + 50 * i + r)")
need(S7F, "MDE.job_tr_real", "MDE.job_tr_null")
# 04-B: gözlenen run_simple/run_nested(..., SEED + r); sıfır N1: run_simple(..., SEED + 500000 + i) (permütasyon başına 1 tekrar),
#       sıfır P: run_nested(..., SEED + 700000 + 50 * i + r), r = 0..4
need(S04, "K_NAIVE, NAIVE_FOLDS, NAIVE_REPS = 100, 10, 10", "P_REPS, P_PERM_REPS, N_PERM = 20, 5, 200",
     "delayed(run_simple)(c, m, X, y, groups, SEED + r)", "delayed(run_nested)(m, X, y, groups, SEED + r)",
     'run_simple("N1", mname, X, yp, groups, SEED + 500000 + i)', "run_nested(mname, X, yp, groups, SEED + 700000 + 50 * i + r) for r in range(P_PERM_REPS)")
# 03: gözlenen run_a/run_b(..., reps, SEED, ...) -> dış kat random_state = SEED + r, r = 0..19;
#     sıfır (a) run_a(..., PERM_REPS, SEED + 100000 + 50 * i, ...), (b) run_b(..., PERM_REPS, SEED + 200000 + 50 * i, ...), r = 0..4
need(S03, "REPS, PERM_REPS, K_OUT, K_IN = 20, 5, 5, 5", "StratifiedKFold(K_OUT, shuffle=True, random_state=seed + r)",
     "run_a(Xa, ya, reps, SEED, nc, details)", "run_b(Xb, yb, (yb == 0), X2, reps, SEED, nc, details)",
     "run_a(Xa, rng.permutation(ya), PERM_REPS, SEED + 100000 + 50 * i, nc)", "run_b(Xb, rng.permutation(yb), (yb == 0), X2, PERM_REPS, SEED + 200000 + 50 * i, nc)")


def seeds_obs(n):
    return {SEED + r for r in range(n)}


def seeds_null(offset, n_perm, reps, step=50):
    return {SEED + offset + step * i + r for i in range(n_perm) for r in range(reps)}


OBS_EXPR = "SEED + r"
FAM07 = dict(n_obs=20, n_null=5, off=700000, step=50, null_expr="SEED + 700000 + 50*i + r")

# ---------------------------------------------------------------- kayıtlı değerler
r03 = pd.read_csv(A / f"{S03}_results.csv"); z03 = np.load(A / f"{S03}_perm_null.npz"); f03 = pd.read_csv(A / f"{S03}_transfer_folds.csv")
r04 = pd.read_csv(A / f"{S04}_results.csv").query("variant == 'primary'"); p04 = pd.read_csv(A / f"{S04}_reps.csv").query("variant == 'primary'")
z04 = np.load(A / f"{S04}_null.npz")
r07 = pd.read_csv(A / f"{S07}_results.csv").set_index("set"); p07 = pd.read_csv(A / f"{S07}_reps.csv"); z07 = np.load(A / f"{S07}_null.npz")
r7c = pd.read_csv(A / f"{S7C}_results.csv").set_index("set")
c_real, c_null = jl(f"{S7C}_ckpt_real.jsonl"), jl(f"{S7C}_ckpt_null.jsonl")
c_treal, c_tnull = jl(f"{S7C}_ckpt_tr_real.jsonl"), jl(f"{S7C}_ckpt_tr_null.jsonl")
rde = pd.read_csv(A / f"{SDE}_results.csv").set_index("set")
d_real, d_null = jl(f"{SDE}_ckpt_real.jsonl"), jl(f"{SDE}_ckpt_null.jsonl")
d_treal, d_tnull = jl(f"{SDE}_ckpt_tr_real.jsonl"), jl(f"{SDE}_ckpt_tr_null.jsonl")
r7f = pd.read_csv(A / f"{S7F}_results.csv").iloc[0]
f_treal, f_tnull = jl(f"{S7F}_ckpt_tr_real.jsonl"), jl(f"{S7F}_ckpt_tr_null.jsonl")


def rep_vals(df, col, **cond):
    """Tekrar sırasına göre tekrar başına gözlenen istatistik."""
    for k, v in cond.items():
        df = df[df[k] == v]
    return df.sort_values("rep")[col].to_numpy(float)


def tr_rep_vals(df, name):
    """Transfer: tekrar başına kat AUC'lerinin ortalaması (tekrar sırasıyla)."""
    d = df[df.set == name].sort_values("rep")
    return np.array([np.mean([f["auc_sg2_24"] for f in folds]) for folds in d.folds])


def nullv(df, col, name):
    return df[df.set == name].sort_values("perm")[col].to_numpy(float)


F03 = dict(n_obs=20, n_null=5, step=50)
TESTS = [  # ad, kaynak betik, tekrar başına gözlenen (ya da None), sıfır, kayıtlı gözlenen, kayıtlı p, alfa, tohum bilgisi
    ("03(a) sg vs sg2", S03, None, z03["null_a"], r03.iloc[0]["mean"], r03.iloc[0].p_perm, 0.025,
     dict(F03, off=100000, null_expr="SEED + 100000 + 50*i + r")),
    ("03(b) transfer", S03, f03.groupby("rep").transfer_auc.mean().sort_index().to_numpy(), z03["null_b"], r03.iloc[2]["mean"], r03.iloc[2].p_perm, 0.025,
     dict(F03, off=200000, null_expr="SEED + 200000 + 50*i + r")),
    ("04-B N1 RF", S04, rep_vals(p04, "row_auc", cell="N1", model="RF"), z04["N1_RF__row_auc"], None, None, 0.05,
     dict(n_obs=10, n_null=1, off=500000, step=1, null_expr="SEED + 500000 + i")),
    ("04-B N1 SVM", S04, rep_vals(p04, "row_auc", cell="N1", model="SVM"), z04["N1_SVM__row_auc"], None, None, 0.05,
     dict(n_obs=10, n_null=1, off=500000, step=1, null_expr="SEED + 500000 + i")),
    ("04-B P SVM", S04, rep_vals(p04, "subj_auc", cell="P", model="SVM"), z04["P_SVM__subj_auc"], None, None, 0.05, FAM07),
    ("07 A", S07, rep_vals(p07, "subj_auc", set="A_log_abs"), z07["A_log_abs"], r07.loc["A_log_abs", "subj_auc"], r07.loc["A_log_abs", "p_perm"], 0.05, FAM07),
    ("07 B", S07, rep_vals(p07, "subj_auc", set="B_relative"), z07["B_relative"], r07.loc["B_relative", "subj_auc"], r07.loc["B_relative", "p_perm"], 0.05, FAM07),
    ("07a closed", S7C, rep_vals(c_real, "subj_auc", set="07a_closed"), nullv(c_null, "subj_auc", "07a_closed"), r7c.loc["07a_closed", "auc"], r7c.loc["07a_closed", "p_perm"], 0.05, FAM07),
    ("07a open", S7C, rep_vals(c_real, "subj_auc", set="07a_open"), nullv(c_null, "subj_auc", "07a_open"), r7c.loc["07a_open", "auc"], r7c.loc["07a_open", "p_perm"], 0.05, FAM07),
    ("07b", S7C, rep_vals(c_real, "subj_auc", set="07b_closed_noC"), nullv(c_null, "subj_auc", "07b_closed_noC"), r7c.loc["07b_closed_noC", "auc"], r7c.loc["07b_closed_noC", "p_perm"], 0.05, FAM07),
    ("07c", S7C, tr_rep_vals(c_treal, "07c_transfer"), nullv(c_tnull, "auc_sg2_24", "07c_transfer"), r7c.loc["07c_transfer", "auc"], r7c.loc["07c_transfer", "p_perm"], 0.05, FAM07),
    ("07d A all", SDE, tr_rep_vals(d_treal, "07d_A_all"), nullv(d_tnull, "auc_sg2_24", "07d_A_all"), rde.loc["07d_A_all", "auc"], rde.loc["07d_A_all", "p_perm"], 0.05, FAM07),
    ("07d B all", SDE, tr_rep_vals(d_treal, "07d_B_all"), nullv(d_tnull, "auc_sg2_24", "07d_B_all"), rde.loc["07d_B_all", "auc"], rde.loc["07d_B_all", "p_perm"], 0.05, FAM07),
    ("07d B open", SDE, tr_rep_vals(d_treal, "07d_B_open"), nullv(d_tnull, "auc_sg2_24", "07d_B_open"), rde.loc["07d_B_open", "auc"], rde.loc["07d_B_open", "p_perm"], 0.05, FAM07),
    ("07e", SDE, rep_vals(d_real, "subj_auc", set="07e_longblock"), nullv(d_null, "subj_auc", "07e_longblock"), rde.loc["07e_longblock", "auc"], rde.loc["07e_longblock", "p_perm"], 0.05, FAM07),
    ("07f", S7F, tr_rep_vals(f_treal, "07f_longblock_transfer"), nullv(f_tnull, "auc_sg2_24", "07f_longblock_transfer"), r7f.auc, r7f.p_perm, 0.05, FAM07),
]
for cell, model, metric in [("N1", "RF", "row_auc"), ("N1", "SVM", "row_auc"), ("P", "SVM", "subj_auc")]:   # 04-B kayıtlı değerler
    rr = r04[(r04.cell == cell) & (r04.model == model)].iloc[0]
    assert rr.null_metric == metric
    i = [t[0] for t in TESTS].index(f"04-B {cell} {model}")
    TESTS[i] = TESTS[i][:4] + (rr[metric], rr.p_perm) + TESTS[i][6:]

rows = []
for name, stem, obs_reps, null, obs_saved, p_saved, alpha, sd in TESTS:
    N = len(null)
    so, sn = seeds_obs(sd["n_obs"]), seeds_null(sd["off"], N, sd["n_null"], sd["step"])
    n_common = len(so & sn)
    # null tekrarlarının hepsi gözlenen analizin ilk n_null tekrarının tohumları mı?
    seeds_same = sn == seeds_obs(sd["n_null"])
    row = dict(test=name, script=f"{stem}.py", n_perm=N, reps_observed=sd["n_obs"], reps_null_per_perm=sd["n_null"],
               seed_observed=OBS_EXPR, seed_null=sd["null_expr"], n_common_seeds=n_common, seeds_same=bool(seeds_same),
               per_repeat_observed_saved=obs_reps is not None)
    if obs_reps is not None:
        assert len(obs_reps) == sd["n_obs"], (name, len(obs_reps))
        obs = float(np.mean(obs_reps)); p = (np.sum(null >= obs) + 1) / (N + 1)
        assert abs(obs - obs_saved) < 1e-9 and abs(p - p_saved) < 1e-12, (name, obs, obs_saved, p, p_saved)   # okuma doğrulaması
    else:
        obs, p = float(obs_saved), float((np.sum(null >= obs_saved) + 1) / (N + 1))
        assert abs(p - p_saved) < 1e-12, (name, p, p_saved)
    row.update(observed_original=obs, p_original=float(p), alpha=alpha, decision_original="p < alpha" if p < alpha else "p >= alpha")
    if seeds_same and obs_reps is not None:
        om = float(np.mean(obs_reps[:sd["n_null"]])); pm = float((np.sum(null >= om) + 1) / (N + 1))
        row.update(observed_matched=om, p_matched=pm, decision_matched="p < alpha" if pm < alpha else "p >= alpha",
                   same_decision=bool((pm < alpha) == (p < alpha)), reason_not_computed="")
    else:
        why = []
        if not seeds_same:
            why.append(f"CV seeds differ: observed {OBS_EXPR} (r = 0..{sd['n_obs'] - 1}), null {sd['null_expr']}; {n_common} common seeds")
        if obs_reps is None:
            why.append("per-repeat observed values not saved (only the mean and percentiles)")
        row.update(observed_matched=np.nan, p_matched=np.nan, decision_matched="not computed", same_decision="n/a",
                   reason_not_computed="; ".join(why))
    rows.append(row)
res = pd.DataFrame(rows)

for p in (OUT_CSV, OUT_MD):
    if p.exists():
        sys.exit(f"DUR: {p.name} zaten var; üzerine yazılmaz.")
res.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

n_done = int((res.decision_matched != "not computed").sum())
changed = res[res.same_decision == False]   # noqa: E712
md = ["# K2 eşleştirilmiş permütasyon p değerleri (12 v1, 2026-10-03)", "",
      "Tanım: CLAUDE.md, \"2026-10-03 Gönderim öncesi kontroller\". Yeni model eğitimi yok; yalnız kayıtlı değerler okundu.", "",
      "## Kararı değişen testler", "",
      ("Yok: " if changed.empty else "") + (f"eşleşik p {n_done} testte hesaplanabildi." if n_done else
                                           f"eşleşik p {len(res)} testin HİÇBİRİNDE hesaplanamadı, dolayısıyla karar karşılaştırması da yapılamadı."), ""]
md += [f"- {r.test}: özgün p {r.p_original:.4f}, eşleşik p {r.p_matched:.4f} (alfa {r.alpha})" for r in changed.itertuples()]
md += ["## Bulgu", "",
       f"{len(res)} testin {int((~res.seeds_same).sum())}'sinde sıfır dağılımının CV tohumları gözlenen analizin tohumlarıyla AYNI DEĞİL "
       f"(ortak tohum sayısı: en çok {int(res.n_common_seeds.max())}). Sıfır dağılımında yalnız etiketler değil, katlama tohumları da farklı:",
       "", "- Gözlenen: SEED + r (r = 0..19; 04-B N1'de 0..9).",
       "- Sıfır, 07 ailesi ve 04-B P: SEED + 700000 + 50·i + r (i = permütasyon, r = 0..4).",
       "- Sıfır, 04-B N1: SEED + 500000 + i (permütasyon başına 1 tekrar).",
       "- Sıfır, 03(a) / 03(b): SEED + 100000 + 50·i + r / SEED + 200000 + 50·i + r (r = 0..4).",
       "- 03(a) için ayrıca tekrar başına gözlenen AUC kayıtlı değil (yalnız ortalama ve yüzdelikler).", "",
       "K2 tanımındaki kural gereği (\"tohumlar farklıysa hesaplama\") eşleşik gözlenen değer ve eşleşik p hesaplanmadı.",
       "Kayıtlı değerlerle \"aynı tohumlar\" koşulu sağlanamaz; bunu sağlamak gözlenen modelin sıfır tohumlarıyla (ya da sıfırın gözlenen "
       "tohumlarıyla) yeniden eğitilmesini gerektirir, bu da K2 tanımının dışındadır (yeni model eğitimi yok).", "",
       "Okuma doğrulaması: her testte kayıtlı tekrar değerlerinden ve kayıtlı sıfır dağılımından özgün gözlenen değer ve özgün p yeniden "
       "üretildi; hepsi results.csv ile aynı (gözlenen |fark| < 1e-9, p |fark| < 1e-12).", "",
       "## Testler", "",
       "| Test | N perm. | Tekrar (gözlenen / sıfır) | Tohumlar aynı mı | Gözlenen (özgün) | p (özgün) | Alfa | Gözlenen (eşleşik) | p (eşleşik) | Karar aynı mı |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for r in res.itertuples():
    md.append(f"| {r.test} | {r.n_perm} | {r.reps_observed} / {r.reps_null_per_perm} | {'evet' if r.seeds_same else 'hayır'} | {r.observed_original:.3f} | "
              f"{r.p_original:.4f} | {r.alpha} | {'–' if pd.isna(r.observed_matched) else f'{r.observed_matched:.3f}'} | "
              f"{'–' if pd.isna(r.p_matched) else f'{r.p_matched:.4f}'} | {r.same_decision if isinstance(r.same_decision, str) else ('evet' if r.same_decision else 'HAYIR')} |")
OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
