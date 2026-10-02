"""08 - Makale şekilleri 1–5 (salt okuma; yalnız analysis/ çıktılarından). 300 dpi PNG + PDF -> analysis/figures/.

Fig 1 sızıntı (04-B + GD) | Fig 2 keşifsel kademe ve transfer (07, 07a–c) | Fig 3 birincil test (05)
Fig 4 önceden belirlenmiş özniteliklerle ayrışma (06, 03) | Fig 5 kohort (01, 04-A)
"""
from pathlib import Path
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Patch
from matplotlib.lines import Line2D

A = Path(__file__).resolve().parent; FIG = A / "figures"; FIG.mkdir(exist_ok=True)
INK, INK2, MUTED, GRID, NULLC = "#0b0b0b", "#52514e", "#898781", "#e8e7e3", "#c9c8c2"
GROUP = {"cg": "#2a78d6", "sg": "#eb6834", "sg2": "#1baf7a"}
MODEL = {"SVM": "#4a3aa7", "RF": "#e87ba4"}
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "pdf.fonttype": 42, "font.family": "DejaVu Sans"})


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig); print("yazıldı:", name)


def panel(ax, s):
    ax.text(-0.12, 1.06, s, transform=ax.transAxes, fontsize=10, fontweight="bold", color=INK, va="bottom")


def chance(ax, horiz=True):
    (ax.axhline if horiz else ax.axvline)(0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=0)


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines()]


