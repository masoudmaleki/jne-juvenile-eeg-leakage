"""08 v6 (2026-10-03) - YALNIZ iki şekil yeniden üretilir; yeni analiz yok, sayılar ve veri kaynakları 08 v5 ile aynı.
  Fig1_leakage_v4          : paneller 2 × 2 (üstte a, b; altta c, d). (a)'da y ekseni 1.1'e açıldı ve "epoch leakage" /
                             "selection leakage" yazıları noktaların üstüne (1.0'ın üstüne) taşındı. Başka değişiklik yok.
  Fig4_prespecified_null_v4: x ekseni yazısında "pre-specified" -> "prespecified". Başka değişiklik yok.
Diğer şekiller için 08 v5 çıktıları geçerli. Var olan şeklin üzerine yazılmaz (--uzerine-yaz seçeneği kaldırıldı).
GD kontrolü -> 08_figures_v6_2026-10-03_gd_check.csv (v5 ile aynı değerler).

08 v5 (2026-10-03) - Şekil turu; yeni analiz yok, yalnız kayıtlı sonuç dosyaları okunur. Eski betiklere ve şekillere dokunulmaz.
  Fig1_leakage_v3            : a–c aynen (08 v2 ile aynı kod); yeni panel d "Golden Distance (RF)" (N1 RF ve P RF; ACC, Sen, Spe, F1).
                               Veri: 04b_leakage_gd_v1_2026-10-02_results.csv (variant = primary); ACC = (Sen*46 + Spe*66)/112.
                               GD çizilen dört değerden, 04b_leakage_gd_v1_2026-10-02.py içe aktarılarak (onun kullandığı metrics_gd) hesaplanır;
                               kayıtlı subj_GD ile karşılaştırma -> 08_figures_v5_2026-10-03_gd_check.csv
  Fig2_exploratory_cascade_v5: (a) üstündeki uzun başlık yok; AUC etiketleri iki ondalık. Başka değişiklik yok.
  Fig4_prespecified_null_v3  : AUC etiketleri iki ondalık; gölgeli alan yazısı "approximately excluded".
  Fig5_cohort_v3             : "Excel" -> "spreadsheet"; son kutuda 07f eklendi.
  FigS_07e_feature_map_v2    : üstteki uzun başlık yok. Etki büyüklükleri kayıtlı 07e_feature_map_v1_2026-10-02.csv'den okunur
                               (yeniden hesap yok); kanal konumları v1 betiğindeki gibi bir .set dosyasından SALT OKUNUR.
  Fig3 değişmez (yeniden üretilmez).
Çıktı: analysis/figures/<ad>.{png,pdf}; pdf kopyaları manuscript/figures/ içine.
Kullanım: python 08_figures_v5_2026-10-03.py [fig1 fig2 fig4 fig5 figS] [--uzerine-yaz]
  Var olan şeklin üzerine yazılmaz; --uzerine-yaz yalnız aynı oturumda üretilmiş, teslim edilmemiş taslağı düzeltmek içindir.

08 v4 - YALNIZ Şekil 2 yeniden üretilir (DENETIM_RAPORU_4, G5): (b) panelinde CV tekrarı 2,5–97,5 (kalın) çizgilerinin arkasına
07g %95 GA'ları (ince; denek bootstrap'ı) ve (b) paneline ayrı gösterge eklendi. Başka değişiklik yok; yeni hesap yok.
Ek okunan: analysis/07g_auc_ci_v1_2026-10-02_results.csv (ci_low, ci_high). Çıktı: figures/Fig2_exploratory_cascade_v4.{png,pdf}

08 v3 - YALNIZ Şekil 2 yeniden üretilir (DENETIM_RAPORU_2: E4 başlık, E6 etiketler; 07f transfer sütunu eklendi).
Şekil 1, 3, 4, 5 için v2 dosyaları geçerli. Aşağıdaki açıklama v2'den devralındı.

08 v2 - Makale şekilleri 1–5 (salt okuma; yalnız analysis/ çıktılarından). 300 dpi PNG + PDF -> analysis/figures/*_v2.*

v1'e göre (DENETIM_RAPORU): D6 Şekil 1a (metrik adı, sızıntı gölgeleri, seçim alt etiketleri); D3/D7 Şekil 2
(C/A bloğu adları, n'ler, kural boşluğu yalnız 07a kapalı sütununda, p ≤ 0,005, başlık 07d kuralına göre; 07d ve 07e eklendi);
D8 Şekil 5a (140'tan dallanan paralel örneklem kutuları). Şekil 3 ve 4 aynı (yeniden üretildi).
"""
from pathlib import Path
import importlib, json, shutil, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Patch
from matplotlib.lines import Line2D

