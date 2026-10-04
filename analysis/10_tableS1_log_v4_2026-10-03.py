"""10 v4 (2026-10-03) - Ek Tablo S1 (karar günlüğü), günlük v3 (52 satır; son satır 46; 44–46 K3 satırları).

Biçim ve etiket (tab:TableLog) 10 v3 ile aynı. v3'e göre fark: girdi TableS1_decision_log_en_v3.csv / _v3_notes.txt;
tek yer tutucu [[K3_RUN]] git geçmişinden bulunan kısa commit kimliğiyle doldurulur (13_matched_null_v1 sonuçları;
ek rapor ayrı commit'teyse "sonuç, ek" biçiminde). Kimlik tahmin edilmez: tam olarak bir commit bulunamazsa betik durur.
Doldurulmuş CSV: TableS1_decision_log_en_v3_filled.csv. Kontrol: 52 satır (son satır 46) ve hiç [[ ]] kalmamış.
Dönüşüm listesine tek ek: α -> $\\alpha$ (günlük v3'ün 45. satırında geçiyor; v2'de yoktu).

10 v2 açıklaması - Ek Tablo S1 (karar günlüğü): CSV'den LaTeX (longtable + booktabs) ve md.

v1'e göre yalnız LaTeX dizgisi değişti (metin aynı): dar sütunlara sığmayan uzun dosya adları (ör. 35 karakterlik
"03_batch_negatif_kontrol_PLAN_v1/v2", sütun 2.3 cm) sağ kenar boşluğuna taşmasın diye (a) her "_" ve "/" işaretinden
sonra satır kırılabilir (\\allowbreak), (b) dar sütunlar (2, 4, 5) sola yaslı (\\raggedright), satır sonu \\tabularnewline.
v1 dosyalarına dokunulmaz.

Yeni analiz yok. Metin değiştirilmez; yalnız LaTeX dönüşümü yapılır (özel karakter kaçışı, Unicode çevirisi,
[a]–[d] işaretleri üst simge).
Okur:  analysis/TableS1_decision_log_en_v3.csv, analysis/TableS1_decision_log_en_v3_notes.txt, git log (salt okuma)
Yazar: analysis/TableS1_decision_log_en_v3_filled.csv, analysis/10_tableS1_log_v4_2026-10-03.{tex,md};
       manuscript/tables/10_tableS1_log_v4_2026-10-03.tex (kopya)
Kontrol: .tex'te 52 veri satırı; her hücre geri çevrildiğinde CSV metniyle aynı. Değilse durur, kopya yazılmaz.
  (Düz ' ile kıvrık ’ LaTeX'te aynı karaktere gider; karşılaştırmada ikisi eşdeğer sayılır.)
Var olan çıktının üzerine yazılmaz: dosya varsa içeriği üretilecek içerikle birebir aynı olmalıdır, değilse durur.
"""
from pathlib import Path
import re
import subprocess
import sys
import pandas as pd

A = Path(__file__).resolve().parent
ROOT = A.parent
STEM = "10_tableS1_log_v4_2026-10-03"
SRC = A / "TableS1_decision_log_en_v3.csv"
FILLED = A / "TableS1_decision_log_en_v3_filled.csv"
NOTES = A / "TableS1_decision_log_en_v3_notes.txt"
MS_TABLES = ROOT / "manuscript" / "tables"
N_ROWS = 52
LAST_ROW = "46"
CAPTION = "Analysis log: every plan, decision rule and change, and whether each preceded the relevant result."
LABEL = "tab:TableLog"
HEAD = ["\\#", "Date (time)", "Decision or event", "Before the relevant result?", "Source"]
MD_HEAD = ["#", "Date (time)", "Decision or event", "Before the relevant result?", "Source"]
# İstenen yaklaşık genişlikler 0.6/2.0/7.4/3.0/2.6 cm; metin genişliği 153 mm olduğu için orantılı küçültüldü
# (toplam 14.4 cm + 4 sütun arası × 6 pt = 15.25 cm).
COLSPEC = r"@{}p{0.6cm}p{1.9cm}p{6.8cm}p{2.8cm}p{2.3cm}@{}"