# ---------------------------------------------------------------- Fig 1
def fig1():
    r = pd.read_csv(A / "04b_leakage_v1_2026-10-01_results.csv").query("variant=='primary'")
    g = pd.read_csv(A / "04b_leakage_gd_v1_2026-10-02_reps.csv").query("variant=='primary'")
    z = np.load(A / "04b_leakage_v1_2026-10-01_null.npz")
    cells = ["N1", "N2", "N3", "N4", "P"]
    sub = {"N1": "row CV\nglobal sel.", "N2": "row CV\nsel. in CV", "N3": "subject CV\nglobal sel.",
           "N4": "subject CV\nsel. in CV", "P": "subject CV\nnested"}
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1.35, 1, 1.1], wspace=0.45))
    x = np.arange(len(cells))
    for j, m in enumerate(["SVM", "RF"]):
        d = r[r.model == m].set_index("cell").loc[cells]
        xx = x + (j - 0.5) * 0.28
        ax[0].errorbar(xx, d.subj_auc, yerr=[d.subj_auc - d.subj_auc_p2_5, d.subj_auc_p97_5 - d.subj_auc], fmt="o",
                       ms=5, color=MODEL[m], ecolor=MODEL[m], elinewidth=1.5, capsize=0, label=m, zorder=3)
        gd = g[g.model == m].groupby("cell").subj_GD
        ax[2].errorbar(xx, gd.mean().loc[cells], yerr=[gd.mean().loc[cells] - gd.quantile(.025).loc[cells],
                       gd.quantile(.975).loc[cells] - gd.mean().loc[cells]], fmt="s", ms=4.5, color=MODEL[m],
                       ecolor=MODEL[m], elinewidth=1.5, capsize=0, label=m, zorder=3)
    for a, yl, tt in [(ax[0], "Subject-level ROC-AUC", "Accuracy by pipeline"), (ax[2], "Golden Distance (lower = better)", "Golden Distance")]:
        a.set_xticks(x); a.set_xticklabels(cells)
        a.set_ylabel(yl); a.set_title(tt, loc="left", color=INK); a.grid(axis="y", color=GRID, lw=0.6)
        for x0, x1, lab in [(-0.3, 1.3, "row CV"), (1.7, 4.3, "subject CV")]:
            a.annotate("", xy=(x0, -0.16), xytext=(x1, -0.16), xycoords=("data", "axes fraction"),
                       arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
            a.text((x0 + x1) / 2, -0.2, lab, transform=a.get_xaxis_transform(), ha="center", va="top", fontsize=6.5, color=INK2)
    chance(ax[0]); ax[0].set_ylim(0.4, 1.0); ax[0].legend(loc="lower left", fontsize=7)
    ax[0].axvspan(-0.5, 1.5, color="#f6efe9", zorder=0); ax[0].text(0.5, 0.97, "leaky", ha="center", va="top", fontsize=7, color=INK2)
    ax[2].axvspan(-0.5, 1.5, color="#f6efe9", zorder=0); ax[2].set_ylim(0.3, 0.85)
    # (b) karıştırılmış etiket
    items = [("N1 SVM", "N1_SVM", r.query("cell=='N1' and model=='SVM'").subj_auc.iloc[0], MODEL["SVM"]),
             ("N1 RF", "N1_RF", r.query("cell=='N1' and model=='RF'").subj_auc.iloc[0], MODEL["RF"]),
             ("P SVM", "P_SVM", r.query("cell=='P' and model=='SVM'").subj_auc.iloc[0], MODEL["SVM"])]
    for i, (lab, k, obs, c) in enumerate(items):
        nv = z[f"{k}__subj_auc"]
        vp = ax[1].violinplot(nv, positions=[i], widths=0.7, showextrema=False)
        for b in vp["bodies"]: b.set_facecolor(NULLC); b.set_edgecolor("none"); b.set_alpha(1)
        ax[1].plot([i - 0.25, i + 0.25], [np.median(nv)] * 2, color=INK2, lw=1)
        ax[1].scatter([i], [obs], marker="D", s=30, color=c, zorder=3, edgecolor="white", lw=0.8)
    ax[1].set_xticks(range(3)); ax[1].set_xticklabels([i[0] for i in items]); chance(ax[1]); ax[1].set_ylim(0.3, 1.0)
    ax[1].set_ylabel("Subject-level ROC-AUC"); ax[1].set_title("Shuffled labels (200×)", loc="left", color=INK)
    ax[1].legend(handles=[Patch(color=NULLC, label="null (shuffled)"), Line2D([], [], marker="D", ls="", color=INK2, label="observed")],
                 loc="lower left", fontsize=7)
    ax[1].grid(axis="y", color=GRID, lw=0.6)
    for a, s in zip(ax, "abc"): panel(a, s)
    save(fig, "Fig1_leakage")


# ---------------------------------------------------------------- Fig 2
def fig2():
    r7 = pd.read_csv(A / "07_amplitude_decomp_v1_2026-10-02_results.csv").set_index("set")
    rep7 = pd.read_csv(A / "07_amplitude_decomp_v1_2026-10-02_reps.csv")
    real = pd.DataFrame(jl(A / "07abc_source_decomp_v1_2026-10-02_ckpt_real.jsonl"))
    null = pd.DataFrame(jl(A / "07abc_source_decomp_v1_2026-10-02_ckpt_null.jsonl"))
    treal = pd.DataFrame(jl(A / "07abc_source_decomp_v1_2026-10-02_ckpt_tr_real.jsonl"))
    tnull = pd.DataFrame(jl(A / "07abc_source_decomp_v1_2026-10-02_ckpt_tr_null.jsonl"))
    r7c = pd.read_csv(A / "07abc_source_decomp_v1_2026-10-02_results.csv").set_index("set")
    z7 = np.load(A / "07_amplitude_decomp_v1_2026-10-02_null.npz")
    items = [("Absolute\nall epochs", rep7.query("set=='A_log_abs'").subj_auc, z7["A_log_abs"], r7.loc["A_log_abs", "p_perm"]),
             ("Relative\nall epochs", rep7.query("set=='B_relative'").subj_auc, z7["B_relative"], r7.loc["B_relative", "p_perm"]),
             ("Relative\neyes open", real.query("set=='07a_open'").subj_auc, null.query("set=='07a_open'").subj_auc, r7c.loc["07a_open", "p_perm"]),
             ("Relative\neyes closed", real.query("set=='07a_closed'").subj_auc, null.query("set=='07a_closed'").subj_auc, r7c.loc["07a_closed", "p_perm"]),
             ("Rel. closed,\nno frontal", real.query("set=='07b_closed_noC'").subj_auc, null.query("set=='07b_closed_noC'").subj_auc, r7c.loc["07b_closed_noC", "p_perm"]),
             ("Transfer\ncg vs sg2", treal.auc_sg2_24, tnull.auc_sg2_24, r7c.loc["07c_transfer", "p_perm"])]
    fig = plt.figure(figsize=(7.2, 2.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.1, 1], wspace=0.35)
    ax = fig.add_subplot(gs[0])
    ax.axhspan(0.60, 0.65, color="#fdf1d6", zorder=0)
    ax.text(-0.55, 0.625, "undefined decision-rule gap (0.60–0.65)", fontsize=6, color=INK2, va="center", ha="left", zorder=4)
    for i, (lab, rv, nv, p) in enumerate(items):
        lo, hi = np.percentile(nv, [2.5, 97.5])
        ax.add_patch(plt.Rectangle((i - 0.22, lo), 0.44, hi - lo, color=NULLC, zorder=1, lw=0))
        m = np.mean(rv); a, b = np.percentile(rv, [2.5, 97.5])
        ax.errorbar([i], [m], yerr=[[m - a], [b - m]], fmt="o", ms=5, color=INK, elinewidth=1.5, capsize=0, zorder=3)
        ax.text(i, b + 0.012, f"{m:.3f}\np={p:.3f}", ha="center", va="bottom", fontsize=6.3, color=INK2)
    ax.axvline(1.5, color=GRID, lw=1)
    ax.text(0.5, 0.35, "07", ha="center", fontsize=7, color=MUTED); ax.text(3.5, 0.35, "07a–c (exploratory)", ha="center", fontsize=7, color=MUTED)
    chance(ax); ax.set_ylim(0.32, 0.90); ax.set_xlim(-0.6, 5.6)
    ax.set_xticks(range(len(items))); ax.set_xticklabels([i[0] for i in items], fontsize=6.3)
    ax.set_ylabel("Subject-level ROC-AUC (sg vs cg)"); ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_title("Separation is graded and does not transfer to sg2", loc="left", color=INK)
    ax.legend(handles=[Line2D([], [], marker="o", ls="-", color=INK, label="observed (CV-repeat 2.5–97.5%)"),
                       Patch(color=NULLC, label="shuffled-label null 95%")], loc="upper right", fontsize=6.3)
    panel(ax, "a")
    # (b) grup medyanları
    d = pd.read_csv(A / "07abc_source_decomp_v1_2026-10-02_descriptive.csv")
    gs2 = gs[1].subgridspec(2, 1, hspace=0.9)
    for k, (meas, tt) in enumerate([("rel_delta_frontalC", "Relative delta, frontal (eyes closed)"),
                                    ("rel_alpha_Ablock", "Relative alpha, posterior (eyes closed)")]):
        a = fig.add_subplot(gs2[k])
        for j, (grp, lab) in enumerate([("cg", "cg"), ("sg", "sg"), ("sg2_24", "sg2")]):
            row = d[(d.group == grp) & (d.measure == meas)].iloc[0]
            a.errorbar([row["median"]], [j], xerr=[[row["median"] - row.q1], [row.q3 - row["median"]]], fmt="o", ms=5,
                       color=GROUP[lab], elinewidth=1.5, capsize=0)
        a.set_yticks(range(3)); a.set_yticklabels(["cg", "sg", "sg2"]); a.set_ylim(-0.6, 2.6); a.invert_yaxis()
        a.set_title(tt, loc="left", fontsize=7.5, color=INK); a.set_xlabel("median [IQR]", fontsize=7); a.grid(axis="x", color=GRID, lw=0.6)
        if k == 0: panel(a, "b")
    save(fig, "Fig2_exploratory_cascade")


# ---------------------------------------------------------------- Fig 3
def fig3():
    s = pd.read_csv(A / "05_alpha_reactivity_v1_2026-10-02_subjects.csv"); s = s[s.n_epochs == 4]
    r = pd.read_csv(A / "05_alpha_reactivity_v1_2026-10-02_results.csv")
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1.3, 0.9, 1], wspace=0.95))
    rng = np.random.default_rng(1)
    for i, grp in enumerate(["cg", "sg", "sg2"]):
        v = s[s.group == grp].ARI.values
        bp = ax[0].boxplot(v, positions=[i], widths=0.45, showfliers=False, patch_artist=True,
                           medianprops=dict(color=INK, lw=1.4), whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                           boxprops=dict(facecolor="white", edgecolor=MUTED))
        ax[0].scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=9, color=GROUP[grp], alpha=0.8, lw=0, zorder=3)
    ax[0].set_xticks(range(3)); ax[0].set_xticklabels([f"cg\n(n={(s.group == 'cg').sum()})", f"sg\n(n={(s.group == 'sg').sum()})",
                                                        f"sg2\n(n={(s.group == 'sg2').sum()})"])
    ax[0].set_ylabel("Alpha reactivity index (C−O)/(C+O)"); ax[0].grid(axis="y", color=GRID, lw=0.6)
    p = r.iloc[0].p
    ax[0].set_title(f"Primary test (p = {p:.3f})", loc="left", color=INK)
    # (b) rank-biserial
    rows = [("n = 136\nprimary", r.iloc[0]), ("n = 140\nsensitivity", r.iloc[1])]
    for j, (lab, rr) in enumerate(rows):
        ax[1].errorbar([rr.rank_biserial], [j], xerr=[[rr.rank_biserial - rr.rb_ci_low], [rr.rb_ci_high - rr.rank_biserial]],
                       fmt="o", ms=5, color=INK, elinewidth=1.5, capsize=0, mfc=INK if j == 0 else "white")
    ax[1].axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 3))); ax[1].set_yticks(range(2)); ax[1].set_yticklabels([x[0] for x in rows], fontsize=7)
    ax[1].set_ylim(-0.6, 1.6); ax[1].invert_yaxis(); ax[1].set_xlim(-0.45, 0.3)
    ax[1].set_xlabel("Rank-biserial r (offender > cg)"); ax[1].set_title("Effect size, 95% CI", loc="left", color=INK); ax[1].grid(axis="x", color=GRID, lw=0.6)
    # (c) ARI farkı
    ols = r[r.analysis.str.startswith("OLS ARI")].iloc[0]
    rows = [("HL, n = 136", r.iloc[0].HL_shift, r.iloc[0].HL_ci_low, r.iloc[0].HL_ci_high),
            ("HL, n = 140", r.iloc[1].HL_shift, r.iloc[1].HL_ci_low, r.iloc[1].HL_ci_high),
            ("OLS + age\n+ EMG", ols.coef_offender, ols.ci_low, ols.ci_high)]
    for j, (lab, m, lo, hi) in enumerate(rows):
        ax[2].errorbar([m], [j], xerr=[[m - lo], [hi - m]], fmt="o", ms=5, color=INK, elinewidth=1.5, capsize=0, mfc=INK if j == 0 else "white")
    ax[2].axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 3))); ax[2].set_yticks(range(3)); ax[2].set_yticklabels([x[0] for x in rows], fontsize=7)
    ax[2].set_ylim(-0.6, 2.6); ax[2].invert_yaxis(); ax[2].set_xlabel("Difference in ARI (offender − cg)")
    ax[2].set_title("Group difference, 95% CI", loc="left", color=INK); ax[2].grid(axis="x", color=GRID, lw=0.6)
    for a, t in zip(ax, "abc"): panel(a, t)
    save(fig, "Fig3_primary_alpha_reactivity")


