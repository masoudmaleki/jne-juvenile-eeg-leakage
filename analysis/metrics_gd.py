"""Golden Distance (GD) — proje uyarlaması (çizimsiz).

Kaynak: Melek M. & Melek N. (2025), Iranian J. Sci. Technol. Trans. Electr. Eng., doi:10.1007/s40998-025-00870-x;
referans uygulama: 13-Golden Distence/python code sosyal medya/files (2)/golden_distance.py (v1.0; salt okundu).

Tanım: N metrik (3..10, [0,1]) düzgün N-genin köşelerine yerleştirilir; her köşe sırası (permütasyon) için
  NAV = Σ r_i r_{i+1} / N  (döngüsel),  DCO = poligon ağırlık merkezinin orijine uzaklığı (shoelace).
  GD = sqrt((Av-NAV − 1)² + Av-DCO²); Av = tüm permütasyonlar üzerinden ortalama (N ≤ 8 tam sayım,
  N > 8 Monte Carlo). Düşük GD = daha iyi; ideal sistem GD = 0. Kontrol: Av-NAV = μ² − σ²/(N−1).
Projedeki varsayılan girdi: [ACC, Duyarlılık, Özgüllük, F1] (makaledeki örnek set); pozitif sınıf = suçlu (1).
"""
from itertools import permutations
import numpy as np

EXACT_LIMIT, N_SAMPLES = 8, 100_000
GD_METRICS = ("ACC", "Sensitivity", "Specificity", "F1")


def _nav_dco(r, perm_idx):
    N = r.shape[0]
    th = np.arange(N) * (2.0 * np.pi / N)
    ca, sa = np.cos(th), np.sin(th)
    ca_n, sa_n = np.roll(ca, -1), np.roll(sa, -1)
    rp = r[perm_idx]; rp_n = np.roll(rp, -1, axis=1)
    navs = np.sum(rp * rp_n, axis=1) / N
    x, y = rp * ca, rp * sa
    x_n, y_n = rp_n * ca_n, rp_n * sa_n
    cross = x * y_n - x_n * y
    A = 0.5 * np.sum(cross, axis=1)
    safe = np.abs(A) > 1e-12
    As = np.where(safe, A, 1.0)
    Cx = np.where(safe, np.sum((x + x_n) * cross, axis=1) / (6.0 * As), 0.0)
    Cy = np.where(safe, np.sum((y + y_n) * cross, axis=1) / (6.0 * As), 0.0)
    return navs, np.hypot(Cx, Cy)


def golden_distance(metrics, n_samples=N_SAMPLES, seed=42):
    """GD, Av-NAV, Av-DCO döndürür (referans compute_gd ile aynı hesap)."""
    r = np.asarray(metrics, dtype=np.float64)
    N = r.shape[0]
    if not 3 <= N <= 10:
        raise ValueError(f"metrik sayısı 3..10 olmalı, {N} verildi")
    if N <= EXACT_LIMIT:
        perm_idx = np.array(list(permutations(range(N))), dtype=np.intp)
    else:
        rng = np.random.default_rng(seed)
        perm_idx = np.stack([rng.permutation(N) for _ in range(n_samples)]).astype(np.intp)
    navs, dcos = _nav_dco(r, perm_idx)
    nav, dco = float(navs.mean()), float(dcos.mean())
    return dict(gd=float(np.hypot(nav - 1.0, dco)), nav=nav, dco=dco,
                nav_closed=float(r.mean() ** 2 - r.var() / (N - 1)))


def confusion_metrics(tp, fp, tn, fn):
    """ACC, Duyarlılık, Özgüllük, F1 (pozitif = 1). Tanımsız durumda 0."""
    acc = (tp + tn) / max(tp + fp + tn + fn, 1)
    sen = tp / max(tp + fn, 1)
    spe = tn / max(tn + fp, 1)
    f1 = 2 * tp / max(2 * tp + fp + fn, 1)
    return dict(ACC=acc, Sensitivity=sen, Specificity=spe, F1=f1)


def gd_from_predictions(y_true, y_pred):
    """İkili gerçek / tahmin etiketlerinden [ACC, Sen, Spe, F1] ve GD."""
    y_true = np.asarray(y_true).astype(int); y_pred = np.asarray(y_pred).astype(int)
    tp = int(((y_true == 1) & (y_pred == 1)).sum()); tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum()); fn = int(((y_true == 1) & (y_pred == 0)).sum())
    m = confusion_metrics(tp, fp, tn, fn)
    return dict(**m, **{f"gd_{k}": v for k, v in golden_distance([m[k] for k in GD_METRICS]).items()},
                tp=tp, fp=fp, tn=tn, fn=fn)
