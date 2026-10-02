"""09 - Tablo 1 (demografi ve confound'lar) ve Tablo S-n (analiz örneklemleri). DENETIM_RAPORU D11, D12.

Tablo 1: 140 katılımcı; sütunlar sg, sg2, suçlu toplamı (sg + sg2), cg; p (suçlu vs cg) ve p (sg vs sg2).
Testler önceden ve tek seçildi (D11): sürekli/sıralı -> Mann–Whitney U (iki yönlü); ikili -> Fisher exact.
Kayıt saati (D12): .set başlığındaki etc.T0 (01 audit, rec_datetime); ortalama saat ve 14:00 sonrası oran.
Eğitim düzeyi grupta farklı kodlandığı için (cg: Middle school vb.; suçlu: Basic primary/secondary) yalnız betimsel; test yok.
Okur:  v1.0.0/participants.tsv, analysis/01_data_audit_v2_2026-10-01.csv
Yazar: analysis/09_tables_v1_2026-10-02_{Table1,TableSn}.{csv,md}
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu, fisher_exact

A = Path(__file__).resolve().parent; ROOT = A.parent
STEM = "09_tables_v1_2026-10-02"
VIOLENT = {"Homicide", "Sexual_Abuse", "Violence", "Abduction", "Kidnapping"}

p = pd.read_csv(ROOT / "v1.0.0" / "participants.tsv", sep="\t").set_index("participant_id")
p["g"] = p.index.str.extract(r"(sg2|sg|cg)$")[0].values
aud = pd.read_csv(A / "01_data_audit_v2_2026-10-01.csv").query("file=='preprocessed'").set_index("subject")
dt = pd.to_datetime(aud.rec_datetime).reindex(p.index)
p["rec_hour"] = dt.dt.hour + dt.dt.minute / 60
p["after14"] = np.where(dt.isna(), np.nan, (p.rec_hour >= 14).astype(float))
p["violent"] = np.where(p.g == "cg", np.nan, p["Type of crime 1"].isin(VIOLENT).astype(float))
yn = lambda c: p[c].map({"Yes": 1.0, "No": 0.0})
for c in ["School dropout", "Gang member", "Domestic violence", "Displaced by violence", "Consumer of psychoactive substances",
          "Alcohol", "Marijuana", "Cocaine", "Recidivist"]:
    p[c + "_b"] = yn(c)
G = {"sg": p.g == "sg", "sg2": p.g == "sg2", "offenders": p.g != "cg", "cg": p.g == "cg"}


def fmt_cont(v):
    v = v.dropna()
    if len(v) == 0: return "–"
    return f"{v.mean():.1f} ± {v.std():.1f}; {v.median():.1f} [{v.quantile(.25):.1f}–{v.quantile(.75):.1f}] (n={len(v)})"


def fmt_bin(v):
    v = v.dropna()
    if len(v) == 0: return "–"
    return f"{int(v.sum())}/{len(v)} ({100 * v.mean():.0f}%)"


def ptest(kind, a, b):
    a, b = a.dropna(), b.dropna()
    if len(a) == 0 or len(b) == 0: return np.nan
    if kind == "cont":
        return mannwhitneyu(a, b, alternative="two-sided").pvalue if (a.nunique() + b.nunique()) > 1 else np.nan
    t = [[int(a.sum()), int(len(a) - a.sum())], [int(b.sum()), int(len(b) - b.sum())]]
    return fisher_exact(t)[1]


rows = []
spec = [("Age (years)", "Age", "cont"), ("Years of education", "Years of education", "cont"),
        ("Socioeconomic stratum (1–3)", "Socioeconomic stratum", "cont"),
        ("School dropout", "School dropout_b", "bin"), ("Gang member", "Gang member_b", "bin"),
        ("Domestic violence", "Domestic violence_b", "bin"), ("Displaced by violence", "Displaced by violence_b", "bin"),
        ("Psychoactive substance use", "Consumer of psychoactive substances_b", "bin"), ("Alcohol", "Alcohol_b", "bin"),
        ("Marijuana", "Marijuana_b", "bin"), ("Cocaine", "Cocaine_b", "bin"), ("Age of first use (users)", "Age of first use", "cont"),
        ("Violent primary offence (offenders)", "violent", "bin"), ("Recidivist (offenders)", "Recidivist_b", "bin"),
        ("Recording clock time (h)", "rec_hour", "cont"), ("Recording after 14:00", "after14", "bin")]
for lab, col, kind in spec:
    f = fmt_cont if kind == "cont" else fmt_bin
    rows.append({"Variable": lab, "sg (n=49)": f(p.loc[G["sg"], col]), "sg2 (n=25)": f(p.loc[G["sg2"], col]),
                 "Offenders (n=74)": f(p.loc[G["offenders"], col]), "cg (n=66)": f(p.loc[G["cg"], col]),
                 "p offenders vs cg": ptest(kind, p.loc[G["offenders"], col], p.loc[G["cg"], col]),
                 "p sg vs sg2": ptest(kind, p.loc[G["sg"], col], p.loc[G["sg2"], col]),
                 "test": "Mann–Whitney U" if kind == "cont" else "Fisher exact"})
lev = p.groupby("g")["Level of education"].value_counts().unstack(fill_value=0)
rows.append({"Variable": "Level of education (coded differently by group; descriptive only)",
             **{f"{k} (n={n})": "; ".join(f"{c}: {v}" for c, v in lev.loc[g].items() if v)
                for k, g, n in [("sg", "sg", 49), ("sg2", "sg2", 25), ("cg", "cg", 66)]},
             "Offenders (n=74)": "; ".join(f"{c}: {v}" for c, v in lev.loc[["sg", "sg2"]].sum().items() if v),
             "p offenders vs cg": np.nan, "p sg vs sg2": np.nan, "test": "none"})
months = dt.dt.to_period("M").astype(str)
rows.append({"Variable": "Recording period (first–last month)",
             **{f"{k} (n={n})": f"{months[G[k]].min()} – {months[G[k]].max()}" for k, n in [("sg", 49), ("sg2", 25), ("cg", 66)]},
             "Offenders (n=74)": f"{months[G['offenders']].min()} – {months[G['offenders']].max()}",
             "p offenders vs cg": np.nan, "p sg vs sg2": np.nan, "test": "none"})
t1 = pd.DataFrame(rows)[["Variable", "sg (n=49)", "sg2 (n=25)", "Offenders (n=74)", "cg (n=66)", "p offenders vs cg", "p sg vs sg2", "test"]]
t1.to_csv(A / f"{STEM}_Table1.csv", index=False, encoding="utf-8-sig")

pf = lambda x: "–" if pd.isna(x) else ("<0.001" if x < 0.001 else f"{x:.3f}")
md = ["# Table 1. Participant characteristics (all 140 published participants)", "",
      "Continuous/ordinal: mean ± SD; median [IQR]; Mann–Whitney U. Binary: n/N (%); Fisher exact. Tests pre-selected (one per variable type); "
      "p values are unadjusted. Recording time from the EEG file header (etc.T0).", "",
      "| " + " | ".join(t1.columns[:-1]) + " |", "|" + "---|" * (len(t1.columns) - 1)]
for _, r in t1.iterrows():
    md.append("| " + " | ".join([str(r[c]) for c in t1.columns[:5]] + [pf(r["p offenders vs cg"]), pf(r["p sg vs sg2"])]) + " |")
(A / f"{STEM}_Table1.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# Tablo S-n: analiz örneklemleri
sn = pd.DataFrame([
    ("01 Data audit", "all files", 66, 49, 25, "–"),
    ("02 Features / 03 / 06", "long eyes-closed block, 465 s", 66, 45, 24, "4 sg (~157 s, no long block), sub-1084sg2 (data file missing)"),
    ("03 (a) sg vs sg2", "long block", 0, 45, 24, "as 02"),
    ("03 (b) sg+cg → sg2 transfer", "long block", 66, 45, 24, "as 02"),
    ("04-A / 04-B Excel features", "Excel C_1, O_1, C_2, O_2 (derived)", 66, 46, 0, "Excel cohort: 12 IDs not in published data; sg2 absent"),
    ("04-B sensitivity (ID-verified)", "Excel", 55, 45, 0, "12 unverified Excel IDs"),
    ("05 Alpha reactivity (primary)", "4 × 50 s eyes-closed/open epochs", 66, 45, 25, "4 sg with 2 epochs (included only in n = 140 sensitivity)"),
    ("06 Offenders vs cg", "long block", 66, 45, 24, "as 02"),
    ("07 / 07a / 07b / 07e", "epochs (07–07b) or long block (07e)", 55, 45, 0, "restricted to Excel ∩ published, ID-verified"),
    ("07c / 07d transfer test set", "same epochs as training", 0, 0, 24, "sub-1084sg2 excluded (25 in extra row)"),
], columns=["Analysis", "Data segment", "cg", "sg", "sg2", "Exclusions / notes"])
sn["Total"] = sn[["cg", "sg", "sg2"]].sum(1)
sn = sn[["Analysis", "Data segment", "cg", "sg", "sg2", "Total", "Exclusions / notes"]]
sn.to_csv(A / f"{STEM}_TableSn.csv", index=False, encoding="utf-8-sig")
md = ["# Table S-n. Sample used in each analysis", "", "| " + " | ".join(sn.columns) + " |", "|" + "---|" * len(sn.columns)]
md += ["| " + " | ".join(str(v) for v in r) + " |" for r in sn.itertuples(index=False)]
(A / f"{STEM}_TableSn.md").write_text("\n".join(md) + "\n", encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(t1.assign(**{"p offenders vs cg": t1["p offenders vs cg"].map(pf), "p sg vs sg2": t1["p sg vs sg2"].map(pf)}).drop(columns="test").to_string())
print(sn.to_string())
