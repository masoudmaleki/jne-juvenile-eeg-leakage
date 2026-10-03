"""11 v1 (2026-10-03) - K1 bütünlük denetimi (tanım: CLAUDE.md, "2026-10-03 Gönderim öncesi kontroller").

v1.0.0/ içindeki her dosyanın boyutu ve SHA256'sı, analysis/ds006923_v1.0.0_manifest.csv ile karşılaştırılır
(OpenNeuro ds006923 1.0.0). Karar kuralı yok; yalnız rapor. v1.0.0/ YALNIZ OKUNUR.
Uyuşmayan ya da eksik dosya v1.0.0/ DIŞINDA <proje>/_redownload/ klasörüne yeniden indirilir
(https://data.nemar.org/on006923/v1.0.0/<yol>), SHA256'sı manifestle doğrulanır; Excel dosyasıysa değerleri
v1.0.0/code/CAR_FREC_DATS.mat'teki karşılığıyla karşılaştırılır (en büyük mutlak fark).
Okur:  analysis/ds006923_v1.0.0_manifest.csv, v1.0.0/**
Yazar: analysis/11_integrity_v1_2026-10-03_{results,extra,redownload}.csv, _rapor.md; _redownload/<yol>
Var olan çıktının üzerine yazılmaz.
"""
from pathlib import Path
import hashlib
import sys
import time
import urllib.request
import numpy as np
import pandas as pd