A = Path(__file__).resolve().parent; FIG = A / "figures"; FIG.mkdir(exist_ok=True)
ROOT = A.parent; MS_FIG = ROOT / "manuscript" / "figures"; STEM = "08_figures_v6_2026-10-03"
INK, INK2, MUTED, GRID, NULLC = "#0b0b0b", "#52514e", "#898781", "#e8e7e3", "#c9c8c2"
GROUP = {"cg": "#2a78d6", "sg": "#eb6834", "sg2": "#1baf7a"}
MODEL = {"SVM": "#4a3aa7", "RF": "#e87ba4"}
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "pdf.fonttype": 42, "font.family": "DejaVu Sans"})


def save(fig, name):
    """name sürüm ekiyle verilir; var olan dosyanın üzerine yazılmaz. pdf kopyası manuscript/figures/ içine."""
    for ext in ("png", "pdf"):
        if (FIG / f"{name}.{ext}").exists():
            sys.exit(f"DUR: {name}.{ext} zaten var; üzerine yazılmaz.")
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    shutil.copyfile(FIG / f"{name}.pdf", MS_FIG / f"{name}.pdf")
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
    fig = plt.figure(figsize=(7.2, 6.4))                                  # v6: 2 × 2 (üstte a, b; altta c, d)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1], wspace=0.32, hspace=0.55)
    ax = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0])]
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
    sel_lab = {"N1": "N1\nglobal", "N2": "N2\nin CV", "N3": "N3\nglobal", "N4": "N4\nin CV", "P": "P\nnested"}
    for a, yl, tt in [(ax[0], "Subject-level ROC-AUC", "ROC-AUC by pipeline"), (ax[2], "Golden Distance (lower = better)", "Golden Distance")]:
        a.set_xticks(x); a.set_xticklabels([sel_lab[c] for c in cells], fontsize=6.5 if a is ax[0] else 5.6)
        a.set_ylabel(yl); a.set_title(tt, loc="left", color=INK); a.grid(axis="y", color=GRID, lw=0.6)
        for x0, x1, lab in [(-0.3, 1.3, "row CV"), (1.7, 4.3, "subject CV")]:
            a.annotate("", xy=(x0, -0.22), xytext=(x1, -0.22), xycoords=("data", "axes fraction"),
                       arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
            a.text((x0 + x1) / 2, -0.25, lab, transform=a.get_xaxis_transform(), ha="center", va="top", fontsize=6.5, color=INK2)
        a.axvspan(-0.5, 1.5, color="#f3e3d8", zorder=0)        # epok + (N1) seçim sızıntısı
        a.axvspan(1.5, 2.5, color="#f8f0ea", zorder=0)         # N3: yalnız seçim sızıntısı
    chance(ax[0]); ax[0].set_ylim(0.4, 1.1); ax[0].set_yticks(np.arange(0.4, 1.01, 0.1))   # v6: yazılar noktaların üstünde
    ax[0].legend(loc="lower left", fontsize=7)
    ax[0].text(0.5, 1.09, "epoch\nleakage", ha="center", va="top", fontsize=6.3, color=INK2)
    ax[0].text(2.0, 1.09, "selection\nleakage", ha="center", va="top", fontsize=6.3, color=INK2)
    ax[2].set_ylim(0.3, 0.85)
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
    # (d) Golden Distance (RF): N1 RF ve P RF, dört eksen (ACC, Sen, Spe, F1), 90 derece aralıklı
    gdr = pd.read_csv(A / "04b_leakage_gd_v1_2026-10-02_results.csv").query("variant=='primary' and model=='RF'").set_index("cell")
    G = importlib.import_module("04b_leakage_gd_v1_2026-10-02")           # yalnız içe aktarma (main çalışmaz)
    golden_distance = sys.modules[G.gd_from_predictions.__module__].golden_distance   # 04b GD betiğinin kullandığı GD (metrics_gd)
    N_SG, N_CG = 46, 66                                                    # sınıf boyutları (sg pozitif)
    axd = fig.add_subplot(gs[1, 1]); axd.axis("off"); axd.set_aspect("equal", anchor="N")
    axd.set_xlim(-1.5, 1.5); axd.set_ylim(-1.3, 1.3)                      # v6: gösterge elmasın altında
    DIRS = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]], float)             # ACC üst, Sen sağ, Spe alt, F1 sol
    poly = lambda v: np.vstack([DIRS * np.asarray(v)[:, None], DIRS[:1] * v[0]])
    for rr in (0.25, 0.5, 0.75):
        p = poly([rr] * 4); axd.plot(p[:, 0], p[:, 1], color=GRID, lw=0.6, zorder=1)
    for dxy in DIRS:
        axd.plot([0, dxy[0]], [0, dxy[1]], color=GRID, lw=0.6, zorder=1)
    p = poly([1.0] * 4); axd.plot(p[:, 0], p[:, 1], color=MUTED, lw=0.7, zorder=2)      # ideal kare (hepsi 1)
    axd.text(0.03, -0.5, "0.5", fontsize=5.8, color=MUTED, ha="left", va="center")   # halkalar 0.25, 0.5, 0.75; dış kare = 1
    for (dx, dy), lab_ in zip(DIRS * 1.08, ["ACC", "Sen", "Spe", "F1"]):
        axd.text(dx, dy, lab_, fontsize=7, color=INK2, ha="center" if dx == 0 else ("left" if dx > 0 else "right"),
                 va="center" if dy == 0 else ("bottom" if dy > 0 else "top"))
    handles, chk_rows = [Line2D([], [], color=MUTED, lw=0.7, label="ideal (all = 1)")], []
    for cell, ls, lab_ in [("N1", "-", "N1 RF (naive)"), ("P", (0, (4, 2)), "P RF (nested, subject-wise)")]:
        d = gdr.loc[cell]
        acc = (d.subj_Sen * N_SG + d.subj_Spe * N_CG) / (N_SG + N_CG)      # kayıtlı ortalamalardan aritmetik
        vals = [acc, d.subj_Sen, d.subj_Spe, d.subj_F1]
        gd_plot = golden_distance(vals)["gd"]                              # çizilen dört değerden
        diff = gd_plot - d.subj_GD                                         # kayıtlı subj_GD = tekrar GD'lerinin ortalaması
        gd_leg = gd_plot if abs(diff) > 0.005 else d.subj_GD
        p = poly(vals)
        axd.plot(p[:, 0], p[:, 1], color=MODEL["RF"], lw=1.5, ls=ls, zorder=3)
        axd.scatter(p[:-1, 0], p[:-1, 1], s=10, color=MODEL["RF"], zorder=4, lw=0)
        handles.append(Line2D([], [], color=MODEL["RF"], lw=1.5, ls=ls, marker="o", ms=3, label=f"{lab_}: GD = {gd_leg:.2f}"))
        chk_rows.append(dict(cell=f"{cell} RF", ACC=acc, Sen=d.subj_Sen, Spe=d.subj_Spe, F1=d.subj_F1, GD_from_plotted=gd_plot,
                             GD_stored_subj_GD=d.subj_GD, diff=diff, abs_diff_gt_0_005=bool(abs(diff) > 0.005), GD_in_legend=f"{gd_leg:.2f}",
                             legend_source="computed from plotted values" if abs(diff) > 0.005 else "stored subj_GD"))
    axd.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.0, -1.32), bbox_transform=axd.transData, fontsize=7, handlelength=2.6)
    axd.text(0.0, 1.0, "Golden Distance (RF)", transform=axd.transAxes, fontsize=9, color=INK, ha="left", va="bottom")
    axd.text(-0.12, 1.0, "d", transform=axd.transAxes, fontsize=10, fontweight="bold", color=INK, va="bottom")
    chk = pd.DataFrame(chk_rows); chk.to_csv(A / f"{STEM}_gd_check.csv", index=False, encoding="utf-8-sig")
    print(chk.to_string(index=False))
    save(fig, "Fig1_leakage_v4")


