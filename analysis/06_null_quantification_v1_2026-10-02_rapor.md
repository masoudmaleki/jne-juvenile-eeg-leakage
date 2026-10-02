# 06 Null sonucun nicelenmesi: sonuç raporu (2026-10-02)

**Plan:** `04_05_PLAN_v2_2026-10-01.md` (06) ve CLAUDE.md. Plana uyuldu, sapma yok.
**Betik:** `06_null_quantification_v1_2026-10-02.py`. 03'ün `build()` ve `make_search()` fonksiyonları birebir kullanıldı. Seed 20261001.
**Okunanlar:** `02_features_v3_2026-10-01_roi.csv`, 03'ün girdileri.
**Çıktılar:** `06_null_quantification_v1_2026-10-02_{oof,results}.csv`

## Kurulum
- **Karşılaştırma:** suçlu (sg + sg2, n = 69) vs cg (n = 66), toplam 135 denek.
- **Öznitelikler:** 03'teki 14 öznitelik (posterior ve global ROI'den göreli güçler, aperiodik üs, offset, IAF). Veri 8 dakikalık göz kapalı blok.
- **Pipeline:** medyan imputasyon → StandardScaler → L2 lojistik regresyon (balanced). Dış döngü stratified 5-fold × 20 tekrar; iç döngü 5-fold ile C seçimi.

## Sonuç
| Ölçü | Değer |
|---|---|
| ROC-AUC, tekrar ortalaması (20 tekrar) | **0,511** (tekrarlar arası 2,5–97,5: 0,456–0,571) |
| Dengeli doğruluk, tekrar ortalaması | 0,503 |
| AUC, 20 tekrarın ortalama olasılığıyla | 0,538 |
| %95 GA, tabakalı denek bootstrap'ı (2000) | **0,440 – 0,633** |
| %95 GA, DeLong | 0,440 – 0,636 (SE 0,050) |

**Not:** Ortalama olasılıkla hesaplanan AUC (0,538), tekrar ortalamasından (0,511) biraz yüksek. Bunun nedeni, tekrarlar boyunca olasılıkların ortalanmasının skorlardaki gürültüyü azaltması. GA bu ortalama olasılıklar üzerinden hesaplandı (önceden belirlendiği gibi). Dolayısıyla GA'nın üst sınırı tutucu değil, hafif iyimser tarafta.

## Dışlanabilen en küçük etki
- **%95 güvenle AUC > 0,633 dışlanır** (bootstrap; DeLong ile 0,636).
- Eşdeğer Cohen d: **0,48** (DeLong'a göre 0,49). Yani orta ve daha büyük etkiler (d ≳ 0,5) bu öznitelik setiyle dışlanıyor. Küçük etkiler (d < 0,48) dışlanamıyor.
- Alt sınır 0,440 (d = −0,21).
- **Sınırlılık:** Bu GA, model eğitimindeki oynaklığı içermiyor. Tekrarlar arası aralık (0,456–0,571) bu oynaklığı ayrıca gösteriyor.

## Yorum
- Önceden belirlenmiş 14 aperiodik-düzeltilmiş ve göreli spektral öznitelik, suçlu ile kontrolü şans düzeyinde ayırıyor. Orta ve büyük etkiler %95 güvenle dışlanıyor.
- 05'te alfa reaktivitesinin rank-biserial GA'sı da benzer bir tablo veriyor: suçlu lehine r > 0,11 dışlanıyor, cg lehine r < −0,28 dışlanıyor.
- 07 ile karşılaştırma: Keşifsel 512 öznitelikli kanal düzeyi SVM, 4 dakikalık kapalı/açık epoklarda 0,73 AUC verdi. Ancak:
  - Bu ayrışma sg2'ye taşınmıyor (07c).
  - Göz açık ve frontal katkılı.
  - Önceden belirlenmiş öznitelik setinde görülmüyor.

  Makalede bu üç sonuç birlikte sunulmalı.
