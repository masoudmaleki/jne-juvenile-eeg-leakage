# 06 Null sonucun nicelenmesi: sonuç raporu v3 (2026-10-02)

**v3 düzeltmeleri** (DENETIM_RAPORU_2, E2 ve E5): Yorum bölümü 07e'ye göre güncellendi. ROI ile kanal düzeyi karşılaştırması aynı gruplar üzerinden yapılıyor. Sayılar değişmedi.

**v2 düzeltmesi (D2, DENETIM_RAPORU):** Nokta tahmini ve GA aynı yöntemle verildi. GA'nın yönüyle ilgili yanlış cümle düzeltildi. Sayılar değişmedi.

**Raporlanacak ifade:** **AUC 0,54 (%95 GA 0,44–0,63; tekrar ortalaması 0,51).**

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

**Not (v2):** GA, ortalama olasılıklar üzerinden hesaplandı (önceden belirlendiği gibi). Bu yüzden nokta tahmini de aynı yöntemden verilmeli: **AUC 0,54 (GA 0,44–0,63)**. Tekrar ortalaması 0,51 ayrıca belirtilir.

GA'nın yönü konusunda iki etki birbirine ters çalışıyor, dolayısıyla net yön belirsiz:
- **Dışlamayı zayıflatan (tutucu) yön:** Tekrarlar boyunca olasılıkların ortalanması AUC'yi, dolayısıyla U'yu yükseltir. U yükselince daha az etki dışlanmış olur.
- **Tutucu olmayan yön:** Model yeniden eğitildiğinde ortaya çıkan oynaklık GA'ya dahil değil; bu da GA'yı daraltır.

"Dışlanabilen etki" ifadesi bu yüzden yaklaşık olarak okunmalı. v1'deki "üst sınır hafif iyimser" cümlesi yanlıştı ve kaldırıldı.

## Dışlanabilen en küçük etki
- **%95 güvenle, yaklaşık olarak, AUC > 0,63 dışlanır** (bootstrap 0,633; DeLong 0,636).
- Eşdeğer Cohen d: **0,48** (DeLong'a göre 0,49). Yani orta ve daha büyük etkiler (d ≳ 0,5) bu öznitelik setiyle dışlanıyor. Küçük etkiler (d < 0,48) dışlanamıyor.
- Alt sınır 0,440 (d = −0,21).
- **Sınırlılık:** Bu GA, model eğitimindeki oynaklığı içermiyor. Tekrarlar arası aralık (0,456–0,571) bu oynaklığı ayrıca gösteriyor.

## Yorum
- Önceden belirlenmiş 14 ROI düzeyi öznitelik (aperiodik-düzeltilmiş ve göreli), suçlu (sg + sg2) ile kontrolü şans düzeyinde ayırıyor. Orta ve büyük etkiler yaklaşık olarak dışlanıyor (D2).
- 05'te alfa reaktivitesinin rank-biserial GA'sı da benzer bir tablo veriyor: suçlu lehine r > 0,11 dışlanıyor, cg lehine r < −0,28 dışlanıyor.
- **v3 (E2, E5): Bu null sonuç ROI ve model seçimine özgü.**
  - Aynı uzun göz kapalı blokta kanal düzeyi öznitelikler ve SVM, sg ile cg'yi 0,746 AUC ile ayırıyor (07e, p ≤ 0,005).
  - Aynı grupların ROI düzeyindeki karşılığı 03(b): sg vs cg 0,53. Bu iki analiz kayıt kesiti bakımından aynı, ama öznitelik çözünürlüğü, model, kanal dışlaması ve örneklem (111 ile 100) bakımından farklı.
  - Bu analizdeki (06) 0,54'ün düşük kalmasının bir nedeni, suçlu grubunda imzayı taşıdığına dair kanıt bulunmayan sg2'nin de yer alması (07c–d).
  - Kanal düzeyindeki ayrışmanın sg2'ye transfer ettiğine dair kanıt yok: 07c–d'de p = 0,19–0,29; uzun blok modeli için 07f'ye bakın.
  - **Makaledeki ifade:** "Önceden belirlenmiş ROI düzeyi öznitelikler suçlu ile kontrolü ayırmıyor". Bu ifade "dinlenim EEG'si grupları ayırmıyor" şeklinde genelleştirilmemeli.
