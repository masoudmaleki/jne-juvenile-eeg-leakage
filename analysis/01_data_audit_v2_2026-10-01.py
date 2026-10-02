"""01 - Veri denetimi (salt okuma).

v1.0.0/ altındaki her denek için acq-epochs ve desc-preprocessed .set dosyalarını
scipy ile ham EEGLAB yapısı olarak açar; hiçbir ham dosyaya yazmaz.
Çıktı: analysis/01_data_audit_v2_2026-10-01.csv (denek x dosya başına bir satır)
       analysis/01_epoch_alignment_v2_2026-10-01.csv (her epoğun sürekli kayıttaki yeri)
Event kodları: 64 = göz kapalı (PostClosed), 128 = göz açık (PostOpen).
v2: veri harici .fdt'de olduğunda (dosya yoksa) başlık bilgisi raporlanır; C/O
segmentleri yalnızca 64/128 event'lerinden hesaplanır, diğer kodlar ayrı sütunda.
"""
from pathlib import Path
import json, re, sys
import numpy as np
import pandas as pd
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "v1.0.0"
OUT = ROOT / "analysis"
CODE = {64: "C", 128: "O"}


def load(p):
    return loadmat(p, squeeze_me=True, struct_as_record=False, simplify_cells=True)


def as_list(v):
    if isinstance(v, dict):
        return [v]
    if isinstance(v, (list, np.ndarray)):
        return list(v)
    return []


def ev_code(e):
    try:
        return int(e.get("edftype"))
    except (TypeError, ValueError):
        m = re.search(r"(\d+)", str(e.get("type", "")))
        return int(m.group(1)) if m else -1


