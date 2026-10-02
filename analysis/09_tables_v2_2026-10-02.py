"""09 v2 - Tablo S-n v2 (07f ve 07g satırları; DENETIM_RAPORU_3 F6) ve Tablo S4 v1 (keşifsel analizler 07–07f, GD, 07g GA'ları).

Tablo 1 değişmedi (09 v1). Tablo S-n v1'in satırları aynen korunur; 07f satırı eklenir, 07c/07d satırı açıklanır.
Tablo S4: kayıtlı sonuç CSV'lerinden (07, 07abc, 07de, 07f) ve 07g GA'larından; yeni hesap yok.
Okur:  analysis/09_tables_v1_2026-10-02_TableSn.csv, 07*_results.csv, 07g_auc_ci_v1_2026-10-02_results.csv
Yazar: analysis/09_tables_v2_2026-10-02_{TableSn,TableS4}.{csv,md}
"""
from pathlib import Path
import pandas as pd

A = Path(__file__).resolve().parent
STEM = "09_tables_v2_2026-10-02"

# --- Tablo S-n v2 ---
sn = pd.read_csv(A / "09_tables_v1_2026-10-02_TableSn.csv")
sn.loc[sn.Analysis == "07c / 07d transfer test set", "Data segment"] = "same epochs as training (07c: eyes closed; 07d: all / eyes open)"
add = pd.DataFrame([
    ("07f transfer test set", "long eyes-closed block, 465 s (4 × 116.25 s), as 07e", 0, 0, 24, 24,
     "sub-1084sg2 has no long block (data file missing); training set as 07e (cg 55, sg 45)"),
    ("07g 95% CIs (no new model)", "as 07–07f", 55, 45, 24, 124,
     "source models: cg 55 + sg 45; transfer: held-out cg (55) vs sg2 24; descriptive sensitivity without sub-1105sg2 and sub-1114sg2 (sg2 22)"),
], columns=sn.columns)
sn = pd.concat([sn, add], ignore_index=True)
sn.to_csv(A / f"{STEM}_TableSn.csv", index=False, encoding="utf-8-sig")
md = ["# Table S-n. Sample used in each analysis (v2)", "", "| " + " | ".join(sn.columns) + " |", "|" + "---|" * len(sn.columns)]
md += ["| " + " | ".join(str(v) for v in r) + " |" for r in sn.itertuples(index=False)]
(A / f"{STEM}_TableSn.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# --- Tablo S4 ---
ci = pd.read_csv(A / "07g_auc_ci_v1_2026-10-02_results.csv").set_index("set")
r7 = pd.read_csv(A / "07_amplitude_decomp_v1_2026-10-02_results.csv").set_index("set")
rabc = pd.read_csv(A / "07abc_source_decomp_v1_2026-10-02_results.csv").set_index("set")
rde = pd.read_csv(A / "07de_transfer_longblock_v1_2026-10-02_results.csv").set_index("set")
rf = pd.read_csv(A / "07f_longblock_transfer_v1_2026-10-02_results.csv").set_index("set")


def src_row(lab, data, r, auc, key):
    c = ci.loc[key]
    return dict(Analysis=lab, Data=data, Comparison="sg vs cg (n = 45 / 55)", AUC=auc, AUC_rep_range=f"{r.auc_lo:.3f}–{r.auc_hi:.3f}",
                AUC_meanscore=c.auc_meanscore, CI95=f"{c.ci_low:.3f}–{c.ci_high:.3f}", null_mean=r.null_mean, p=r.p_perm,
                BA=r.subj_ba, GD=r.GD, Sen=r.Sensitivity, Spe=r.Specificity, F1=r.F1, sg2_offender_rate=None, AUC_excl_atypical=None)


def tr_row(lab, data, r, key):
    c = ci.loc[key]
    return dict(Analysis=lab, Data=data, Comparison="held-out cg vs sg2 (n = 55 / 24), within fold", AUC=r.auc,
                AUC_rep_range=f"{r.auc_p2_5:.3f}–{r.auc_p97_5:.3f}", AUC_meanscore=None, CI95=f"{c.ci_low:.3f}–{c.ci_high:.3f}",
                null_mean=r.null_mean, p=r.p_perm, BA=None, GD=None, Sen=None, Spe=None, F1=None,
                sg2_offender_rate=r.frac_sg2_offender_24, AUC_excl_atypical=c.auc_excl_atypical_22)


for d in (r7,):
    d["auc"] = d.subj_auc; d["auc_lo"] = d.subj_auc_p2_5; d["auc_hi"] = d.subj_auc_p97_5
for d in (rabc, rde):
    d["auc_lo"] = d.auc_p2_5; d["auc_hi"] = d.auc_p97_5
rows = [
    src_row("07 A", "log10 absolute band power, all epochs", r7.loc["A_log_abs"], r7.loc["A_log_abs"].auc, "07_A_log_abs"),
    src_row("07 B", "relative band power, all epochs", r7.loc["B_relative"], r7.loc["B_relative"].auc, "07_B_relative"),
    src_row("07a closed", "B, eyes-closed epochs (2 × 50 s)", rabc.loc["07a_closed"], rabc.loc["07a_closed"].auc, "07a_closed"),
    src_row("07a open", "B, eyes-open epochs (2 × 50 s)", rabc.loc["07a_open"], rabc.loc["07a_open"].auc, "07a_open"),
    src_row("07b", "B, eyes closed, C block removed", rabc.loc["07b_closed_noC"], rabc.loc["07b_closed_noC"].auc, "07b_closed_noC"),
    src_row("07e", "B, long eyes-closed block (4 × 116.25 s)", rde.loc["07e_longblock"], rde.loc["07e_longblock"].auc, "07e_longblock"),
    tr_row("07c", "B, eyes-closed epochs", rabc.loc["07c_transfer"], "07c_B_closed"),
    tr_row("07d A all", "A, all epochs", rde.loc["07d_A_all"], "07d_A_all"),
    tr_row("07d B all", "B, all epochs", rde.loc["07d_B_all"], "07d_B_all"),
    tr_row("07d B open", "B, eyes-open epochs", rde.loc["07d_B_open"], "07d_B_open"),
    tr_row("07f", "B, long eyes-closed block", rf.loc["07f_longblock_transfer"], "07f_B_longblock"),
]
s4 = pd.DataFrame(rows)
s4.to_csv(A / f"{STEM}_TableS4.csv", index=False, encoding="utf-8-sig")

f3 = lambda v: "–" if v is None or pd.isna(v) else f"{v:.3f}"
fp = lambda v: "≤ 0.005" if v <= 1 / 201 + 1e-12 else (f"{v:.4f}" if v < 0.1 else f"{v:.3f}")
md = ["# Table S4. Exploratory analyses 07–07f: subject-level AUC, 95% CI (07g), permutation p and Golden Distance", "",
      "All exploratory; p values unadjusted (D9); 200 permutations (smallest attainable p = 1/201 ≈ 0.005). "
      "Pipeline: StandardScaler → SelectKBest(f_classif) → RBF SVM, nested StratifiedGroupKFold (outer 5 × 20 repeats).",
      "Source models (sg vs cg): AUC = mean over 20 repeats (as reported); 95% CI = class-stratified subject bootstrap (2000) of the AUC "
      "computed from subject scores averaged over the 20 repeats (AUC_meanscore; the same method as 06). Averaging scores raises the AUC, "
      "so the CI is centred on AUC_meanscore, not on the repeat mean.",
      "Transfer models (held-out cg vs sg2, within fold): AUC = mean of 100 fold AUCs; 95% CI = weighted subject bootstrap (multinomial "
      "weights for cg 55 and sg2 24; 2000). CIs cover subject sampling only, not model-training variability. "
      "Excl. atypical = descriptive transfer AUC without sub-1105sg2 and sub-1114sg2 (no retraining). "
      "sg2 offender rate depends on the threshold and cannot be interpreted alone (E1).", "",
      "| Analysis | Data | Comparison | AUC (repeat mean) | Repeat 2.5–97.5 | AUC (mean score) | 95% CI | Null mean | p | BA | GD ↓ | Sen | Spe | F1 | sg2 \"offender\" rate | AUC excl. atypical sg2 |",
      "|" + "---|" * 16]
for r in s4.itertuples(index=False):
    md.append("| " + " | ".join([r.Analysis, r.Data, r.Comparison, f3(r.AUC), r.AUC_rep_range, f3(r.AUC_meanscore), r.CI95,
                                   f3(r.null_mean), fp(r.p), f3(r.BA), f3(r.GD), f3(r.Sen), f3(r.Spe), f3(r.F1),
                                   f3(r.sg2_offender_rate), f3(r.AUC_excl_atypical)]) + " |")
(A / f"{STEM}_TableS4.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
