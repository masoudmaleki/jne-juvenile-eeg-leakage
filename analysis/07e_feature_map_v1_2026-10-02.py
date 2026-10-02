"""07e betimsel öznitelik haritası (DENETIM_RAPORU_2 bölüm 5; TEST YOK).

07e öznitelikleri (B seti: göreli bant gücü, uzun göz kapalı blok, 4 x 116,25 s, kanal dışlaması yok; 100 denek: sg 45, cg 55).
Denek başına 4 parçanın ortalaması alınır; her kanal x bant için sg − cg etki büyüklüğü:
  Hedges g (birleşik SD, küçük örneklem düzeltmesi) ve rank-biserial r (sg > cg pozitif). p değeri hesaplanmaz.
Okur:  analysis/07de_transfer_longblock_v1_2026-10-02_longblock_features.npz, analysis/07_..._features.npz (etiket),
       1 adet .set (kanal adları ve konumları)
Yazar: analysis/07e_feature_map_v1_2026-10-02.csv, analysis/figures/FigS_07e_feature_map_v1.{png,pdf}
"""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.io import loadmat
from scipy.stats import mannwhitneyu
import mne

A = Path(__file__).resolve().parent; ROOT = A.parent
BANDS = ["delta", "theta", "alpha", "beta"]
L = np.load(A / "07de_transfer_longblock_v1_2026-10-02_longblock_features.npz")
z7 = np.load(A / "07_amplitude_decomp_v1_2026-10-02_features.npz")
assert list(L["subjects"]) == list(z7["subjects"])
X = L["B"].reshape(100, 4, 512).mean(1)                    # denek x öznitelik
y = z7["y"][::4]
E = loadmat(ROOT / "v1.0.0" / "sub-1005sg" / "eeg" / "sub-1005sg_task-restingstate_desc-preprocessed_eeg.set",
            squeeze_me=True, struct_as_record=False, simplify_cells=True, variable_names=["chanlocs"])
labels = [c["labels"] for c in E["chanlocs"]]
pos = np.array([[c["radius"] * np.sin(np.deg2rad(c["theta"])), c["radius"] * np.cos(np.deg2rad(c["theta"]))] for c in E["chanlocs"]])

a, b = X[y == 1], X[y == 0]; n1, n0 = len(a), len(b)
sp = np.sqrt(((n1 - 1) * a.var(0, ddof=1) + (n0 - 1) * b.var(0, ddof=1)) / (n1 + n0 - 2))
g = (a.mean(0) - b.mean(0)) / sp * (1 - 3 / (4 * (n1 + n0) - 9))
U = np.array([mannwhitneyu(a[:, j], b[:, j], alternative="two-sided").statistic for j in range(X.shape[1])])
rb = 2 * U / (n1 * n0) - 1
df = pd.DataFrame(dict(band=np.repeat(BANDS, 128), channel=np.tile(labels, 4), block=np.tile([l[0] for l in labels], 4),
                       mean_sg=a.mean(0), mean_cg=b.mean(0), hedges_g=g, rank_biserial=rb))
df.to_csv(A / "07e_feature_map_v1_2026-10-02.csv", index=False, encoding="utf-8-sig")
print(df.groupby("band").hedges_g.describe().round(3))
print(df.groupby(["band", "block"]).hedges_g.median().unstack().round(3))

cmap = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#ec835a", "#c14a1c"])
lim = float(np.ceil(np.abs(g).max() * 10) / 10)
fig, ax = plt.subplots(1, 4, figsize=(7.4, 2.3), gridspec_kw=dict(wspace=0.15))
for k, band in enumerate(BANDS):
    v = df[df.band == band].hedges_g.values
    im, _ = mne.viz.plot_topomap(v, pos, axes=ax[k], show=False, cmap=cmap, vlim=(-lim, lim), sphere=0.5, contours=0,
                                 sensors=True)
    isC = np.array([l.startswith("C") for l in labels])
    ax[k].scatter(pos[isC, 0], pos[isC, 1], s=4, facecolors="none", edgecolors="#52514e", lw=0.4)
    ax[k].set_title(f"Relative {band}", fontsize=8, color="#0b0b0b")
cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02); cb.set_label("Hedges g (sg − cg)", fontsize=7); cb.ax.tick_params(labelsize=6.5)
fig.suptitle("07e long eyes-closed block: channel-level effect sizes, sg (n = 45) vs cg (n = 55); descriptive, no test",
             x=0.02, ha="left", fontsize=8, color="#0b0b0b", y=1.02)
for ext in ["png", "pdf"]:
    fig.savefig(A / "figures" / f"FigS_07e_feature_map_v1.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
print("yazıldı: 07e_feature_map_v1_2026-10-02.csv, figures/FigS_07e_feature_map_v1.png/pdf")