# ---------------------------------------------------------------- Fig 4
def fig4():
    r6 = pd.read_csv(A / "06_null_quantification_v1_2026-10-02_results.csv").iloc[0]
    r3 = pd.read_csv(A / "03_batch_negcontrol_v1_2026-10-01_results.csv")
    get = lambda t: r3[r3.test == t].iloc[0]
    rows = [("Offenders vs cg (06)\nbootstrap 95% CI", r6.auc_mean_prob, r6.boot_ci_low, r6.boot_ci_high, "ci"),
            ("Offenders vs cg (06)\nCV-repeat range", r6.auc_rep_mean, r6.auc_rep_p2_5, r6.auc_rep_p97_5, "rep"),
            ("sg vs cg (03)", get("(b) referans: sg vs cg")["mean"], get("(b) referans: sg vs cg").p2_5, get("(b) referans: sg vs cg").p97_5, "rep"),
            ("sg vs sg2 (03)\np = 0.053, α = 0.025", get("(a) sg vs sg2")["mean"], get("(a) sg vs sg2").p2_5, get("(a) sg vs sg2").p97_5, "rep"),
            ("Transfer: held-out cg\nvs sg2 (03)", r3.iloc[2]["mean"], r3.iloc[2].p2_5, r3.iloc[2].p97_5, "rep")]
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    U = r6.boot_ci_high
    ax.axvspan(U, 1.0, color="#eef3fb", zorder=0)
    ax.text(0.985, 1.5, f"AUC > {U:.2f}\nexcluded (95%)\nfor offenders vs cg", ha="right", va="center", fontsize=6.5, color=INK2)
    for j, (lab, m, lo, hi, kind) in enumerate(rows):
        ax.errorbar([m], [j], xerr=[[m - lo], [hi - m]], fmt="o", ms=5, color=INK, elinewidth=2.0 if kind == "ci" else 1.0,
                    capsize=0, mfc=INK if kind == "ci" else "white", zorder=3)
        ax.text(hi + 0.01, j, f"{m:.3f}", va="center", fontsize=6.5, color=INK2)
    chance(ax, horiz=False)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=6.8); ax.set_ylim(-0.6, len(rows) - 0.4); ax.invert_yaxis()
    ax.set_xlim(0.25, 1.0); ax.set_xlabel("ROC-AUC (pre-specified 14 spectral features, long eyes-closed block)")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.legend(handles=[Line2D([], [], marker="o", color=INK, lw=2, label="95% CI (subject bootstrap)"),
                       Line2D([], [], marker="o", color=INK, mfc="white", lw=1, label="CV-repetition 2.5–97.5% (not a CI)")],
              loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=2, fontsize=6.3)
    save(fig, "Fig4_prespecified_null")


