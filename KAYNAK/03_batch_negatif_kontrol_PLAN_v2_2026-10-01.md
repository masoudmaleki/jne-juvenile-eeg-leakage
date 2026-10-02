# 03 Batch negatif kontrolü: analiz planı v2 (2026-10-01, ONAYLANDI)

v1'den farkları:
- Adım 0 sonuçları eklendi.
- (a)'nın yorum tablosu yeniden yazıldı.
- Kurum ifadesi düzeltildi.
- (b)'deki transfer AUC'si artık her kat içinde ayrı hesaplanıyor.
- Yaş kalıntılama duyarlılık analizine eklendi.
- Permütasyonda 5 tekrar ve Bonferroni α = 0,025 onaylandı.

## Amaç
Kayıt dönemi ya da kayıt ortamı farkının EEG özniteliklerinde ayırt edilebilir olup olmadığını test etmek.
- **(a) sg ile sg2.** İkisi de suçlu. Aynı kurumda kaydedildikleri varsayılıyor, ama bu doğrulanmadı; tek dayanak dosya yolunun ikisinde de `D:\Infractores` olması. Kayıt dönemleri farklı: 2021-07…09 ve 2021-12…2022-06.
- **(b) sg + cg ile eğitilen model sg2'yi nasıl sınıflıyor?**

Bu bir negatif kontrol. Sonucu ne çıkarsa çıksın, öznitelik ve model seçiminde geri dönüş yapılmaz.

## Adım 0: sg (n=45) ile sg2 (n=24) karşılaştırması
Kaynak: `03_step0_demografi_v1_2026-10-01.csv`.

| Değişken | sg | sg2 | p |
|---|---|---|---|
| Şiddet suçu (birincil suç: Homicide, Sexual_Abuse, Violence, Abduction, Kidnapping) | 39/45 (%87) | 6/24 (%25) | 5×10⁻⁷ (Fisher) |
| Alkol | 22/45 (%49) | 19/24 (%79) | 0,02 (Fisher) |
| Yaş | 17,20 ± 1,14 | 16,62 ± 1,06 | 0,054 (Mann-Whitney); 0,041 (Welch t) |
| Kokain | 26/45 | 19/24 | 0,11 |
| Çete üyeliği | 17/45 | 4/24 | 0,10 |
| Esrar, madde kullanımı, okul terki, tekrar suç, tabaka 1, eğitim yılı, ilk kullanım yaşı | | | ≥ 0,16 |