A = Path(__file__).resolve().parent
ROOT = A.parent
DATA = ROOT / "v1.0.0"
REDL = ROOT / "_redownload"
STEM = "11_integrity_v1_2026-10-03"
MANIFEST = A / "ds006923_v1.0.0_manifest.csv"
URL = "https://data.nemar.org/on006923/v1.0.0/"
OUT = {k: A / f"{STEM}_{k}" for k in ("results.csv", "extra.csv", "redownload.csv", "rapor.md")}
STATS = ["Power", "RMS", "Standarddesv", "Minimun", "Maximun", "Symetry", "Kurtosis"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def excel_vs_mat(xlsx, rel):
    """İndirilen Excel dosyasının 112 x 7 değeri ile .mat'teki karşılığı arasındaki en büyük mutlak fark."""
    from scipy.io import loadmat
    name = Path(rel).stem                                   # FR_Dats_band_<BANT>_EP_<KOŞUL>_can_<KANAL>
    band = name.split("_band_")[1].split("_EP_")[0]
    cond, chan = name.split("_EP_")[1].split("_can_")
    M = loadmat(DATA / "code" / "CAR_FREC_DATS.mat", squeeze_me=True, struct_as_record=False, simplify_cells=True)["Datos"]
    recs = M[band][cond][chan]
    mat = pd.DataFrame([{k: r[k] for k in ["Subject", "Label"] + STATS} for r in recs])
    x = pd.read_excel(xlsx)
    info = dict(xlsx_shape=str(x.shape), xlsx_columns=";".join(map(str, x.columns)), mat_rows=len(mat))
    if x.shape[0] != len(mat) or not set(STATS) <= set(x.columns):
        return dict(info, compared=False, max_abs_diff=np.nan, ids_identical=False)
    ids_ok = ("Subject" in x.columns and list(x["Subject"].astype(str)) == list(mat["Subject"].astype(str))
              and "Label" in x.columns and list(x["Label"].astype(int)) == list(mat["Label"].astype(int)))
    d = np.abs(x[STATS].to_numpy(float) - mat[STATS].to_numpy(float))
    return dict(info, compared=True, n_values=int(d.size), max_abs_diff=float(d.max()), ids_identical=bool(ids_ok))


def main():
    for p in OUT.values():
        if p.exists():
            sys.exit(f"DUR: {p.name} zaten var; üzerine yazılmaz.")
    man = pd.read_csv(MANIFEST, dtype={"path": str, "sha256": str})
    assert man.path.is_unique
    local = {p.relative_to(DATA).as_posix(): p for p in DATA.rglob("*") if p.is_file()}
    rows, t0 = [], time.time()
    for i, r in enumerate(man.itertuples(index=False), 1):
        p = local.get(r.path)
        if p is None:
            rows.append(dict(path=r.path, storage=r.storage, expected_size=r.size_bytes, local_size=np.nan,
                             expected_sha256=r.sha256, local_sha256="", status="missing"))
            continue
        size = p.stat().st_size
        h = sha256(p)
        status = "ok" if (size == r.size_bytes and h == r.sha256) else ("size_mismatch" if size != r.size_bytes else "hash_mismatch")
        rows.append(dict(path=r.path, storage=r.storage, expected_size=r.size_bytes, local_size=size,
                         expected_sha256=r.sha256, local_sha256=h, status=status))
        if i % 250 == 0:
            print(f"{i}/{len(man)}  {time.time() - t0:.0f} s", flush=True)
    res = pd.DataFrame(rows)
    res["local_size"] = res.local_size.astype("Int64")
    extra = pd.DataFrame([dict(path=k, local_size=p.stat().st_size, local_sha256=sha256(p))
                          for k, p in sorted(local.items()) if k not in set(man.path)],
                         columns=["path", "local_size", "local_sha256"])
    res.to_csv(OUT["results.csv"], index=False, encoding="utf-8-sig")
    extra.to_csv(OUT["extra.csv"], index=False, encoding="utf-8-sig")
    counts = res.status.value_counts().reindex(["ok", "size_mismatch", "hash_mismatch", "missing"], fill_value=0)
    print(counts.to_string(), f"\nmanifestte olmayan yerel dosya: {len(extra)}", flush=True)

    # ---------------- uyuşmayan / eksik dosyalar: v1.0.0 DIŞINA yeniden indir, doğrula
    rd = []
    for r in res[res.status != "ok"].itertuples(index=False):
        dst = REDL / r.path
        d = dict(path=r.path, status_local=r.status, url=URL + r.path, expected_size=r.expected_size, expected_sha256=r.expected_sha256)
        try:
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                tmp = dst.with_name(dst.name + ".part")
                with urllib.request.urlopen(urllib.request.Request(d["url"], headers={"User-Agent": "integrity-check"}), timeout=300) as u, \
                        open(tmp, "wb") as f:
                    for chunk in iter(lambda: u.read(1 << 20), b""):
                        f.write(chunk)
                tmp.rename(dst)
            d.update(downloaded=True, dl_size=dst.stat().st_size, dl_sha256=sha256(dst))
            d["dl_matches_manifest"] = bool(d["dl_size"] == r.expected_size and d["dl_sha256"] == r.expected_sha256)
            if dst.suffix == ".xlsx":
                d.update(excel_vs_mat(dst, r.path))
        except Exception as e:                                # ağ hatası vb.: rapora yazılır
            d.update(downloaded=False, error=f"{type(e).__name__}: {e}")
        rd.append(d)
    rdf = pd.DataFrame(rd)
    rdf.to_csv(OUT["redownload.csv"], index=False, encoding="utf-8-sig")

    # ---------------- rapor
    md = [f"# K1 bütünlük denetimi (11 v1, 2026-10-03)", "",
          "Tanım: CLAUDE.md, \"2026-10-03 Gönderim öncesi kontroller\". Karar kuralı yok; yalnız rapor. v1.0.0/ yalnız okundu.", "",
          f"- Manifest: {len(man)} dosya (toplam {man.size_bytes.sum():,} bayt). Yerel v1.0.0/: {len(local)} dosya.",
          f"- ok: {counts['ok']}; size_mismatch: {counts['size_mismatch']}; hash_mismatch: {counts['hash_mismatch']}; missing: {counts['missing']}.",
          f"- Manifestte olmayan yerel dosya: {len(extra)}" + (" (" + "; ".join(extra.path) + ")" if 0 < len(extra) <= 10 else "") + ".", ""]
    bad = res[res.status != "ok"]
    if len(bad):
        md += ["## Uyuşmayan ya da eksik dosyalar", "", "| Dosya | Durum | Beklenen boyut | Yerel boyut |", "|---|---|---|---|"]
        md += [f"| {r.path} | {r.status} | {r.expected_size} | {'' if pd.isna(r.local_size) else r.local_size} |" for r in bad.itertuples()]
        md += ["", "## Yeniden indirme (_redownload/, v1.0.0 dışında)", ""]
        for d in rd:
            if d.get("downloaded"):
                s = (f"- {d['path']}: indirildi, {d['dl_size']} bayt, SHA256 manifestle "
                     f"{'AYNI' if d['dl_matches_manifest'] else 'FARKLI'}.")
                if d.get("compared"):
                    s += (f" .mat karşılaştırması: {d['n_values']} değer ({d['xlsx_shape']}), en büyük mutlak fark {d['max_abs_diff']:.3g}; "
                          f"Subject/Label sırası {'aynı' if d['ids_identical'] else 'FARKLI'}.")
                elif "compared" in d:
                    s += f" .mat ile karşılaştırılamadı (biçim: {d['xlsx_shape']}; sütunlar: {d['xlsx_columns']})."
            else:
                s = f"- {d['path']}: İNDİRİLEMEDİ ({d.get('error')})."
            md.append(s)
    else:
        md.append("Bütün dosyalar manifestle aynı; yeniden indirme gerekmedi.")
    OUT["rapor.md"].write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