# ---------------------------------------------------------------- Fig 5
def fig5():
    aud = pd.read_csv(A / "01_data_audit_v2_2026-10-01.csv").query("file=='preprocessed'")
    aud["dt"] = pd.to_datetime(aud.rec_datetime)
    fig = plt.figure(figsize=(7.2, 3.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.45, 1], height_ratios=[1, 1], hspace=0.55, wspace=0.25)
    # (a) akış
    ax = fig.add_subplot(gs[:, 0]); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    def box(x, y, w, h, txt, fc="white"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=MUTED, lw=0.9))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=5.9, color=INK)
    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.9))
    box(1.0, 8.4, 6.0, 1.3, "OpenNeuro ds006923: 140 participants\ncg 66 · sg 49 · sg2 25")
    box(7.3, 6.5, 2.6, 1.9, "Excluded (5)\n4 sg: ~157 s,\nno long block\n1 sg2: file missing", fc="#f6efe9")
    box(1.0, 6.0, 6.0, 1.3, "Long eyes-closed block (465 s)\n135: cg 66 · sg 45 · sg2 24\n→ 02, 03, 06")
    box(1.0, 3.6, 6.0, 1.3, "Eyes-closed/open epochs (4 × 50 s)\n136 (+ sg2 via epoch file)\n→ 05 primary test")
    box(1.0, 1.2, 6.0, 1.3, "Excel ∩ published data, ID-verified\n100: cg 55 · sg 45  → 04-B (verified), 07\n(07c adds sg2 24 for transfer)")
    arrow(4.0, 8.4, 4.0, 7.3); arrow(7.0, 8.6, 7.6, 8.3); arrow(4.0, 6.0, 4.0, 4.9); arrow(4.0, 3.6, 4.0, 2.5)
    panel(ax, "a")
    # (b) Venn
    ax = fig.add_subplot(gs[0, 1]); ax.axis("off"); ax.set_xlim(-2.6, 2.6); ax.set_ylim(-1.5, 1.6); ax.set_aspect("equal")
    ax.add_patch(Circle((-0.55, 0), 1.05, fc="#fdf1d6", ec=MUTED, alpha=0.9)); ax.add_patch(Circle((0.65, 0), 1.25, fc="#eef3fb", ec=MUTED, alpha=0.7))
    ax.text(-1.15, 0, "12", ha="center", va="center", fontsize=9, color=INK); ax.text(0.05, 0, "100", ha="center", va="center", fontsize=9, color=INK)
    ax.text(1.35, 0, "40", ha="center", va="center", fontsize=9, color=INK)
    ax.text(-1.55, 1.2, "Excel features\n(112; no sg2)", ha="center", fontsize=6.4, color=INK2)
    ax.text(1.6, 1.3, "Published EEG\n(140)", ha="center", fontsize=6.4, color=INK2)
    ax.text(0, -1.45, "12 Excel IDs match no published recording", ha="center", fontsize=6.2, color=INK2)
    panel(ax, "b")
    # (c) kayıt zaman çizelgesi
    ax = fig.add_subplot(gs[1, 1]); rng = np.random.default_rng(2)
    for i, grp in enumerate(["cg", "sg", "sg2"]):
        d = aud[aud.subject.str.endswith(grp) & ~(aud.subject.str.endswith("sg2") & (grp == "sg"))]
        ax.scatter(d.dt, i + rng.uniform(-0.18, 0.18, len(d)), s=7, color=GROUP[grp], lw=0, alpha=0.85)
    ax.set_yticks(range(3)); ax.set_yticklabels(["cg", "sg", "sg2"]); ax.set_ylim(-0.6, 2.6); ax.invert_yaxis()
    ax.grid(axis="x", color=GRID, lw=0.6); ax.tick_params(axis="x", labelsize=6.3)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_title("Recording date by group", loc="left", fontsize=7.5, color=INK)
    panel(ax, "c")
    save(fig, "Fig5_cohort")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