Not: Şiddet suçu tanımı, 4 suç sütunundan herhangi birinin şiddet içermesi olarak genişletildiğinde de sonuç aynı (39/45'e karşı 6/24).

**Sonuç:** sg ile sg2 arasındaki karşılaştırma yalnızca kayıt dönemini değil, aynı anda suç profilini (şiddet), alkol kullanımını ve kısmen yaşı da içeriyor. Bu karşılaştırma saf bir batch testi değil.

## Veri
- Kaynak: `02_features_v3_2026-10-01_roi.csv`. Segment `full`, model `primary` (fixed, 3–30 Hz).
- **Öznitelikler (14):** posterior ve global ROI'den {rel_delta, rel_theta, rel_alpha, rel_beta, ap_exponent, ap_offset, iaf_fooof}.
- **Eksik değer:** iaf_fooof iki yerde eksik: 1 denekte posterior ROI, sub-1105sg2'de global ROI. Eğitim katının medyanıyla doldurulur.
- **Örneklem:** (a) 45 + 24 = 69. (b) eğitim 45 + 66 = 111; transfer kümesi 24 sg2.

## Model ve doğrulama
- **Pipeline:** medyan imputasyon → StandardScaler → LogisticRegression (L2, `class_weight="balanced"`, lbfgs). Her denek tek satır, bölmeler denek bazlı.
- **Dış döngü:** stratified 5-fold × 20 tekrar.
- **İç döngü:** stratified 5-fold. C ∈ logspace(−3, 3, 13), seçim ölçütü ROC-AUC. Seed = 20261001.
- **Birincil metrik:** ROC-AUC. Her tekrarda dışarıda tutulan tahminlerden tek bir AUC hesaplanır; 20 tekrarın ortalaması ve 2,5–97,5 persentil aralığı raporlanır.
- **İkincil metrik:** dengeli doğruluk (eşik 0,5). Golden Distance ve NAoSP bu adımda hesaplanmaz; asıl sınıflandırma adımında, kullanıcının vereceği formüllerle eklenecek.
- **Permütasyon:** 1000 kez etiket karıştırılır, iç içe CV'nin tamamı her seferinde 5 tekrarla yeniden çalıştırılır.
  - p = (k + 1) / 1001.
  - İki birincil test var ((a) ve (b) transfer): α = 0,025 (Bonferroni).

## (b) için transfer tasarımı: AUC kat içinde hesaplanır
- sg ile cg, iç içe CV ile ayrıştırılır. Elde edilen AUC sg–cg ayrışmasının referans değeridir.
- Her dış katta, o katın modeli (iç döngüde C seçilmiş) iki kümeyi skorlar: o katta dışarıda tutulan cg denekleri ve 24 sg2 deneğinin tamamı.
- O kat için AUC(sg2 ile dışarıda tutulan cg) hesaplanır. Birincil sonuç, bu AUC'nin 5 kat × 20 tekrar üzerinden ortalaması.
- **Skorların ortalaması alınmaz.**
- Ek olarak, her katta sg2'nin "suçlu" sınıflanma oranı (eşik 0,5) hesaplanır ve katlar üzerinden ortalaması raporlanır.
- **Permütasyon:** eğitimdeki sg/cg etiketleri 1000 kez karıştırılır, kat içi transfer AUC'si her seferinde aynı şekilde yeniden hesaplanır.
- **Betimsel alt analiz:** zamanca örtüşen cg alt kümesi (Mayıs–Haziran 2022, n = 9). Test yapılmaz.

## Yorum kuralları (önceden)
| Sonuç | Yorum |
|---|---|
| (a) AUC anlamlı > 0,5 | sg ile sg2 farkı kayıt dönemi, şiddet profili, alkol ve yaşla iç içe. Pozitif sonuç "batch" olarak yorumlanamaz. Söylenebilecek tek şey, özniteliklerin bu karışık farka duyarlı olduğu. |
| (a) anlamsız | Öznitelikler ne kayıt dönemine ne de bu klinik ve demografik farklara duyarlı. Bu, özniteliklerin bu tür farklara duyarsız olduğu lehine kanıttır (aşağıdaki güç sınırıyla birlikte). |
| (b) sg–cg AUC yüksek, transfer AUC ≈ 0,5 | sg–cg ayrışması diğer suçlu alt grubuna genellenmiyor. Ayrışma dönem, batch ya da sg'ye özgü bir özelliğe bağlı olabilir. |
| (b) transfer AUC yüksek | Gerçek grup farkıyla uyumlu, ama kurum ya da site etkisiyle de uyumlu. Aynı kurum varsayımı doğrulanmadığı için site confound'u dışlanamaz. Bu sonuç yalnızca kayıt dönemi açıklamasını zayıflatır. |

## Duyarlılık analizleri (aynı pipeline, yalnız gerçek değer; permütasyon yok)
1. Atipik spektrumlu 2 denek (1105sg2, 1114sg2) hariç.
2. EMG indeksi ve teta/alfa eğimi (global) her öznitelikten eğitim katında kalıntılanarak çıkarılır.
3. Yaş her öznitelikten eğitim katında kalıntılanarak çıkarılır.
4. Tam kesit yerine H1 segmenti; sonuçlar yan yana raporlanır.
5. ap_offset çıkarılır.
6. Model knee (2–30 Hz) öznitelikleri.

## Güç ve yorum sınırı
- Hanley–McNeil yaklaşımıyla (a)'da 45'e karşı 24 denekle AUC'nin standart hatası 0,5 civarında yaklaşık 0,074. %80 güçle tespit edilebilecek en küçük etki AUC ≈ 0,70.
- Dolayısıyla anlamsız bir (a) sonucu, AUC < 0,70 düzeyindeki etkileri dışlamaz.

## Çıktılar
`03_batch_negcontrol_v1_2026-10-01.py` ve aynı önekli şu dosyalar:
- `_results.csv`
- `_perm_null.npz`
- `_transfer_folds.csv`
- `_coefs.csv`
- `_sensitivity.csv`
- `_rapor.md`
