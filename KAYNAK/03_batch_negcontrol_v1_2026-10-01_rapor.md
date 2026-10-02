# 03 Batch negatif kontrolü: sonuç raporu (2026-10-01)

**Plan:** `03_batch_negatif_kontrol_PLAN_v2_2026-10-01.md`. Çalışma plana göre yapıldı; plandan sapma yok.
**Betik:** `03_batch_negcontrol_v1_2026-10-01.py`. Seed 20261001. Toplam süre yaklaşık 47 dakika.
**Okunanlar:** `02_features_v3_2026-10-01_roi.csv`, `02_features_v2_..._subject_qc.csv`, `01_data_audit_v2_...csv`, `participants.tsv`. Ham veriye yazılmadı.

## Birincil sonuçlar
| Test | Metrik | Değer | Tekrarlar arası 2,5–97,5 | Permütasyon sıfır dağılımı (ort.; %97,5) | p (1000 perm.) | α |
|---|---|---|---|---|---|---|
| (a) sg (45) vs sg2 (24) | ROC-AUC | **0,629** | 0,539–0,709 | 0,498; 0,651 | **0,053** | 0,025 |
| (a) | Dengeli doğruluk | 0,592 | 0,500–0,678 | – | – | – |
| (b) transfer: held-out cg vs sg2 | Kat-içi ROC-AUC (100 kat) | **0,436** | 0,293–0,610 | 0,501; 0,647 | **0,77** | 0,025 |
| (b) | sg2'nin "suçlu" sınıflanma oranı | 0,372 | 0,228–0,522 | – | – | – |
| (b) referans: sg (45) vs cg (66) | ROC-AUC | **0,530** | 0,435–0,633 | (test edilmedi) | – | – |

Not: "2,5–97,5" sütunu CV tekrarları arasındaki oynaklığı gösteriyor. Bu bir örneklem güven aralığı değildir. Örneklemden kaynaklanan belirsizliğin ölçüsü permütasyon sıfır dağılımının genişliği: SD ≈ 0,077.

## Duyarlılık analizleri (yalnızca gerçek değer, 20 tekrar)
| Varyant | (a) AUC | (a) Dengeli doğruluk | (b) transfer AUC | (b) sg2 suçlu oranı | sg vs cg AUC |
|---|---|---|---|---|---|
| Birincil | 0,629 | 0,592 | 0,436 | 0,372 | 0,530 |
| 1. Atipik 2 denek hariç (sg2 = 22) | 0,609 | 0,586 | 0,457 | 0,395 | 0,530 |
| 2. EMG ve teta/alfa eğimi kalıntılanmış | 0,609 | 0,580 | 0,452 | 0,398 | 0,527 |
| 3. Yaş kalıntılanmış | 0,609 | 0,574 | 0,425 | 0,367 | 0,514 |
| 4. H1 segmenti | 0,576 | 0,556 | 0,526 | 0,428 | 0,565 |
| 5. ap_offset yok | 0,635 | 0,600 | 0,437 | 0,388 | 0,498 |
| 6. Knee modeli | 0,618 | 0,599 | 0,506 | 0,418 | 0,564 |

- Varyant 1, 2 ve 3'te (a) AUC'si aynı görünüyor, ama dördüncü basamakta farklı (0,6086, 0,6088, 0,6094). Bu tesadüf, hata değil.
- Atipik denekler sg2'de olduğu için, onları çıkarınca sg vs cg değeri birincil analizle birebir aynı kalıyor. Bu beklenen bir tutarlılık kontrolü.

## Önceden belirlenmiş kurallara göre yorum
- **(a) Anlamlı değil:** p = 0,053, α = 0,025. Kurala göre bu sonuç, özniteliklerin kayıt dönemi, şiddet profili, alkol ve yaştan oluşan karışık farka duyarsız olduğu lehine kanıttır. Sınırları:
  - Gözlenen AUC 0,63. Bu değer, %80 güçle tespit edilebilen en küçük etkinin (AUC ≈ 0,70) altında. Yani bu büyüklükte bir etki olsa bile bu örneklemde tespit edilemezdi; sonuç "etki yok" değil, "tespit edilebilir etki yok" anlamına geliyor.
  - p, düzeltme yapılmasaydı 0,05 sınırına çok yakın.
  - Duyarlılık analizlerinin hepsi 0,58–0,64 aralığında kaldı. H1 segmentinde en düşük değer (0,576).
- **(b) Önceden belirlenen yorum tablosu uygulanamıyor:**
  - Tablo, sg–cg ayrışmasının yüksek olduğunu varsayıyordu. Gerçekte sg vs cg AUC'si 0,53; yani model ne suçlu ile kontrolü ayırabiliyor ne de herhangi bir şeyi aktarabiliyor.
  - Transfer AUC'si 0,436 (p = 0,77). 0,5'in altında olması da anlamlı değil (alt kuyruk p ≈ 0,23).
  - Bu yüzden (b) ne kayıt dönemi açıklamasını ne de site açıklamasını sınayabiliyor. Bilgilendirici değil.
- **Betimsel:** dışarıda tutulan skorların ortalaması:
  - sg2: 0,43
  - Zamanca örtüşen cg (Mayıs–Haziran 2022, n = 9): 0,45
  - Diğer cg: 0,47

  Üçü de birbirine yakın.

## Asıl önemli bulgu (negatif kontrolün yan ürünü)
**Önceden belirlenmiş 14 spektral öznitelik suçlu (sg) ile kontrolü (cg) ayıramıyor: AUC 0,53; duyarlılık analizlerinde 0,50–0,56.**
- Bu bir hipotez testi değil, referans değer. Ama sonraki adım için belirleyici.
- Suçlu ile kontrol arasında güçlü bir madde kullanımı, sosyoekonomik ve site farkı olmasına rağmen ayrışma çıkmıyor. Bu, özniteliklerin bu farklara genel olarak duyarsız olduğu sonucuyla tutarlı.
- **Uyarı:** Bu sonucu gördükten sonra yeni öznitelik eklemek (bağlantısallık, entropi, kanal düzeyi gibi) çatallanan yollar (garden of forking paths) riski taşır. Yeni öznitelik eklenecekse, ana analizden önce CLAUDE.md'ye önceden belirlenmiş ek analiz olarak yazılmalı ve gerekçesi mevcut sonuçtan bağımsız olmalı.
- Katsayılar: `_coefs.csv`. Katlar arasında işaret tutarlılığı düşük. (a)'da işareti katların %95'inden fazlasında aynı kalan öznitelikler yalnızca posterior teta, global beta, global ve posterior delta ve global IAF. Seçilen C değerleri 0,003 ile 1000 arasında dağınık. Model kararlı bir sinyal yakalamıyor.

## Çıktılar (`analysis/`)
- `03_step0_demografi_v1_2026-10-01.csv` ve betiği
- `03_batch_negcontrol_v1_2026-10-01_results.csv`, `_sensitivity.csv`, `_transfer_folds.csv`, `_coefs.csv`, `_heldout_scores.csv`, `_perm_null.npz`
