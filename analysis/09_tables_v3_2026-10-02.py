"""09 v3 - Eksik tablolar (Table 2, S_leak, 3, 4, S3, S5) ve bütün tabloların LaTeX hâli (Table 1, S-n, S4 dahil).

ANALİZ DONDURULDU: yeni hesap yok. Yalnız kayıtlı CSV'ler ve raporlar okunur; seçme, yuvarlama, biçimlendirme.
Her tablo için md + csv + tex; tex yalnız table ortamı (booktabs), \\caption{[CAPTION]}, \\label{tab:<ad>}.
Kontrol: tablodaki her sayı kaynak CSV'den yeniden okunup aynı biçimle karşılaştırılır -> _check.csv.
Okur:  analysis/04b_*, 05_*, 06_*, 03_*, 02_*, 04a_*, 01_data_audit_v2_*.csv, 07*_results.csv, 07g_*, 09_tables_v1/v2 CSV'leri,
       ilgili raporlar (.md) ve ../CLAUDE.md (yalnız metin kanıtı için).
Yazar: analysis/09_tables_v3_2026-10-02_<Tablo>.{md,csv,tex}, analysis/09_tables_v3_2026-10-02_check.csv
"""
from pathlib import Path
import re
import sys
import pandas as pd

A = Path(__file__).resolve().parent
ROOT = A.parent
STEM = "09_tables_v3_2026-10-02"

# Grup etiketleri: ad kararı verilince yalnız bu sözlük değişir.
LABELS = {"sg": "sg", "sg2": "sg2", "cg": "cg", "offender": "offenders (sg + sg2)"}

NPERM_MIN_P = 1 / 201  # 200 permütasyon -> en küçük p


def relabel(s):
    s = re.sub(r"\bsg2\b", "\0SG2\0", str(s))
    s = re.sub(r"\bsg\b", LABELS["sg"], s)
    s = re.sub(r"\bcg\b", LABELS["cg"], s)
    return s.replace("\0SG2\0", LABELS["sg2"])


# ---------------------------------------------------------------- okuma
_CACHE = {}


def load(name, **kw):
    key = (name, tuple(sorted((k, str(v)) for k, v in kw.items())))
    if key not in _CACHE:
        p = A / name
        if name.endswith(".csv"):
            kw.setdefault("encoding", "utf-8-sig")
            kw.setdefault("encoding_errors", "replace")
            _CACHE[key] = pd.read_csv(p, **kw)
        else:
            _CACHE[key] = p.read_text(encoding="utf-8").splitlines()
    return _CACHE[key]


# ---------------------------------------------------------------- biçim
def fnum(v, d):
    s = f"{float(v):.{d}f}"
    if s.startswith("-") and float(s) == 0:
        s = s[1:]
    return s.replace("-", "−")


f2 = lambda v: fnum(v, 2)
f3 = lambda v: fnum(v, 3)
fint = lambda v: str(int(round(float(v))))
fg = lambda v: f"{float(v):g}".replace("-", "−")


def fp(v):
    v = float(v)
    if abs(v - NPERM_MIN_P) < 1e-9:
        return "≤ 0.005"
    if v < 0.001:
        return "< 0.001"
    return f"{v:.3f}"


def fpct(v):
    return f"{100 * float(v):.1f}%"


# ---------------------------------------------------------------- kayıt
REG = []


class Table:
    def __init__(self, name, title, columns):
        self.name, self.title, self.columns = name, title, list(columns)
        self.rows, self.notes = [], []

    def add(self, row):
        self.rows.append(row)

    def df(self):
        return pd.DataFrame(self.rows, columns=self.columns)

    def cell(self, rowid, col):
        if col == "note":
            return " ".join(self.notes)
        for r in self.rows:
            if r[self.columns[1] if self.columns[0] == "Panel" else self.columns[0]] == rowid:
                return str(r[col])
        raise KeyError((self.name, rowid, col))


def V(t, rowid, col, src, src_col, getter, fmt, **kw):
    """Kaynaktan bir sayı okur, biçimler, kayda alır; biçimli dizeyi döndürür."""
    val = getter(load(src, **kw))
    s = fmt(val)
    REG.append(dict(kind="num", table=t.name, row=rowid, col=col, shown=s, src=src, src_col=src_col,
                    getter=getter, fmt=fmt, kw=kw))
    return s


def T(t, rowid, col, shown, src, evidence):
    """Metin parametresi: kaynak dosyada kanıt dizesinin geçtiği satırı bulur, kayda alır; satır no döndürür."""
    lines = (ROOT / src).read_text(encoding="utf-8").splitlines() if src == "CLAUDE.md" else load(src)
    hits = [i + 1 for i, l in enumerate(lines) if evidence in l]
    if not hits:
        sys.exit(f"KANIT BULUNAMADI: {src}: {evidence!r}")
    REG.append(dict(kind="text", table=t.name, row=rowid, col=col, shown=shown, src=src, src_col=f"line {hits[0]}",
                    evidence=evidence, line=hits[0]))
    return hits[0]


def row_sel(**cond):
    def g(df):
        m = pd.Series(True, index=df.index)
        for k, v in cond.items():
            m &= df[k] == v
        assert m.sum() == 1, (cond, m.sum())
        return df[m].iloc[0]
    return g


def cv(col, **cond):
    sel = row_sel(**cond)
    return lambda df: sel(df)[col]


def fci(lo, hi):
    sep = ", " if (lo.startswith("−") or hi.startswith("−")) else "–"
    return f"{lo}{sep}{hi}"


# ---------------------------------------------------------------- çıktı
TEX_MAP = [("–", "--"), ("—", "---"), ("−", "$-$"), ("±", r"$\pm$"), ("×", r"$\times$"), ("≤", r"$\leq$"),
           ("≥", r"$\geq$"), ("→", r"$\rightarrow$"), ("∩", r"$\cap$"), ("≈", r"$\approx$"), ("²", r"$^{2}$"),
           ("µ", r"$\mu$"), ("·", r"$\cdot$"), ("√", r"$\surd$"), ("α", r"$\alpha$"), ("’", "'"), ("|", r"$|$"),
           ("~", r"$\sim$"), ("…", r"\ldots{}"), ("<", r"$<$"), (">", r"$>$")]


