"""03 - Adım 0: sg ile sg2 demografik/klinik karşılaştırma (yalnız (a) için confound kontrolü; EEG yok).
Örneklem: 02 v3 ROI dosyasındaki denekler (sg 45, sg2 24).
Kategorik: Fisher exact (2x2) / Fisher-Freeman-Halton yerine ki-kare (2xk; beklenen < 5 notu); sürekli: Welch t + Mann-Whitney.
Şiddet suçu tanımı (birincil): Type of crime 1 ∈ VIOLENT. Ek tanım: 4 suç sütunundan herhangi biri ∈ VIOLENT.
Okur: v1.0.0/participants.tsv, analysis/02_features_v3_2026-10-01_roi.csv
Yazar: analysis/03_step0_demografi_v1_2026-10-01.csv
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import fisher_exact, chi2_contingency, ttest_ind, mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "analysis"
VIOLENT = {"Homicide", "Sexual_Abuse", "Violence", "Abduction", "Kidnapping"}
CRIME = ["Type of crime 1", "Type of crime 2", "Type of crime 3", "Type of crime 4"]

p = pd.read_csv(ROOT / "v1.0.0" / "participants.tsv", sep="\t")
subs = pd.read_csv(OUT / "02_features_v3_2026-10-01_roi.csv", usecols=["subject"]).subject.unique()
p = p[p.participant_id.isin(subs)].copy()
p["g"] = p.participant_id.str.extract(r"(sg2|sg|cg)$")[0]
o = p[p.g.isin(["sg", "sg2"])].copy()
o["Violent crime (primary)"] = np.where(o["Type of crime 1"].isin(VIOLENT), "Yes", "No")
o["Violent crime (any)"] = np.where(o[CRIME].isin(VIOLENT).any(axis=1), "Yes", "No")
o["Stratum 1"] = np.where(o["Socioeconomic stratum"] == 1, "Yes", "No")

rows = []
for c in ["Violent crime (primary)", "Violent crime (any)", "Alcohol", "Marijuana", "Cocaine",
          "Consumer of psychoactive substances", "School dropout", "Gang member", "Recidivist",
          "Domestic violence", "Displaced by violence", "Stratum 1"]:
    t = pd.crosstab(o.g, o[c]).reindex(index=["sg", "sg2"], columns=["Yes", "No"], fill_value=0)
    pv = fisher_exact(t.values)[1]
    rows.append(dict(variable=c, type="binary", sg=f"{t.loc['sg', 'Yes']}/{t.loc['sg'].sum()}",
                     sg2=f"{t.loc['sg2', 'Yes']}/{t.loc['sg2'].sum()}",
                     sg_pct=round(100 * t.loc["sg", "Yes"] / t.loc["sg"].sum(), 1),
                     sg2_pct=round(100 * t.loc["sg2", "Yes"] / t.loc["sg2"].sum(), 1), test="Fisher exact", p=pv))
t = pd.crosstab(o.g, o["Type of crime 1"])
rows.append(dict(variable="Type of crime 1 (all categories)", type="categorical",
                 sg="; ".join(f"{k}:{v}" for k, v in t.loc["sg"].items() if v), sg2="; ".join(f"{k}:{v}" for k, v in t.loc["sg2"].items() if v),
                 test="chi-square (expected<5 cells; descriptive)", p=chi2_contingency(t.values)[1]))
for c in ["Age", "Years of education", "Age of first use"]:
    a, b = o.loc[o.g == "sg", c].dropna(), o.loc[o.g == "sg2", c].dropna()
    rows.append(dict(variable=c, type="continuous", sg=f"{a.mean():.2f} ± {a.std():.2f} (n={len(a)})",
                     sg2=f"{b.mean():.2f} ± {b.std():.2f} (n={len(b)})", test="Welch t", p=ttest_ind(a, b, equal_var=False).pvalue,
                     p_mannwhitney=mannwhitneyu(a, b).pvalue))
res = pd.DataFrame(rows)
fn = OUT / "03_step0_demografi_v1_2026-10-01.csv"
res.to_csv(fn, index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(res.assign(p=res.p.map(lambda x: f"{x:.2g}"), p_mannwhitney=res.get("p_mannwhitney").map(lambda x: "" if pd.isna(x) else f"{x:.2g}")).to_string())
print("yazıldı:", fn)