# ---------------------------------------------------------------- Fig 2
def fig2():
    rep7 = pd.read_csv(A / "07_amplitude_decomp_v1_2026-10-02_reps.csv")
    r7 = pd.read_csv(A / "07_amplitude_decomp_v1_2026-10-02_results.csv").set_index("set")
    z7 = np.load(A / "07_amplitude_decomp_v1_2026-10-02_null.npz")
    S = "07abc_source_decomp_v1_2026-10-02"; D = "07de_transfer_longblock_v1_2026-10-02"
    real = pd.DataFrame(jl(A / f"{S}_ckpt_real.jsonl")); null = pd.DataFrame(jl(A / f"{S}_ckpt_null.jsonl"))
    treal = pd.DataFrame(jl(A / f"{S}_ckpt_tr_real.jsonl")); tnull = pd.DataFrame(jl(A / f"{S}_ckpt_tr_null.jsonl"))
    r7c = pd.read_csv(A / f"{S}_results.csv").set_index("set")
    dreal = pd.DataFrame(jl(A / f"{D}_ckpt_real.jsonl")); dnull = pd.DataFrame(jl(A / f"{D}_ckpt_null.jsonl"))
    dtr = pd.DataFrame(jl(A / f"{D}_ckpt_tr_real.jsonl")); dtn = pd.DataFrame(jl(A / f"{D}_ckpt_tr_null.jsonl"))
    rd = pd.read_csv(A / f"{D}_results.csv").set_index("set")
    within = [("Absolute\nall epochs", rep7.query("set=='A_log_abs'").subj_auc, z7["A_log_abs"], r7.loc["A_log_abs", "p_perm"]),
              ("Relative\nall epochs", rep7.query("set=='B_relative'").subj_auc, z7["B_relative"], r7.loc["B_relative", "p_perm"]),
              ("Relative\neyes open", real.query("set=='07a_open'").subj_auc, null.query("set=='07a_open'").subj_auc, r7c.loc["07a_open", "p_perm"]),
              ("Relative\neyes closed", real.query("set=='07a_closed'").subj_auc, null.query("set=='07a_closed'").subj_auc, r7c.loc["07a_closed", "p_perm"]),
              ("Rel. closed,\nC block out", real.query("set=='07b_closed_noC'").subj_auc, null.query("set=='07b_closed_noC'").subj_auc, r7c.loc["07b_closed_noC", "p_perm"]),
              ("Relative, long\neyes-closed block", dreal.subj_auc, dnull.subj_auc, rd.loc["07e_longblock", "p_perm"])]
    trans = [("Rel. closed\n(07c)", treal.auc_sg2_24, tnull.auc_sg2_24, r7c.loc["07c_transfer", "p_perm"]),
             ("Absolute\nall (07d)", dtr.query("set=='07d_A_all'").auc_sg2_24, dtn.query("set=='07d_A_all'").auc_sg2_24, rd.loc["07d_A_all", "p_perm"]),
             ("Relative\nall (07d)", dtr.query("set=='07d_B_all'").auc_sg2_24, dtn.query("set=='07d_B_all'").auc_sg2_24, rd.loc["07d_B_all", "p_perm"]),
             ("Relative\nopen (07d)", dtr.query("set=='07d_B_open'").auc_sg2_24, dtn.query("set=='07d_B_open'").auc_sg2_24, rd.loc["07d_B_open", "p_perm"])]
    F = "07f_longblock_transfer_v1_2026-10-02"
    ftr = pd.DataFrame(jl(A / f"{F}_ckpt_tr_real.jsonl")); ftn = pd.DataFrame(jl(A / f"{F}_ckpt_tr_null.jsonl"))
    rf = pd.read_csv(A / f"{F}_results.csv").iloc[0]
    trans.append(("Long closed\nblock (07f)", ftr.auc_sg2_24, ftn.auc_sg2_24, rf.p_perm))
    pmin = 1 / 201
    def plab(p):
        if p <= pmin + 1e-9: return "p ≤ 0.005"
        s3 = f"{p:.3f}"
        return f"p = {p:.4f}" if (p < 0.05) != (float(s3) < 0.05) else f"p = {s3}"   # E6: 0.0498 ≠ "0.050"
    fig = plt.figure(figsize=(7.4, 5.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.75, 1], height_ratios=[1, 1], hspace=0.65, wspace=0.32)

    def draw(ax, items, ylab, gap_idx=None, ytop=0.92, cis=None):
        for i, (lab, rv, nv, p) in enumerate(items):
            lo, hi = np.percentile(nv, [2.5, 97.5])
            ax.add_patch(plt.Rectangle((i - 0.22, lo), 0.44, hi - lo, color=NULLC, zorder=1, lw=0))
            m = float(np.mean(rv)); a, b = np.percentile(rv, [2.5, 97.5]); ytxt = b
            if cis is not None:                                                   # G5: 07g %95 GA, ince çizgi, arkada
                ax.plot([i, i], cis[i], color=INK2, lw=0.7, zorder=2, solid_capstyle="butt")
                ytxt = max(b, cis[i][1])                                          # yalnız etiket konumu
            ax.errorbar([i], [m], yerr=[[m - a], [b - m]], fmt="o", ms=5, color=INK, elinewidth=1.5, capsize=0, zorder=3,
                        mfc=INK if p < 0.05 else "white")
            ax.text(i, ytxt + 0.012, f"{m:.2f}\n{plab(p)}", ha="center", va="bottom", fontsize=6.0, color=INK2)
        if gap_idx is not None:
            ax.add_patch(plt.Rectangle((gap_idx - 0.38, 0.60), 0.76, 0.05, color="#f7d98b", alpha=0.55, zorder=0, lw=0))
            ax.text(gap_idx + 0.42, 0.625, "rule gap\n0.60–0.65", fontsize=5.6, color=INK2, va="center", ha="left")
        chance(ax); ax.set_ylim(0.32, ytop); ax.set_xlim(-0.6, len(items) - 0.4)
        ax.set_xticks(range(len(items))); ax.set_xticklabels([i[0] for i in items], fontsize=6.2)
        ax.set_ylabel(ylab); ax.grid(axis="y", color=GRID, lw=0.6)

    ax = fig.add_subplot(gs[0, :])
    draw(ax, within, "Subject-level ROC-AUC\n(sg vs cg)", gap_idx=3, ytop=1.0)
    ax.legend(handles=[Line2D([], [], marker="o", ls="-", color=INK, label="observed, p < 0.05 (CV-repeat 2.5–97.5%)"),
                       Line2D([], [], marker="o", ls="-", color=INK, mfc="white", label="observed, p ≥ 0.05"),
                       Patch(color=NULLC, label="shuffled-label null 95%")], loc="upper right", fontsize=6.0, ncol=3,
              bbox_to_anchor=(1.0, 1.02))
    panel(ax, "a")
    ax = fig.add_subplot(gs[1, 0])
    ci = pd.read_csv(A / "07g_auc_ci_v1_2026-10-02_results.csv").set_index("set")
    ci_keys = ["07c_B_closed", "07d_A_all", "07d_B_all", "07d_B_open", "07f_B_longblock"]
    assert len(ci_keys) == len(trans)
    draw(ax, trans, "Transfer ROC-AUC\n(held-out cg vs sg2)", cis=[(ci.loc[k, "ci_low"], ci.loc[k, "ci_high"]) for k in ci_keys])
    ax.legend(handles=[Line2D([], [], color=INK, lw=1.5, label="thick: CV-repeat 2.5–97.5%"),
                       Line2D([], [], color=INK2, lw=0.7, label="thin: 95% CI (subject bootstrap)")],
              loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=5.6, ncol=2)
    ax.set_title("Models trained on sg + cg, tested on sg2 (n = 24)", loc="left", fontsize=8, color=INK)
    panel(ax, "b")
    d = pd.read_csv(A / f"{S}_descriptive.csv")
    gs2 = gs[1, 1].subgridspec(2, 1, hspace=1.0)
    for k, (meas, tt) in enumerate([("rel_delta_frontalC", "Relative delta, C block (eyes closed)"),
                                    ("rel_alpha_Ablock", "Relative alpha, A block (eyes closed)")]):
        a = fig.add_subplot(gs2[k])
        for j, (grp, lab, n) in enumerate([("cg", "cg", 55), ("sg", "sg", 45), ("sg2_24", "sg2", 24)]):
            row = d[(d.group == grp) & (d.measure == meas)].iloc[0]
            a.errorbar([row["median"]], [j], xerr=[[row["median"] - row.q1], [row.q3 - row["median"]]], fmt="o", ms=4.5,
                       color=GROUP[lab], elinewidth=1.5, capsize=0)
        a.set_yticks(range(3)); a.set_yticklabels(["cg (55)", "sg (45)", "sg2 (24)"], fontsize=6.5); a.set_ylim(-0.6, 2.6); a.invert_yaxis()
        a.set_title(tt, loc="left", fontsize=7, color=INK); a.set_xlabel("median [IQR]", fontsize=6.5); a.grid(axis="x", color=GRID, lw=0.6)
        a.tick_params(axis="x", labelsize=6.5)
        if k == 0: panel(a, "c")
    save(fig, "Fig2_exploratory_cascade_v5")


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
    save(fig, "Fig3_primary_alpha_reactivity_v3")   # v5'te çağrılmaz


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
    assert f"{U:.2f}" == "0.63"
    ax.text(0.985, 1.5, f"AUC > {U:.2f}\napproximately excluded\n(offenders vs cg)", ha="right", va="center", fontsize=6.5, color=INK2)
    for j, (lab, m, lo, hi, kind) in enumerate(rows):
        ax.errorbar([m], [j], xerr=[[m - lo], [hi - m]], fmt="o", ms=5, color=INK, elinewidth=2.0 if kind == "ci" else 1.0,
                    capsize=0, mfc=INK if kind == "ci" else "white", zorder=3)
        ax.text(hi + 0.01, j, f"{m:.2f}", va="center", fontsize=6.5, color=INK2)
    chance(ax, horiz=False)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=6.8); ax.set_ylim(-0.6, len(rows) - 0.4); ax.invert_yaxis()
    ax.set_xlim(0.25, 1.0); ax.set_xlabel("ROC-AUC (prespecified 14 spectral features, long eyes-closed block)")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.legend(handles=[Line2D([], [], marker="o", color=INK, lw=2, label="95% CI (subject bootstrap)"),
                       Line2D([], [], marker="o", color=INK, mfc="white", lw=1, label="CV-repetition 2.5–97.5% (not a CI)")],
              loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=2, fontsize=6.3)
    save(fig, "Fig4_prespecified_null_v4")


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
    # D8: 140'tan dallanan PARALEL örneklemler (ardışık bir süzme değil)
    box(0.2, 8.7, 9.6, 1.1, "OpenNeuro ds006923: 140 participants (cg 66 · sg 49 · sg2 25)")
    branches = [(6.75, "Long eyes-closed block (465 s): n = 135\ncg 66 · sg 45 · sg2 24  → 02, 03, 06\n"
                       "not available: 4 sg (~157 s), 1 sg2 (file missing)", "white"),
                (4.95, "Eyes-closed/open epochs (4 × 50 s): n = 136\ncg 66 · sg 45 · sg2 25  → 05 (primary)\n"
                       "+ 4 short sg in n = 140 sensitivity", "white"),
                (3.15, "Precomputed spreadsheet features: n = 112\ncg 66 · sg 46 (no sg2)  → 04-A, 04-B\n"
                       "12 IDs match no published recording", "#fbf3e3"),
                (1.35, "ID-verified (spreadsheet ∩ published): n = 100\ncg 55 · sg 45  → 07, 07a–b, 07e\n"
                       "+ sg2 24 as transfer test set → 07c, 07d, 07f", "white")]
    ax.plot([0.55, 0.55], [8.7, 2.1], color=MUTED, lw=0.9)
    for y, txt, fc in branches:
        box(1.0, y, 8.8, 1.5, txt, fc=fc); arrow(0.55, y + 0.75, 1.0, y + 0.75)
    panel(ax, "a")
    # (b) Venn
    ax = fig.add_subplot(gs[0, 1]); ax.axis("off"); ax.set_xlim(-2.6, 2.6); ax.set_ylim(-1.5, 1.6); ax.set_aspect("equal")
    ax.add_patch(Circle((-0.55, 0), 1.05, fc="#fdf1d6", ec=MUTED, alpha=0.9)); ax.add_patch(Circle((0.65, 0), 1.25, fc="#eef3fb", ec=MUTED, alpha=0.7))
    ax.text(-1.15, 0, "12", ha="center", va="center", fontsize=9, color=INK); ax.text(0.05, 0, "100", ha="center", va="center", fontsize=9, color=INK)
    ax.text(1.35, 0, "40", ha="center", va="center", fontsize=9, color=INK)
    ax.text(-1.55, 1.2, "Spreadsheet features\n(112; no sg2)", ha="center", fontsize=6.4, color=INK2)
    ax.text(1.6, 1.3, "Published EEG\n(140)", ha="center", fontsize=6.4, color=INK2)
    ax.text(0, -1.45, "12 spreadsheet IDs match no published recording", ha="center", fontsize=6.2, color=INK2)
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
    save(fig, "Fig5_cohort_v3")