def tex_esc(s):
    s = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"),
                 ("$", r"\$"), ("{", r"\{"), ("}", r"\}"), ("^", r"\^{}")):
        s = s.replace(a, b)
    for a, b in TEX_MAP:
        s = s.replace(a, b)
    bad = sorted({c for c in s if ord(c) > 127})
    if bad:
        sys.exit(f"TeX'e çevrilmeyen karakter: {bad} in {s!r}")
    return s


def write_table(t, colspec=None, resize=True, panels=None):
    df = t.df()
    df.to_csv(A / f"{STEM}_{t.name}.csv", index=False, encoding="utf-8-sig")
    md = [f"# {t.title}", ""]
    md += ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    md += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    if t.notes:
        md += ["", "**Notes.** " + " ".join(t.notes)]
    (A / f"{STEM}_{t.name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    cols = [c for c in df.columns if not (panels and c == "Panel")]
    colspec = colspec or ("l" * 1 + "c" * (len(cols) - 1))
    tx = [r"\begin{table}[htbp]", r"\centering", r"\caption{[CAPTION]}", rf"\label{{tab:{t.name}}}", r"\footnotesize"]
    if resize:
        tx.append(r"\resizebox{\textwidth}{!}{%")
    tx += [rf"\begin{{tabular}}{{{colspec}}}", r"\toprule", " & ".join(tex_esc(c) for c in cols) + r" \\", r"\midrule"]
    last_panel = None
    for _, r in df.iterrows():
        if panels:
            if r["Panel"] != last_panel:
                if last_panel is not None:
                    tx.append(r"\midrule")
                tx.append(rf"\multicolumn{{{len(cols)}}}{{l}}{{\textit{{{tex_esc(r['Panel'])}}}}} \\")
                last_panel = r["Panel"]
        tx.append(" & ".join(tex_esc(r[c]) for c in cols) + r" \\")
    tx += [r"\bottomrule", r"\end{tabular}"]
    if resize:
        tx.append(r"}")
    if t.notes:
        tx += [r"\par\smallskip", r"\begin{minipage}{\textwidth}\raggedright\scriptsize",
               tex_esc("Notes. " + " ".join(t.notes)), r"\end{minipage}"]
    tx.append(r"\end{table}")
    (A / f"{STEM}_{t.name}.tex").write_text("\n".join(tx) + "\n", encoding="utf-8")


TABLES = []

# ================================================================ Table 2 (04-B sızıntı)
R04 = "04b_leakage_v1_2026-10-01_results.csv"
G04 = "04b_leakage_gd_v1_2026-10-02_results.csv"
REP04 = "04b_leakage_rapor_v2_2026-10-02.md"
t2 = Table("Table2", "Table 2. Leakage demonstration on the published Excel features (04-B, primary variant)",
           ["Pipeline", "CV unit", "Feature selection", "Row AUC", "Subject AUC", "Subject balanced accuracy",
            "Subject GD", "Shuffled-label null: metric", "Null mean [2.5–97.5]", "p"])
# CV birimi ve öznitelik seçiminin yeri: 04b raporu v2 ana tablosu (kanıt dizesi o satırda aranır)
DESIGN = {
    "N1": ("row-wise 10-fold", "whole data", "| **N1 naif** | satır 10-fold | tüm veride | RF"),
    "N2": ("row-wise 10-fold", "within CV", "| N2 | satır 10-fold | CV içinde"),
    "N3": ("subject-wise 5-fold", "whole data", "| N3 | denek 5-fold | tüm veride"),
    "N4": ("subject-wise 5-fold", "within CV", "| N4 | denek 5-fold | CV içinde"),
    "P": ("subject-wise 5-fold × 20, nested", "inner loop (k, C)", "| **P doğru, iç içe** | denek 5-fold × 20 | iç döngüde (k, C) | RF"),
}
NULLNAME = {"row_auc": "row AUC", "subj_auc": "subject AUC"}
for cell in ["N1", "N2", "N3", "N4", "P"]:
    for model in ["RF", "SVM"]:
        rid = f"{cell} {model}"
        sel = dict(variant="primary", cell=cell, model=model)
        cvu, fs, ev = DESIGN[cell]
        T(t2, rid, "CV unit", cvu, REP04, ev)
        T(t2, rid, "Feature selection", fs, REP04, ev)
        row = dict(Pipeline=rid, **{"CV unit": cvu, "Feature selection": fs})
        row["Row AUC"] = V(t2, rid, "Row AUC", R04, "row_auc", cv("row_auc", **sel), f2)
        sa = V(t2, rid, "Subject AUC", R04, "subj_auc", cv("subj_auc", **sel), f2)
        if cell == "P":
            lo = V(t2, rid, "Subject AUC", R04, "subj_auc_p2_5", cv("subj_auc_p2_5", **sel), f2)
            hi = V(t2, rid, "Subject AUC", R04, "subj_auc_p97_5", cv("subj_auc_p97_5", **sel), f2)
            sa = f"{sa} [{fci(lo, hi)}]"
        row["Subject AUC"] = sa
        row["Subject balanced accuracy"] = V(t2, rid, "Subject balanced accuracy", R04, "subj_ba", cv("subj_ba", **sel), f2)
        row["Subject GD"] = V(t2, rid, "Subject GD", G04, "subj_GD", cv("subj_GD", **sel), f2)
        r = row_sel(**sel)(load(R04))
        if pd.notna(r.null_metric):
            row["Shuffled-label null: metric"] = NULLNAME[r.null_metric]
            m = V(t2, rid, "Null mean [2.5–97.5]", R04, "null_mean", cv("null_mean", **sel), f2)
            lo = V(t2, rid, "Null mean [2.5–97.5]", R04, "null_p2_5", cv("null_p2_5", **sel), f2)
            hi = V(t2, rid, "Null mean [2.5–97.5]", R04, "null_p97_5", cv("null_p97_5", **sel), f2)
            row["Null mean [2.5–97.5]"] = f"{m} [{fci(lo, hi)}]"
            row["p"] = V(t2, rid, "p", R04, "p_perm", cv("p_perm", **sel), fp)
        else:
            row["Shuffled-label null: metric"] = row["Null mean [2.5–97.5]"] = row["p"] = "–"
        t2.add(row)
ids = "04a_excel_audit_v1_2026-10-01_ids.csv"
n_x = V(t2, "", "note", ids, "len(rows)", lambda d: len(d), fint)
n_x0 = V(t2, "", "note", ids, "label==0", lambda d: (d.label == 0).sum(), fint)
n_x1 = V(t2, "", "note", ids, "label==1", lambda d: (d.label == 1).sum(), fint)
nr_n = V(t2, "", "note", R04, "n_reps (N1 RF)", cv("n_reps", variant="primary", cell="N1", model="RF"), fint)
nr_p = V(t2, "", "note", R04, "n_reps (P RF)", cv("n_reps", variant="primary", cell="P", model="RF"), fint)
T(t2, "", "note", "200 permutations", REP04, "200 kez karıştırıldı")
t2.notes = [
    f"Published Excel-derived features (CAR_FREC_DATS.mat), {n_x} subjects ({LABELS['cg']} {n_x0}, {LABELS['sg']} {n_x1}); one row per subject × epoch.",
    f"N1–N4: {nr_n} CV repeats; P: {nr_p} repeats. Subject AUC/balanced accuracy/GD: row decision values averaged per subject.",
    "For P, the bracket gives the 2.5th–97.5th percentile across CV repeats (not a sampling CI).",
    "Shuffled-label null: labels permuted at subject level, 200 permutations; smallest attainable p = 1/201 (shown as ≤ 0.005).",
    "No permutation was run for the remaining cells (–).",
    f"GD = Golden Distance on [accuracy, sensitivity, specificity, F1], positive class {LABELS['sg']}; lower is better.",
    "The naive pipelines were built in this study to represent a common error; they are not attributed to the data owners.",
]
TABLES.append((t2, dict(colspec="llll" + "c" * 6, resize=True)))

# ================================================================ Table S_leak (04-B duyarlılık)
tsl = Table("TableS_leak", "Table S_leak. Leakage demonstration: sensitivity variants (subject AUC)",
            ["Variant", "N1 RF", "N1 SVM", "P RF", "P SVM"])
VARS = [("primary", "Primary (reference)"), ("verified_100", "ID-verified subjects only"),
        ("no_kurtosis", "Kurtosis features removed"), ("closed_only", "Eyes-closed epochs only")]
for v, lab in VARS:
    row = {"Variant": lab}
    for cell in ["N1", "P"]:
        for model in ["RF", "SVM"]:
            c = f"{cell} {model}"
            row[c] = V(tsl, lab, c, R04, "subj_auc", cv("subj_auc", variant=v, cell=cell, model=model), f2)
    tsl.add(row)
idm = "04a_excel_audit_v1_2026-10-01_id_match.csv"
n_ver = V(tsl, "", "note", idm, "best_is_same_id==True", lambda d: int((d.best_is_same_id == True).sum()), fint)
tsl.notes = [f"ID-verified: the {n_ver} Excel subjects whose published EEG matched their own ID (Table S5).",
             "Pipelines as in Table 2; N1 = naive (row-wise CV, selection on whole data), P = correct nested subject-wise CV."]
TABLES.append((tsl, dict(colspec="lcccc", resize=False)))

# ================================================================ Table 3 (05 birincil test)
R05 = "05_alpha_reactivity_v1_2026-10-02_results.csv"
D05 = "05_alpha_reactivity_v1_2026-10-02_descriptive.csv"
DKW = dict(header=[0, 1], index_col=0)
t3 = Table("Table3", "Table 3. Primary hypothesis test: posterior alpha reactivity index (ARI), offenders vs controls",
           ["Analysis", "n (offenders / cg)", "ARI median, offenders", "ARI median [Q1–Q3], cg", "U", "p",
            "Rank-biserial r [95% CI]", "HL shift [95% CI]", "Adjusted offender coefficient [95% CI]", "p (age)", "p (EMG)"])
NCOL = t3.columns[1]
RIDS = [("PRIMARY n=136 (Mann-Whitney)", "Primary: Mann–Whitney U"),
        ("sensitivity n=140 (short 4 sg: C1/O1)", f"Sensitivity: incl. short-recording {LABELS['sg']} (C1/O1 only)"),
        ("OLS ARI ~ offender + age + EMG (HC3)", "OLS: ARI ~ offender + age + EMG (HC3)"),
        ("OLS rank(ARI) ~ offender + age + EMG (HC3)", "OLS: rank(ARI) ~ offender + age + EMG (HC3)")]
cg_q = lambda q: (lambda d: d.loc["cg", ("ARI", q)])
for key, lab in RIDS:
    g = lambda c, k=key: cv(c, analysis=k)
    r = row_sel(analysis=key)(load(R05))
    row = {"Analysis": lab}
    if pd.notna(r.n_offender):
        a = V(t3, lab, NCOL, R05, "n_offender", g("n_offender"), fint)
        b = V(t3, lab, NCOL, R05, "n_cg", g("n_cg"), fint)
        row[NCOL] = f"{a} / {b}"
        row["ARI median, offenders"] = V(t3, lab, "ARI median, offenders", R05, "median_offender", g("median_offender"), f3)
        m = V(t3, lab, "ARI median [Q1–Q3], cg", R05, "median_cg", g("median_cg"), f3)
        q1 = V(t3, lab, "ARI median [Q1–Q3], cg", D05, "ARI 25% (cg)", cg_q("25%"), f3, **DKW)
        q3 = V(t3, lab, "ARI median [Q1–Q3], cg", D05, "ARI 75% (cg)", cg_q("75%"), f3, **DKW)
        row["ARI median [Q1–Q3], cg"] = f"{m} [{fci(q1, q3)}]"
        row["U"] = V(t3, lab, "U", R05, "U", g("U"), fint)
        row["p"] = V(t3, lab, "p", R05, "p", g("p"), fp)
        rb = [V(t3, lab, "Rank-biserial r [95% CI]", R05, c, g(c), f2) for c in ("rank_biserial", "rb_ci_low", "rb_ci_high")]
        row["Rank-biserial r [95% CI]"] = f"{rb[0]} [{fci(rb[1], rb[2])}]"
        hl = [V(t3, lab, "HL shift [95% CI]", R05, c, g(c), f2) for c in ("HL_shift", "HL_ci_low", "HL_ci_high")]
        row["HL shift [95% CI]"] = f"{hl[0]} [{fci(hl[1], hl[2])}]"
        row["Adjusted offender coefficient [95% CI]"] = row["p (age)"] = row["p (EMG)"] = "–"
    else:
        row[NCOL] = "n = " + V(t3, lab, NCOL, R05, "n", g("n"), fint)
        for c in ("ARI median, offenders", "ARI median [Q1–Q3], cg", "U", "Rank-biserial r [95% CI]", "HL shift [95% CI]"):
            row[c] = "–"
        row["p"] = V(t3, lab, "p", R05, "p", g("p"), fp)
        co = [V(t3, lab, "Adjusted offender coefficient [95% CI]", R05, c, g(c), f2) for c in ("coef_offender", "ci_low", "ci_high")]
        row["Adjusted offender coefficient [95% CI]"] = f"{co[0]} [{fci(co[1], co[2])}]"
        row["p (age)"] = V(t3, lab, "p (age)", R05, "p_age", g("p_age"), fp)
        row["p (EMG)"] = V(t3, lab, "p (EMG)", R05, "p_emg", g("p_emg"), fp)
    t3.add(row)
desc = []
for grp in ("sg", "sg2", "cg"):
    n = V(t3, "", "note", D05, f"ARI count ({grp})", lambda d, g_=grp: d.loc[g_, ("ARI", "count")], fint, **DKW)
    m = V(t3, "", "note", D05, f"ARI 50% ({grp})", lambda d, g_=grp: d.loc[g_, ("ARI", "50%")], f3, **DKW)
    q1 = V(t3, "", "note", D05, f"ARI 25% ({grp})", lambda d, g_=grp: d.loc[g_, ("ARI", "25%")], f3, **DKW)
    q3 = V(t3, "", "note", D05, f"ARI 75% ({grp})", lambda d, g_=grp: d.loc[g_, ("ARI", "75%")], f3, **DKW)
    desc.append(f"{LABELS[grp]} (n = {n}) {m} [{fci(q1, q3)}]")
t3.notes = [
    "ARI = (C − O)/(C + O), posterior ROI absolute alpha (8–13 Hz) power, eyes closed (C) and open (O) epochs of the first 4 minutes.",
    "Two-sided Mann–Whitney U, α = 0.05; rank-biserial r positive when offenders > cg; HL = Hodges–Lehmann shift (offenders − cg, ARI units); CIs bootstrap.",
    "OLS rows: HC3 robust SE; the offender coefficient is in ARI units (ARI model) or rank units (rank model); its p is in the p column.",
    "The interquartile range of the combined offender group is not recorded in the saved outputs; subgroup descriptives (no test), ARI median [Q1–Q3]: "
    + "; ".join(desc) + ".",
]
TABLES.append((t3, dict(colspec="l" + "c" * 10, resize=True)))

# ================================================================ Table 4 (06 + 03)
R06 = "06_null_quantification_v1_2026-10-02_results.csv"
R03 = "03_batch_negcontrol_v1_2026-10-01_results.csv"
S03 = "03_batch_negcontrol_v1_2026-10-01_sensitivity.csv"
t4 = Table("Table4", "Table 4. ROI-level analyses with 14 prespecified spectral features (06 and 03)",
           ["Analysis", "Comparison (n)", "AUC from mean score [bootstrap 95% CI]", "DeLong 95% CI",
            "Repeat-mean AUC [2.5–97.5]", "Significance threshold (null 97.5th pct.)", "p", "α", "Sensitivity variants, range"])
one = lambda c: (lambda d: d.iloc[0][c])
rid = "06: offenders vs cg (prespecified null quantification)"
row = {"Analysis": rid}
n1 = V(t4, rid, "Comparison (n)", R06, "n_offender", one("n_offender"), fint)
n2 = V(t4, rid, "Comparison (n)", R06, "n_cg", one("n_cg"), fint)
row["Comparison (n)"] = f"{LABELS['offender']} vs {LABELS['cg']} ({n1} / {n2})"
a = [V(t4, rid, "AUC from mean score [bootstrap 95% CI]", R06, c, one(c), f2) for c in ("auc_mean_prob", "boot_ci_low", "boot_ci_high")]
row["AUC from mean score [bootstrap 95% CI]"] = f"{a[0]} [{fci(a[1], a[2])}]"
d_ = [V(t4, rid, "DeLong 95% CI", R06, c, one(c), f2) for c in ("delong_ci_low", "delong_ci_high")]
row["DeLong 95% CI"] = fci(*d_)
r_ = [V(t4, rid, "Repeat-mean AUC [2.5–97.5]", R06, c, one(c), f2) for c in ("auc_rep_mean", "auc_rep_p2_5", "auc_rep_p97_5")]
row["Repeat-mean AUC [2.5–97.5]"] = f"{r_[0]} [{fci(r_[1], r_[2])}]"
for c in ("Significance threshold (null 97.5th pct.)", "p", "α", "Sensitivity variants, range"):
    row[c] = "–"
t4.add(row)
ROWS03 = [("(b) referans: sg vs cg", "ROC-AUC (20 tekrar)", "03(b) reference", "b_sgcg_auc_mean"),
          ("(a) sg vs sg2", "ROC-AUC (20 tekrar)", "03(a) negative control", "a_auc_mean"),
          ("(b) transfer: held-out cg vs sg2", "kat-içi ROC-AUC (100 kat)", "03(b) transfer (within fold)", "b_transfer_auc_mean")]
for test, metric, rid, scol in ROWS03:
    g = lambda c, t_=test, m_=metric: cv(c, test=t_, metric=m_)
    r = row_sel(test=test, metric=metric)(load(R03))
    row = {"Analysis": rid}
    a1, b1 = test.split(": ")[-1].replace("(a) ", "").split(" vs ")
    row["Comparison (n)"] = relabel(f"{a1} vs {b1} ({r.n})")
    REG.append(dict(kind="num", table=t4.name, row=rid, col="Comparison (n)", shown=relabel(r.n), src=R03, src_col="n",
                    getter=g("n"), fmt=relabel, kw={}))
    row["AUC from mean score [bootstrap 95% CI]"] = row["DeLong 95% CI"] = "–"
    m = V(t4, rid, "Repeat-mean AUC [2.5–97.5]", R03, "mean", g("mean"), f2)
    lo = V(t4, rid, "Repeat-mean AUC [2.5–97.5]", R03, "p2_5", g("p2_5"), f2)
    hi = V(t4, rid, "Repeat-mean AUC [2.5–97.5]", R03, "p97_5", g("p97_5"), f2)
    row["Repeat-mean AUC [2.5–97.5]"] = f"{m} [{fci(lo, hi)}]"
    if pd.notna(r.null_p97_5):
        row["Significance threshold (null 97.5th pct.)"] = V(t4, rid, "Significance threshold (null 97.5th pct.)", R03, "null_p97_5", g("null_p97_5"), f2)
        row["p"] = V(t4, rid, "p", R03, "p_perm", g("p_perm"), fp)
        row["α"] = V(t4, rid, "α", R03, "alpha", g("alpha"), f3)
    else:
        row["Significance threshold (null 97.5th pct.)"] = row["p"] = row["α"] = "–"
    lo = V(t4, rid, "Sensitivity variants, range", S03, f"min({scol})", lambda d, c=scol: d[c].min(), f2)
    hi = V(t4, rid, "Sensitivity variants, range", S03, f"max({scol})", lambda d, c=scol: d[c].max(), f2)
    row["Sensitivity variants, range"] = fci(lo, hi)
    t4.add(row)
nvar = V(t4, "", "note", S03, "len(rows)", lambda d: len(d), fint)
REP06 = "06_null_quantification_rapor_v4_2026-10-02.md"
T(t4, "", "note", "14 features", REP06, "03'teki 14 öznitelik")
T(t4, "", "note", "L2 logistic regression", REP06, "L2 lojistik regresyon (balanced)")
T(t4, "", "note", "1000 permutations", "03_batch_negcontrol_v1_2026-10-01_rapor.md", "p (1000 perm.)")
t4.notes = [
    "Features: 14 prespecified ROI-level features from the long eyes-closed block (posterior and global relative band power, aperiodic exponent and offset, IAF).",
    "Pipeline: median imputation → StandardScaler → L2 logistic regression (balanced), outer stratified 5-fold × 20 repeats, inner 5-fold for C.",
    "06: AUC computed from subject scores averaged over repeats, with class-stratified subject bootstrap and DeLong CIs; repeat-mean AUC with 2.5th–97.5th percentile across repeats (not a sampling CI).",
    "03: 1000 permutations; α = 0.025 per test (prespecified). 03(b) transfer: model trained on sg + cg, AUC of held-out cg vs sg2 within each fold, averaged over 100 folds.",
    f"Sensitivity range: minimum–maximum over the {nvar} rows of the 03 sensitivity file (primary and six variants).",
]
t4.notes = [relabel(n) for n in t4.notes]
TABLES.append((t4, dict(colspec="ll" + "c" * 7, resize=True)))

# ================================================================ Table S3 (öznitelik ve QC parametreleri)
REP02 = "02_features_v2_rapor_2026-10-01.md"
ts3 = Table("TableS3", "Table S3. Feature extraction and quality-control parameters (A) and group-wise QC summary (B)",
            ["Panel", "Item", "Setting", LABELS["sg"], LABELS["sg2"], LABELS["cg"], "Source"])
PARAMS = [
    ("Segment", "Fixed 465 s from the 3rd eyes-closed marker + 5 s; two halves H1, H2 (232.5 s each)", "CLAUDE.md",
     "Kesit: 3. göz kapalı işareti + 5 s'den başlayan sabit 465 s"),
    ("PSD", "Welch, 4 s Hann window, 50% overlap (0.25 Hz resolution)", "CLAUDE.md", "PSD: Welch, 4 s Hann penceresi, %50 örtüşme (0,25 Hz çözünürlük)"),
    ("Bands (relative power)", "delta 1–4, theta 4–8, alpha 8–13, beta 13–30 Hz; denominator = 1–30 Hz total; gamma not a feature (EMG control only)",
     "CLAUDE.md", "Göreli güç: delta 1–4, teta 4–8, alfa 8–13, beta 13–30 Hz; payda 1–30 Hz toplamı"),
    ("Aperiodic fit (FOOOF)", "fooof 1.1; primary: aperiodic mode 'fixed', 3–30 Hz", "CLAUDE.md",
     "FOOOF (fooof 1.1, specparam kurulmayacak): BİRİNCİL = aperiodik 'fixed', 3–30 Hz"),
    ("Aperiodic fit, sensitivity", "'knee' mode, 2–30 Hz; sensitivity analysis only, no post hoc choice", "CLAUDE.md", "'knee', 2–30 Hz yalnızca duyarlılık analizi"),
    ("IAF", "Primary: strongest FOOOF peak in 7–13 Hz; secondary: centre of gravity in 7–13 Hz of the aperiodic-removed spectrum; no PSD argmax",
     "CLAUDE.md", "IAF: birincil = FOOOF'un 7–13 Hz'deki en güçlü tepesi"),
    ("EMG index", "Slope of log10 PSD vs log10 f, 30–40 Hz (flatter/positive = more muscle); covariate in group analyses", "CLAUDE.md",
     "EMG indeksi = log10 PSD – log10 f doğrusal eğimi, 30–40 Hz"),
    ("Channel exclusion", "Primary FOOOF R² < 0.9 OR EMG index robust z > 3 (median + 3·1.4826·MAD, one-sided); determined on the full segment, same set for halves",
     "CLAUDE.md", "Kanal dışlanır: birincil FOOOF R² < 0,9 VEYA EMG indeksi robust z > 3"),
    ("ROI features", "Computed from the mean spectrum of the retained channels", "CLAUDE.md", "ROI öznitelikleri kalan kanalların ortalama spektrumundan hesaplanır"),
    ("Atypical-spectrum rule", "> 25% of channels (> 32/128) excluded → subject flagged; only the EMG rule applied, ROI from all remaining channels; included in primary, excluded in sensitivity analyses",
     "CLAUDE.md", "Kanalların > %25'i (> 32/128) dışlanırsa denek \"atipik spektrum\" olarak bayraklanır"),
    ("Vigilance", "Theta/alpha ratio in 30 s windows; slope (log10 ratio per min) as vigilance index; features also for H1 and H2",
     "CLAUDE.md", "30 s pencerelerde teta/alfa oranı zaman serisi kaydedilir, eğimi (log oran / dk)"),
    ("EMG index caveat", "Includes the roll-off of the preprocessing low-pass FIR filter; valid as a relative index only", REP02, "EMG indeksi filtre etkisi içeriyor"),
]
for item, setting, src, ev in PARAMS:
    ln = T(ts3, item, "Setting", setting, src, ev)
    ts3.add({"Panel": "A. Parameters (prespecified)", "Item": item, "Setting": setting, LABELS["sg"]: "", LABELS["sg2"]: "",
             LABELS["cg"]: "", "Source": f"{src}, line {ln}"})
QC = "02_features_v2_2026-10-01_subject_qc.csv"
D02 = "02_descriptive_by_group_v2_2026-10-01.csv"
row = {"Panel": "B. QC summary, median [Q1–Q3]", "Item": "Subjects processed (n)", "Setting": "", "Source": QC}
for grp in ("sg", "sg2", "cg"):
    row[LABELS[grp]] = V(ts3, "Subjects processed (n)", LABELS[grp], QC, f"count(group=={grp})", lambda d, g_=grp: (d.group == g_).sum(), fint)
ts3.add(row)
QCM = [("emg_slope_median_all", "EMG index (channel median, all channels)", f2),
       ("n_excluded", "Excluded channels, total", fg), ("n_excl_r2", "… due to R² < 0.9", fg), ("n_excl_emg", "… due to EMG z > 3", fg),
       ("r2_median_all_ch", "FOOOF R², channel median", f3), ("r2_roi_posterior", "FOOOF R², posterior ROI", f3),
       ("ta_slope_global", "Theta/alpha slope, global (log10 ratio/min)", f3), ("ta_slope_posterior", "Theta/alpha slope, posterior", f3)]
for met, lab, fm in QCM:
    row = {"Panel": "B. QC summary, median [Q1–Q3]", "Item": lab, "Setting": "", "Source": D02}
    for grp in ("sg", "sg2", "cg"):
        vals = [V(ts3, lab, LABELS[grp], D02, f"{c} (metric={met}, group={grp})", cv(c, metric=met, group=grp), fm) for c in ("median", "q1", "q3")]
        row[LABELS[grp]] = f"{vals[0]} [{fci(vals[1], vals[2])}]"
    ts3.add(row)
lab = "Atypical-spectrum subjects (> 32 channels excluded)"
row = {"Panel": "B. QC summary, median [Q1–Q3]", "Item": lab, "Setting": "", "Source": QC}
for grp in ("sg", "sg2", "cg"):
    row[LABELS[grp]] = V(ts3, lab, LABELS[grp], QC, f"count(n_excluded>32, group=={grp})",
                         lambda d, g_=grp: ((d.group == g_) & (d.n_excluded > 32)).sum(), fint)
ts3.add(row)
ts3.notes = ["Panel A: parameters fixed before any group comparison (CLAUDE.md, 'prespecified primary analysis'); line numbers refer to the files at commit time.",
             "Panel B: full 465 s segment, primary FOOOF fit; descriptive only, no group test. Subjects without a long eyes-closed block or with a missing data file are not included (Table S-n)."]
TABLES.append((ts3, dict(colspec="p{3.2cm}p{6.5cm}cccl", resize=True, panels=True)))

# ================================================================ Table S5 (04-A Excel denetimi)
STR = "04a_excel_audit_v1_2026-10-01_structure.csv"
NPT = "04a_excel_audit_v1_2026-10-01_n_points.csv"
AUD = "01_data_audit_v2_2026-10-01.csv"
ts5 = Table("TableS5", "Table S5. Integrity audit of the published Excel features (04-A)", ["Item", "Finding", "Source"])


def add5(item, finding, src):
    ts5.add({"Item": item, "Finding": finding, "Source": src})


it = "File structure"
nf = V(ts5, it, "Finding", STR, "len(rows)", lambda d: len(d), fint)
nb = V(ts5, it, "Finding", STR, "nunique(band)", lambda d: d.band.nunique(), fint)
nc = V(ts5, it, "Finding", STR, "nunique(cond)", lambda d: d.cond.nunique(), fint)
nch = V(ts5, it, "Finding", STR, "nunique(channel)", lambda d: d.channel.nunique(), fint)
bands = ", ".join(sorted(load(STR).band.unique()))
conds = ", ".join(sorted(load(STR).cond.unique()))
add5(it, f"{nf} files = {nb} bands ({bands}) × {nc} condition-epochs ({conds}) × {nch} channels; 7 statistics per file", STR)
it = "Empty (0-byte) files"
ne = V(ts5, it, "Finding", STR, "sum(empty_file)", lambda d: int(d.empty_file.astype(str).eq("True").sum()), fint)
er = load(STR)[load(STR).empty_file.astype(str).eq("True")]
names = "; ".join(f"FR_Dats_band_{r.band}_EP_{r.cond}_can_{r.channel}.xlsx" for r in er.itertuples())
T(ts5, it, "Finding", names, "04a_excel_audit_v1_2026-10-01_rapor.md", "FR_Dats_band_THETA_EP_C_2_can_B12.xlsx")
add5(it, f"{ne}: {names} (values available in CAR_FREC_DATS.mat)", STR)
it = "Subjects in the Excel files"
n_all = V(ts5, it, "Finding", ids, "len(rows)", lambda d: len(d), fint)
n0 = V(ts5, it, "Finding", ids, "label==0", lambda d: (d.label == 0).sum(), fint)
n1 = V(ts5, it, "Finding", ids, "label==1", lambda d: (d.label == 1).sum(), fint)
add5(it, f"{n_all} ({LABELS['cg']} {n0}, Label = 0; {LABELS['sg']} {n1}, Label = 1); no {LABELS['sg2']}", ids)
it = "Excel IDs absent from the published dataset"
miss = load(ids)[load(ids).in_dataset_dirs.astype(str) != "True"]
nm = V(ts5, it, "Finding", ids, "count(in_dataset_dirs==False)", lambda d: int((d.in_dataset_dirs.astype(str) != "True").sum()), fint)
add5(it, f"{nm}: " + relabel(", ".join(miss.excel_subject)), ids)
it = "Published subjects absent from the Excel files"
pub = lambda d: d[["subject", "group"]].drop_duplicates()
absent = lambda d: pub(d)[~pub(d).subject.isin(load(ids).bids_id)]
na = V(ts5, it, "Finding", AUD, "count(subject not in Excel ids)", lambda d: len(absent(d)), fint)
parts = []
for grp in ("sg2", "sg", "cg"):
    k = V(ts5, it, "Finding", AUD, f"count(absent, group=={grp})", lambda d, g_=grp: int((absent(d).group == g_).sum()), fint)
    parts.append(f"{LABELS[grp]} {k}")
add5(it, f"{na} ({', '.join(parts)})", f"{AUD}; {ids}")
it = "Statistics computed from 3 values"
smp = dict(sd_convention=load(NPT).sd_convention.iloc[1])
pop = dict(sd_convention=load(NPT).sd_convention.iloc[0])
kmin = V(ts5, it, "Finding", NPT, "kurtosis_min", one("kurtosis_min"), lambda v: fnum(v, 5))
kmax = V(ts5, it, "Finding", NPT, "kurtosis_max", one("kurtosis_max"), lambda v: fnum(v, 5))
msk = V(ts5, it, "Finding", NPT, "max_abs_skew", one("max_abs_skew"), lambda v: fnum(v, 6))
add5(it, f"Kurtosis {kmin}–{kmax} in every cell (population kurtosis of any 3 unequal values = 1.5); max absolute skewness = {msk} (bound for 3 values: 1/√2)", NPT)
it = "SD convention"
ins = V(ts5, it, "Finding", NPT, "mid_within_min_max (sample SD)", cv("mid_within_min_max", **smp), fpct)
inp = V(ts5, it, "Finding", NPT, "mid_within_min_max (population SD)", cv("mid_within_min_max", **pop), fpct)
add5(it, f"Sample SD (n − 1): reconstructed middle value within [Min, Max] in {ins} of cells vs {inp} with population SD", NPT)
it = "ID verification (log-power profile correlation)"
ver = lambda d: d[d.in_participants.astype(str) == "True"]
unk = lambda d: d[d.in_participants.astype(str) != "True"]
nok = V(ts5, it, "Finding", idm, "sum(best_is_same_id) among in_participants", lambda d: int((ver(d).best_is_same_id.astype(str) == "True").sum()), fint)
ntot = V(ts5, it, "Finding", idm, "count(in_participants)", lambda d: len(ver(d)), fint)
rmed = V(ts5, it, "Finding", idm, "median(r_same_id)", lambda d: ver(d).r_same_id.median(), f3)
rmin = V(ts5, it, "Finding", idm, "min(r_same_id)", lambda d: ver(d).r_same_id.min(), f3)
rmax = V(ts5, it, "Finding", idm, "max(r_same_id)", lambda d: ver(d).r_same_id.max(), f3)
mrg = V(ts5, it, "Finding", idm, "min(r_same_id − r_second)", lambda d: (ver(d).r_same_id - ver(d).r_second).min(), f3)
add5(it, f"Best match = own ID in {nok}/{ntot}; r with own ID median {rmed} (range {rmin}–{rmax}); smallest margin over the second-best match {mrg}", idm)
it = "Unknown Excel IDs"
nu = V(ts5, it, "Finding", idm, "count(not in_participants)", lambda d: len(unk(d)), fint)
ulo = V(ts5, it, "Finding", idm, "min(r_best) unknown", lambda d: unk(d).r_best.min(), f2)
uhi = V(ts5, it, "Finding", idm, "max(r_best) unknown", lambda d: unk(d).r_best.max(), f2)
add5(it, f"None of the {nu} matched a published recording: best r {ulo}–{uhi}", idm)
ts5.notes = ["Excel feature files are part of the published dataset (code/ folder); no Excel result can be reproduced from the published EEG because the cohorts differ.",
             "ID verification: z-scored log-power profiles (4 bands × 4 epochs × 128 channels) from the Excel files vs. the same profile recomputed from the published acq-epochs files; Pearson correlation."]
TABLES.append((ts5, dict(colspec="p{3.5cm}p{9cm}p{3.5cm}", resize=False)))

# ================================================================ Table 1 (v1 CSV'den yalnız tex)
T1 = "09_tables_v1_2026-10-02_Table1.csv"
t1src = load(T1)
hdr = {c: relabel(c).replace("Offenders", LABELS["offender"]) for c in t1src.columns}
t1 = Table("Table1", "Table 1. Participant characteristics and confounds (n = 140)", [hdr[c] for c in t1src.columns])
for i, r in t1src.iterrows():
    row = {}
    rid = r["Variable"]
    for c in t1src.columns:
        v = r[c]
        if c.startswith("p "):
            row[hdr[c]] = "–" if pd.isna(v) else V(t1, rid, hdr[c], T1, c, lambda d, i_=i, c_=c: d.loc[i_, c_], fp)
        else:
            row[hdr[c]] = relabel(v) if c != "Variable" else v
            if c != "Variable" and isinstance(v, str):
                REG.append(dict(kind="num", table="Table1", row=rid, col=hdr[c], shown=relabel(v), src=T1, src_col=c,
                                getter=lambda d, i_=i, c_=c: d.loc[i_, c_], fmt=relabel, kw={}))
    t1.add(row)
t1.notes = ["Mean ± SD; median [Q1–Q3] (n with data). p: offenders vs cg and sg vs sg2 (test column); < 0.001 shown as such. Source: participants.tsv."]
t1.notes = [n.replace("offenders", LABELS["offender"]) for n in t1.notes]
TABLES.append((t1, dict(colspec="p{3.2cm}" + "p{2.6cm}" * 4 + "ccl", resize=True)))

# ================================================================ Table S-n (v2 CSV'den yalnız tex)
TSN = "09_tables_v2_2026-10-02_TableSn.csv"
snsrc = load(TSN)
tsn = Table("TableSn", "Table S-n. Sample used in each analysis", [relabel(c) for c in snsrc.columns])
for i, r in snsrc.iterrows():
    row = {}
    rid = relabel(r["Analysis"])
    for c in snsrc.columns:
        cc = relabel(c)
        if c in ("cg", "sg", "sg2", "Total"):
            row[cc] = V(tsn, rid, cc, TSN, c, lambda d, i_=i, c_=c: d.loc[i_, c_], fint)
        else:
            row[cc] = relabel(r[c])
    tsn.add(row)
TABLES.append((tsn, dict(colspec="p{3.5cm}p{3.8cm}cccc p{5cm}".replace(" ", ""), resize=True)))

# ================================================================ Table S4 (v2 CSV + aynı kaynaklardan 2 ondalık)
TS4 = "09_tables_v2_2026-10-02_TableS4.csv"
s4 = load(TS4)
CI7G = "07g_auc_ci_v1_2026-10-02_results.csv"
SRC = {  # Analiz -> (aralık kaynağı, set, lo sütunu, hi sütunu, 07g anahtarı)
    "07 A": ("07_amplitude_decomp_v1_2026-10-02_results.csv", "A_log_abs", "subj_auc_p2_5", "subj_auc_p97_5", "07_A_log_abs"),
    "07 B": ("07_amplitude_decomp_v1_2026-10-02_results.csv", "B_relative", "subj_auc_p2_5", "subj_auc_p97_5", "07_B_relative"),
    "07a closed": ("07abc_source_decomp_v1_2026-10-02_results.csv", "07a_closed", "auc_p2_5", "auc_p97_5", "07a_closed"),
    "07a open": ("07abc_source_decomp_v1_2026-10-02_results.csv", "07a_open", "auc_p2_5", "auc_p97_5", "07a_open"),
    "07b": ("07abc_source_decomp_v1_2026-10-02_results.csv", "07b_closed_noC", "auc_p2_5", "auc_p97_5", "07b_closed_noC"),
    "07e": ("07de_transfer_longblock_v1_2026-10-02_results.csv", "07e_longblock", "auc_p2_5", "auc_p97_5", "07e_longblock"),
    "07c": ("07abc_source_decomp_v1_2026-10-02_results.csv", "07c_transfer", "auc_p2_5", "auc_p97_5", "07c_B_closed"),
    "07d A all": ("07de_transfer_longblock_v1_2026-10-02_results.csv", "07d_A_all", "auc_p2_5", "auc_p97_5", "07d_A_all"),
    "07d B all": ("07de_transfer_longblock_v1_2026-10-02_results.csv", "07d_B_all", "auc_p2_5", "auc_p97_5", "07d_B_all"),
    "07d B open": ("07de_transfer_longblock_v1_2026-10-02_results.csv", "07d_B_open", "auc_p2_5", "auc_p97_5", "07d_B_open"),
    "07f": ("07f_longblock_transfer_v1_2026-10-02_results.csv", "07f_longblock_transfer", "auc_p2_5", "auc_p97_5", "07f_B_longblock"),
}
ts4 = Table("TableS4", "Table S4. Exploratory analyses 07–07f: subject-level AUC, 95% CI (07g), permutation p and Golden Distance",
            ["Analysis", "Data", "Comparison", "AUC [repeat range]", "AUC (mean score)", "95% CI", "Null mean", "p",
             "BA", "GD", "Sen", "Spe", "F1", "sg2 classified offender", "AUC excl. atypical sg2"])
ts4.columns = [relabel(c) for c in ts4.columns]
for i, r in s4.iterrows():
    an = r["Analysis"]
    f, st, lo_c, hi_c, key = SRC[an]
    at = lambda c, i_=i: (lambda d: d.loc[i_, c])
    row = {"Analysis": an, "Data": relabel(r["Data"]), "Comparison": relabel(r["Comparison"])}
    a = V(ts4, an, "AUC [repeat range]", TS4, "AUC", at("AUC"), f2)
    lo = V(ts4, an, "AUC [repeat range]", f, f"{lo_c} (set={st})", cv(lo_c, set=st), f2)
    hi = V(ts4, an, "AUC [repeat range]", f, f"{hi_c} (set={st})", cv(hi_c, set=st), f2)
    row["AUC [repeat range]"] = f"{a} [{fci(lo, hi)}]"
    row["AUC (mean score)"] = "–" if pd.isna(r.AUC_meanscore) else V(ts4, an, "AUC (mean score)", TS4, "AUC_meanscore", at("AUC_meanscore"), f2)
    clo = V(ts4, an, "95% CI", CI7G, f"ci_low (set={key})", cv("ci_low", set=key), f2)
    chi = V(ts4, an, "95% CI", CI7G, f"ci_high (set={key})", cv("ci_high", set=key), f2)
    row["95% CI"] = fci(clo, chi)
    row["Null mean"] = V(ts4, an, "Null mean", TS4, "null_mean", at("null_mean"), f2)
    row["p"] = V(ts4, an, "p", TS4, "p", at("p"), fp)
    for src_c, col in (("BA", "BA"), ("GD", "GD"), ("Sen", "Sen"), ("Spe", "Spe"), ("F1", "F1"),
                       ("sg2_offender_rate", relabel("sg2 classified offender")), ("AUC_excl_atypical", relabel("AUC excl. atypical sg2"))):
        row[col] = "–" if pd.isna(r[src_c]) else V(ts4, an, col, TS4, src_c, at(src_c), f2)
    ts4.add(row)
ts4.notes = [
    "All exploratory; p values unadjusted; 200 permutations (smallest attainable p = 1/201, shown as ≤ 0.005).",
    "Source models (sg vs cg): AUC = mean over 20 repeats, bracket = 2.5th–97.5th percentile across repeats; 95% CI = class-stratified subject bootstrap of the AUC from repeat-averaged subject scores (AUC mean score).",
    "Transfer models (held-out cg vs sg2, within fold): AUC = mean of 100 fold AUCs; 95% CI = weighted subject bootstrap. 'AUC excl. atypical sg2': descriptive, without the two atypical-spectrum sg2 subjects.",
    "BA, GD, Sen, Spe, F1 at subject level, positive class sg. Smaller GD is better.",
]
ts4.notes = [relabel(n) for n in ts4.notes]
TABLES.append((ts4, dict(colspec="lp{2.6cm}p{2.6cm}" + "c" * 12, resize=True)))

# ================================================================ yaz
for t, kw in TABLES:
    write_table(t, **kw)

# ================================================================ kontrol
_CACHE.clear()  # kaynaklar diskten yeniden okunur
tabs = {t.name: t for t, _ in TABLES}
out = []
for e in REG:
    t = tabs[e["table"]]
    cell_txt = t.cell(e["row"], e["col"])
    if e["kind"] == "num":
        sv = e["getter"](load(e["src"], **e["kw"]))
        exp = e["fmt"](sv)
        ok = (exp == e["shown"]) and (e["shown"] in cell_txt)
        out.append(dict(table=e["table"], cell=f"{e['row']} | {e['col']}", table_value=e["shown"], source_file=e["src"],
                        source_column=e["src_col"], source_value=sv, match=ok))
    else:
        lines = (ROOT / e["src"]).read_text(encoding="utf-8").splitlines() if e["src"] == "CLAUDE.md" else load(e["src"])
        ok = e["evidence"] in lines[e["line"] - 1] and (e["col"] == "note" or e["shown"] in cell_txt)
        out.append(dict(table=e["table"], cell=f"{e['row']} | {e['col']}", table_value=e["shown"], source_file=e["src"],
                        source_column=e["src_col"], source_value=e["evidence"], match=ok))
chk = pd.DataFrame(out)
chk.to_csv(A / f"{STEM}_check.csv", index=False, encoding="utf-8-sig")
nbad = int((~chk.match).sum())
print(f"Tablolar: {', '.join(tabs)}")
print(f"Kontrol: {len(chk)} hücre, uyuşmayan {nbad}")
if nbad:
    print(chk[~chk.match].to_string())
    sys.exit(1)