def audit_file(p, kind):
    E = load(p)
    sr = float(E["srate"]); pnts = int(E["pnts"]); tr = int(E["trials"])
    data_ref = E["data"]
    if isinstance(data_ref, str):  # veri harici .fdt dosyasında
        fdt = p.parent / data_ref
        if fdt.exists():
            data = np.fromfile(fdt, dtype="<f4").reshape((int(E["nbchan"]), pnts * tr), order="F").reshape(int(E["nbchan"]), pnts, tr, order="F")
        else:
            data = None
    else:
        data = np.asarray(data_ref, dtype=np.float32)
        if data.ndim == 2:
            data = data[:, :, None]
    labels = [c["labels"] for c in as_list(E["chanlocs"])]
    ctypes = [str(c.get("type")) if isinstance(c.get("type"), str) and c.get("type") else "" for c in as_list(E["chanlocs"])]
    removed = [c.get("labels") for c in as_list(E["chaninfo"].get("removedchans", []))] if isinstance(E["chaninfo"], dict) else []
    evs = as_list(E["event"])
    codes = [ev_code(e) for e in evs]
    lats = [float(e["latency"]) for e in evs]  # örnek (1 tabanlı)
    t0 = E["etc"].get("T0") if isinstance(E["etc"], dict) else None
    ica = np.shape(E.get("icaweights"))
    if data is not None:
        flat = data.reshape(data.shape[0], -1)
        ch_sd = flat.std(axis=1)
        dstats = dict(
            data_rank=int(np.linalg.matrix_rank(flat[:, :: max(1, flat.shape[1] // 20000)].astype(np.float64))),
            n_flat_ch=int((ch_sd < 1e-6).sum()), n_nan=int(np.isnan(flat).sum()),
            median_ch_sd_uv=round(float(np.median(ch_sd)), 3))
    else:
        dstats = dict(data_rank=None, n_flat_ch=None, n_nan=None, median_ch_sd_uv=None)
    # Yalnızca göz kapalı/açık işaretleri
    co = [(c, l) for c, l in zip(codes, lats) if c in CODE]
    other = [(c, l) for c, l in zip(codes, lats) if c not in CODE]
    row = dict(
        file=kind, path=str(p.relative_to(ROOT)), size_mb=round(p.stat().st_size / 2**20, 2),
        setname=E.get("setname"), eeglab_filename=E.get("filename"),
        orig_bdf=(re.search(r"Original file:\s*(\S+)", " ".join(as_list(E.get("comments")) if not isinstance(E.get("comments"), str) else [E["comments"]])) or [None, None])[1],
        srate=sr, pnts_per_epoch=pnts, n_epochs=tr, duration_s=round(pnts * tr / sr, 3),
        data_in_file=data is not None, data_ref=data_ref if isinstance(data_ref, str) else "embedded",
        n_channels=int(E["nbchan"]), n_eeg=sum(1 for l in labels if re.fullmatch(r"[A-D]\d{1,2}", str(l))),
        n_eog=0, n_ecg=0,  # dosyada yok; harici kanallar removedchans içinde
        chan_types_field=";".join(sorted(set(ctypes))) or "empty",
        nonstandard_labels=";".join(l for l in labels if not re.fullmatch(r"[A-D]\d{1,2}", str(l))),
        removed_chans=";".join(map(str, removed)), ref=E.get("ref"),
        n_ica_comp=ica[0] if len(ica) == 2 else 0,
        **dstats,
        rec_datetime=("%04d-%02d-%02d %02d:%02d:%02d" % tuple(int(x) for x in t0)) if t0 is not None and np.size(t0) == 6 else None,
        n_events=len(evs), event_seq="".join(CODE.get(c, "?") for c in codes),
        event_types=";".join(str(e.get("type")) for e in evs),
        event_lat_s=";".join(f"{(l - 1) / sr:.2f}" for l in lats),
        has_CO_markers=bool(co),
        co_seq="".join(CODE[c] for c, _ in co), co_lat_s=";".join(f"{(l - 1) / sr:.2f}" for _, l in co),
        n_other_events=len(other),
        other_codes=";".join(sorted({str(c) for c, _ in other}, key=lambda x: int(x) if x.lstrip('-').isdigit() else 0)),
        other_lat_range_s=(f"{(min(l for _, l in other) - 1) / sr:.1f}-{(max(l for _, l in other) - 1) / sr:.1f}" if other else ""),
    )
    if kind == "preprocessed":
        # Segment sınırları yalnızca C/O işaretlerinden: her işaret bir sonrakine (ya da kayıt sonuna) kadar
        segs = []
        for i, (c, l) in enumerate(co):
            end = co[i + 1][1] if i + 1 < len(co) else pnts * tr + 1
            segs.append(f"{CODE[c]}:{(l - 1) / sr:.1f}-{(end - 1) / sr:.1f}({(end - l) / sr:.1f}s)")
        row["segments"] = " | ".join(segs)
        row["first_marker_s"] = round((co[0][1] - 1) / sr, 2) if co else None
        row["last_marker_s"] = round((co[-1][1] - 1) / sr, 2) if co else None
        row["tail_after_last_marker_s"] = round((pnts * tr - co[-1][1] + 1) / sr, 2) if co else None
        # Uzun kapalı blok: 3. C işaretinden bir sonraki C/O işaretine (yoksa kayıt sonuna)
        c_idx = [i for i, (c, _) in enumerate(co) if c == 64]
        if len(c_idx) >= 3:
            j = c_idx[2]
            end = co[j + 1][1] if j + 1 < len(co) else pnts * tr + 1
            row["long_closed_s"] = round((end - co[j][1]) / sr, 1)
            row["long_closed_ends_with_marker"] = j + 1 < len(co)
    else:
        row["epoch_event_seq"] = row["event_seq"]
        ure = as_list(E.get("urevent"))
        row["urevent_lat_s"] = ";".join(f"{(float(e['latency']) - 1) / sr:.2f}" for e in ure)
    return row, data, lats, codes, sr


def locate_epochs(ep, cont, sr, pre_lats):
    """Her epoğu sürekli kayıtta bul: tek kanalda FFT ile çapraz korelasyon, sonra tam epokta doğrula."""
    from scipy.signal import correlate
    rows = []
    ch = int(np.argmax(cont.std(axis=1)))
    x = cont[ch].astype(np.float64)
    for k in range(ep.shape[2]):
        tpl = ep[ch, :, k].astype(np.float64)
        n = len(tpl)
        if n > len(x):
            rows.append(dict(epoch=k + 1, start_s=None, corr=None, max_abs_diff_uv=None)); continue
        num = correlate(x, tpl - tpl.mean(), mode="valid", method="fft")
        cs = np.concatenate([[0], np.cumsum(x)]); cs2 = np.concatenate([[0], np.cumsum(x * x)])
        win_var = (cs2[n:] - cs2[:-n]) - (cs[n:] - cs[:-n]) ** 2 / n
        r = num / np.sqrt(np.maximum(win_var, 1e-12) * ((tpl - tpl.mean()) ** 2).sum())
        off = int(np.argmax(r))
        seg = cont[:, off:off + n]
        diff = float(np.abs(seg - ep[:, :, k]).max())
        rfull = float(np.corrcoef(seg.ravel(), ep[:, :, k].ravel())[0, 1])
        prev = [l for l in pre_lats if (l - 1) <= off]
        rows.append(dict(epoch=k + 1, start_s=round(off / sr, 3), end_s=round((off + n) / sr, 3),
                         corr_all_ch=round(rfull, 6), max_abs_diff_uv=round(diff, 6),
                         offset_from_marker_s=round((off - (prev[-1] - 1)) / sr, 3) if prev else None))
    return rows


def main():
    subs = sorted(p.name for p in DS.glob("sub-*") if p.is_dir())
    rows, align = [], []
    for i, s in enumerate(subs, 1):
        grp = re.search(r"(sg2|sg|cg)$", s).group(1)
        base = DS / s / "eeg" / f"{s}_task-restingstate"
        res = {}
        for kind, suf in [("epochs", "_acq-epochs_eeg.set"), ("preprocessed", "_desc-preprocessed_eeg.set")]:
            p = Path(str(base) + suf)
            sc = Path(str(base) + suf.replace(".set", ".json"))
            meta = json.loads(sc.read_text(encoding="utf-8")) if sc.exists() else {}
            if not p.exists():
                rows.append(dict(subject=s, group=grp, file=kind, error="missing")); continue
            try:
                r, d, lats, codes, sr = audit_file(p, kind)
                r.update(subject=s, group=grp, sidecar_duration_s=meta.get("RecordingDuration"),
                         sidecar_epoch_len_s=meta.get("EpochLength"),
                         sidecar_eog=meta.get("EOGChannelCount"), sidecar_ecg=meta.get("ECGChannelCount"))
                rows.append(r)
                if d is not None:
                    res[kind] = (d, [l for c, l in zip(codes, lats) if c in CODE], sr)
            except Exception as e:  # noqa
                rows.append(dict(subject=s, group=grp, file=kind, error=repr(e)))
        if "epochs" in res and "preprocessed" in res:
            for a in locate_epochs(res["epochs"][0], res["preprocessed"][0][:, :, 0], res["preprocessed"][2], res["preprocessed"][1]):
                a.update(subject=s, group=grp); align.append(a)
        print(f"[{i}/{len(subs)}] {s}", flush=True)

    df = pd.DataFrame(rows)
    front = ["subject", "group", "file", "data_in_file", "duration_s", "n_epochs", "n_channels", "n_eeg", "n_eog", "n_ecg",
             "has_CO_markers", "co_seq", "co_lat_s", "segments", "n_other_events", "other_codes"]
    front = [c for c in front if c in df.columns]
    df = df[front + [c for c in df.columns if c not in front]]
    f1 = OUT / "01_data_audit_v2_2026-10-01.csv"; f2 = OUT / "01_epoch_alignment_v2_2026-10-01.csv"
    df.to_csv(f1, index=False, encoding="utf-8-sig")
    al = pd.DataFrame(align)
    al = al[["subject", "group"] + [c for c in al.columns if c not in ("subject", "group")]]
    al.to_csv(f2, index=False, encoding="utf-8-sig")
    print("yazıldı:", f1, f2)


if __name__ == "__main__":
    main()