# (kaynak, LaTeX) - sıra önemli; ters çevirme aynı listeyi tersten uygular
SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
PAIRS = [("/", r"/\allowbreak{}"), ("_", r"\_\allowbreak{}"), ("%", r"\%"), ("&", r"\&"), ("#", r"\#"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
         ("–", "--"), ("α", r"$\alpha$"), ("≈", r"$\approx$"), ("×", r"$\times$"), ("§", r"\S{}"), ("<", "$<$"), (">", "$>$"),
         ("‘", "`"), ("’", "'")]
POW_RE = re.compile(rf"10⁻([{SUP}]+)")
MARK_RE = re.compile(r"\[([a-d])\]")


def to_tex(s):
    for bad in ("\\", "$", "{", "}", "`"):
        if bad in s:
            sys.exit(f"DUR: kaynak metinde beklenmeyen karakter {bad!r}: {s[:80]!r}")
    s = POW_RE.sub(lambda m: "\0POW" + "".join(str(SUP.index(c)) for c in m.group(1)) + "\0", s)
    s = MARK_RE.sub(lambda m: f"\0SUP{m.group(1)}\0", s)
    for a, b in PAIRS:
        s = s.replace(a, b)
    s = re.sub("\0POW(\\d+)\0", r"$10^{-\1}$", s)
    s = re.sub("\0SUP([a-d])\0", r"\\textsuperscript{\1}", s)
    bad = sorted({c for c in s if ord(c) > 127})
    if bad:
        sys.exit(f"DUR: LaTeX'e çevrilmeyen karakter {bad} in {s[:80]!r}")
    return s


def put(path, text):
    """Yeni dosya yazar; dosya varsa üzerine yazmaz, içeriğin aynı olduğunu doğrular."""
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            sys.exit(f"DUR: {path.name} zaten var ve içeriği farklı; üzerine yazılmaz.")
        print(f"zaten var, içerik aynı: {path.name}")
    else:
        path.write_text(text, encoding="utf-8")


def apos(s):
    return s.replace("’", "'")   # LaTeX'te ikisi de ' olur


def from_tex(s):
    """to_tex'in tersi (kontrol için)."""
    s = re.sub(r"\\textsuperscript\{([a-d])\}", r"[\1]", s)
    s = re.sub(r"\$10\^\{-(\d+)\}\$", lambda m: "10⁻" + "".join(SUP[int(c)] for c in m.group(1)), s)
    for a, b in reversed(PAIRS):
        s = s.replace(b, a)
    return s


def git(*args):
    out = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def added_in(path):
    """Dosyayı depoya EKLEYEN commit(ler)in kısa kimlikleri."""
    return git("log", "--diff-filter=A", "--format=%h", "--", path)


def one(label, ids):
    if len(ids) != 1:
        sys.exit(f"DUR: {label} için tam bir commit bekleniyordu, bulunan: {ids}")
    return ids[0]


# Yer tutucu: git geçmişinden (tahmin yok)
k3_out = one("K3_RUN (13_matched_null_v1 sonuçları)", sorted(set(
    sum((added_in(f"analysis/13_matched_null_v1_2026-10-03{sfx}") for sfx in ("_results.csv", "_null_values.csv", "_rapor.md")), []))))
k3_add = one("K3_RUN (ek rapor)", added_in("analysis/13_matched_null_v1_2026-10-03_rapor_ek1.md"))
K3_RUN = k3_out if k3_add == k3_out else f"{k3_out}, {k3_add}"
FILL = {"[[K3_RUN]]": K3_RUN}
print("Yer tutucular:", FILL)

df = pd.read_csv(SRC, dtype=str, keep_default_na=False, encoding="utf-8-sig")
n_ph = {k: int(sum(v.count(k) for v in df.to_numpy().ravel())) for k in FILL}
if any(n == 0 for n in n_ph.values()):
    sys.exit(f"DUR: CSV'de bulunmayan yer tutucu var: {n_ph}")
df = df.apply(lambda col: col.map(lambda v: re.sub(r"\[\[\w+\]\]", lambda m: FILL.get(m.group(0), m.group(0)), v)))
left = sorted({m for v in df.to_numpy().ravel() for m in re.findall(r"\[\[[^\]]*\]\]", v)})
print(f"Kontrol (doldurma): {len(df)} satır (son satır {df['row'].iloc[-1]}); doldurulan yer tutucu sayıları {n_ph}; "
      f"kalan [[ ]]: {left if left else 'yok'}")
if len(df) != N_ROWS or df["row"].iloc[-1] != LAST_ROW or left or "[[" in "".join(df.to_numpy().ravel()) or "]]" in "".join(df.to_numpy().ravel()):
    sys.exit(f"DUR: satır sayısı {N_ROWS} değil, son satır {LAST_ROW} değil ya da doldurulmamış yer tutucu kaldı.")
assert list(df.columns) == ["row", "date_time", "decision_or_event", "before_relevant_result", "source"], list(df.columns)
if len(df) != N_ROWS:
    sys.exit(f"DUR: CSV'de {len(df)} satır var, {N_ROWS} bekleniyordu.")
notes = NOTES.read_text(encoding="utf-8-sig").strip()
if "[[" in notes:
    sys.exit("DUR: not metninde yer tutucu var.")

# ---------------------------------------------------------------- tex
ROW_END = r" \tabularnewline"
RAGGED = (1, 3, 4)                       # dar sütunlar (0 tabanlı): sola yaslı
RR = r"\raggedright "
head = " & ".join(HEAD) + ROW_END
tx = [r"\begingroup", r"\footnotesize", r"\setlength{\tabcolsep}{3pt}",
      rf"\begin{{longtable}}{{{COLSPEC}}}",
      rf"\caption{{{CAPTION}}}\label{{{LABEL}}}\\", r"\toprule", head, r"\midrule", r"\endfirsthead",
      rf"\multicolumn{{5}}{{@{{}}l}}{{\tablename~\thetable{{}} (continued)}}\\", r"\toprule", head, r"\midrule", r"\endhead",
      r"\midrule", r"\multicolumn{5}{r@{}}{\textit{continued on next page}}\\", r"\endfoot",
      r"\bottomrule", r"\endlastfoot", "% DATA-BEGIN"]
for r in df.itertuples(index=False):
    tx.append(" & ".join((RR if j in RAGGED else "") + to_tex(v) for j, v in enumerate(r)) + ROW_END)
tx += ["% DATA-END", r"\end{longtable}", r"\vspace{-0.5\baselineskip}",
       r"{\scriptsize\noindent " + to_tex(notes) + r"\par}", r"\endgroup"]
tex_path = A / f"{STEM}.tex"
md_path = A / f"{STEM}.md"
put(tex_path, "\n".join(tx) + "\n")

# ---------------------------------------------------------------- md
md = [f"# Table S1. {CAPTION}", "", "| " + " | ".join(MD_HEAD) + " |", "|" + "---|" * 5]
md += ["| " + " | ".join(v.replace("|", "\\|") for v in r) + " |" for r in df.itertuples(index=False)]
md += ["", notes]
put(md_path, "\n".join(md) + "\n")
put(FILLED, df.to_csv(index=False, lineterminator="\n"))

# ---------------------------------------------------------------- kontrol (diskten yeniden okunur)
df = pd.read_csv(FILLED, dtype=str, keep_default_na=False, encoding="utf-8")      # kontrol doldurulmuş CSV'ye karşı (diskten)
lines = tex_path.read_text(encoding="utf-8").splitlines()
data = lines[lines.index("% DATA-BEGIN") + 1:lines.index("% DATA-END")]
nbad = 0
if len(data) != N_ROWS:
    sys.exit(f"DUR: .tex'te {len(data)} veri satırı var, {N_ROWS} bekleniyordu.")
for i, (line, r) in enumerate(zip(data, df.itertuples(index=False))):
    assert line.endswith(ROW_END)
    raw = re.split(r"(?<!\\) & ", line[:-len(ROW_END)])                           # "\&" (kaçışlı) ayırıcı değildir
    assert all(c.startswith(RR) == (j in RAGGED) for j, c in enumerate(raw))
    cells = [from_tex(c[len(RR):] if j in RAGGED else c) for j, c in enumerate(raw)]
    if [apos(c) for c in cells] != [apos(v) for v in r]:
        nbad += 1
        print(f"UYUŞMUYOR satır {i + 1} (#{r[0]}):\n  tex: {cells}\n  csv: {list(r)}")
note_line = next(l for l in lines if l.startswith(r"{\scriptsize\noindent "))
notes_ok = apos(from_tex(note_line[len(r"{\scriptsize\noindent "):-len(r"\par}")])) == apos(notes)
n_sup = sum(l.count(r"\textsuperscript{") for l in lines)
print(f"Kontrol: {len(data)} veri satırı; CSV ile uyuşmayan {nbad}; not metni aynı: {notes_ok}; üst simge sayısı {n_sup} "
      f"(CSV + notlardaki [a]–[d] sayısı {len(MARK_RE.findall(SRC.read_text(encoding='utf-8-sig') + notes))})")
if nbad or not notes_ok:
    sys.exit("DUR: .tex metni CSV ile aynı değil; manuscript/tables kopyası yazılmadı.")
put(MS_TABLES / tex_path.name, tex_path.read_text(encoding="utf-8"))
print(f"yazıldı: {tex_path.name}, {md_path.name}; kopya -> manuscript/tables/")
