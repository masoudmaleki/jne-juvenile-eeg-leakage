"""02 - Pilot öznitelikler için QC figürü (salt okuma).
Okur: analysis/02_features_pilot_v1_2026-10-01.csv ve _psd.npz; v1.0.0'dan yalnız kanal konumları.
Yazar: analysis/02_features_pilot_qc_v1_2026-10-01.png
Satır = denek. Sütunlar: posterior ROI spektrumu + FOOOF modeli | aperiodik üs topografisi | FOOOF R² topografisi.
"""
from pathlib import Path
import warnings
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
from fooof import FOOOF
import importlib.util

ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "analysis"
spec = importlib.util.spec_from_file_location("feat", OUT / "02_features_v1_2026-10-01.py")
feat = importlib.util.module_from_spec(spec); spec.loader.exec_module(feat)

INK, INK2, MUTED, SURF = "#0b0b0b", "#52514e", "#898781", "#fcfcfb"
DATA, MODEL, APER = "#2a78d6", "#eb6834", "#52514e"

d = pd.read_csv(OUT / "02_features_pilot_v1_2026-10-01.csv")
z = np.load(OUT / "02_features_pilot_v1_2026-10-01_psd.npz")
f, psd, subs, chans = z["freqs"], z["psd"], list(z["subjects"]), list(z["channels"])
_, _, labels, pos, _ = feat.load_block(subs[0])  # kanal konumları tüm deneklerde aynı
post = [chans.index(c) for c in feat.ROIS["posterior"]]

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(len(subs), 3, figsize=(11, 3.3 * len(subs)), facecolor=SURF,
                       gridspec_kw=dict(width_ratios=[1.6, 1, 1]))
for r, s in enumerate(subs):
    a = ax[r, 0]; a.set_facecolor(SURF)
    p = psd[r][post].mean(0)
    fm = FOOOF(**feat.FOOOF_KW)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore"); fm.fit(f, p, feat.FOOOF_RANGE)
    a.plot(fm.freqs, fm.power_spectrum, color=DATA, lw=2, label="PSD (log10)")
    a.plot(fm.freqs, fm.fooofed_spectrum_, color=MODEL, lw=2, label="FOOOF modeli")
    a.plot(fm.freqs, fm._ap_fit, color=APER, lw=1.5, ls="--", label="Aperiodik bileşen")
    row = d[(d.subject == s) & (d.unit == "ROI_posterior")].iloc[0]
    a.set_title(f"{s} · posterior ROI   üs={row.ap_exponent:.2f}  IAF={row.iaf_fooof:.2f} Hz  R²={row.fooof_r2:.3f}",
                loc="left", fontsize=9, color=INK)
    a.set_xlabel("Frekans (Hz)"); a.set_ylabel("log10 güç (µV²/Hz)")
    a.grid(axis="y", color="#e8e7e3", lw=0.6)
    if r == 0: a.legend(frameon=False, fontsize=8)
    ch = d[(d.subject == s) & ~d.unit.str.startswith("ROI_")].set_index("unit").loc[chans]
    for c, (col, vmin, vmax, cmap, ttl) in enumerate([("ap_exponent", 0, 2.2, "Blues", "Aperiodik üs"),
                                                      ("fooof_r2", 0.3, 1.0, "Blues", "FOOOF R²")], start=1):
        a = ax[r, c]
        im, _ = mne.viz.plot_topomap(ch[col].values, pos, axes=a, show=False, cmap=cmap, vlim=(vmin, vmax),
                                     sphere=0.5, contours=0, sensors=True)
        bad = ch["fooof_r2"].values < 0.9
        a.scatter(pos[bad, 0], pos[bad, 1], s=22, facecolors="none", edgecolors=MODEL, lw=1.2)
        a.set_title(f"{ttl}" + ("  (turuncu halka: R²<0,9)" if c == 2 else ""), fontsize=9, color=INK)
        fig.colorbar(im, ax=a, shrink=0.7)
fig.suptitle("Pilot öznitelik QC: 465 s göz kapalı blok (3. C işareti + 5 s)", x=0.01, ha="left", color=INK, fontsize=11)
fig.tight_layout()
fn = OUT / "02_features_pilot_qc_v1_2026-10-01.png"
fig.savefig(fn, dpi=130, facecolor=SURF); print("yazıldı:", fn)