# ---------------------------------------------------------------- Fig S (07e öznitelik haritası)
def figS():
    """07e_feature_map_v1_2026-10-02.py ile aynı çizim, üstteki uzun başlık (suptitle) olmadan. Hedges g kayıtlı CSV'den okunur."""
    from matplotlib.colors import LinearSegmentedColormap
    from scipy.io import loadmat
    import mne
    BANDS = ["delta", "theta", "alpha", "beta"]
    df = pd.read_csv(A / "07e_feature_map_v1_2026-10-02.csv")
    E = loadmat(ROOT / "v1.0.0" / "sub-1005sg" / "eeg" / "sub-1005sg_task-restingstate_desc-preprocessed_eeg.set",
                squeeze_me=True, struct_as_record=False, simplify_cells=True, variable_names=["chanlocs"])   # salt okuma
    labels = [c["labels"] for c in E["chanlocs"]]
    pos = np.array([[c["radius"] * np.sin(np.deg2rad(c["theta"])), c["radius"] * np.cos(np.deg2rad(c["theta"]))] for c in E["chanlocs"]])
    g = df.hedges_g.values
    cmap = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#ec835a", "#c14a1c"])
    lim = float(np.ceil(np.abs(g).max() * 10) / 10)
    fig, ax = plt.subplots(1, 4, figsize=(7.4, 2.3), gridspec_kw=dict(wspace=0.15))
    for k, band in enumerate(BANDS):
        d = df[df.band == band]
        assert list(d.channel) == labels, "CSV kanal sırası .set ile aynı olmalı"
        im, _ = mne.viz.plot_topomap(d.hedges_g.values, pos, axes=ax[k], show=False, cmap=cmap, vlim=(-lim, lim), sphere=0.5, contours=0,
                                     sensors=True)
        isC = np.array([l.startswith("C") for l in labels])
        ax[k].scatter(pos[isC, 0], pos[isC, 1], s=4, facecolors="none", edgecolors="#52514e", lw=0.4)
        ax[k].set_title(f"Relative {band}", fontsize=8, color="#0b0b0b")
    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02); cb.set_label("Hedges g (sg − cg)", fontsize=7); cb.ax.tick_params(labelsize=6.5)
    save(fig, "FigS_07e_feature_map_v2")


if __name__ == "__main__":
    ALL = dict(fig1=fig1, fig4=fig4)                                       # v6: yalnız Şekil 1 ve 4
    for k in ([a for a in sys.argv[1:] if not a.startswith("--")] or list(ALL)):
        ALL[k]()
