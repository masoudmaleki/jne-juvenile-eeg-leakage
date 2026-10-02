# 03 Batch negatif kontrolü: analiz planı (v1, 2026-10-01, KOD YAZILMADI)

## Amaç
Kayıt dönemi ya da kayıt ortamından kaynaklanan (batch) farkın EEG özniteliklerinde ayırt edilebilir olup olmadığını test etmek.
- **(a) sg ile sg2.** İkisi de suçlu ve aynı kurumda kaydedildi; yalnızca kayıt dönemi farklı (2021-07…09 ve 2021-12…2022-06).
- **(b) sg + cg ile eğitilen model sg2'yi nasıl sınıflıyor?**

Bu bir negatif kontrol, bulgu analizi değil. Sonucu ne çıkarsa çıksın, öznitelik ve model seçiminde geri dönüş yapılmaz.

## Veri
- Kaynak: `02_features_v3_2026-10-01_roi.csv`. Segment `full`, model `primary` (fixed, 3–30 Hz).
- **Öznitelikler (14):** posterior ve global ROI'den {rel_delta, rel_theta, rel_alpha, rel_beta, ap_exponent, ap_offset, iaf_fooof}.
  - Göreli güçlerin toplamı 1 olduğu için aralarında doğrusal bağımlılık var. L2 cezası bunu tolere eder; ek dönüşüm yapılmaz.
  - ap_offset mutlak güce duyarlıdır; batch'i en çok taşıyan öznitelik olması beklenir. Birincil sette kalır.
- **Eksik değer:** iaf_fooof iki yerde eksik: 1 denekte posterior ROI, sub-1105sg2'de global ROI. Eğitim katında hesaplanan medyanla doldurulur; bu iç döngünün parçasıdır.
- **Örneklem:** (a) sg 45 + sg2 24 = 69. (b) eğitim sg 45 + cg 66 = 111; test sg2 24.

## Model ve doğrulama
- **Pipeline:** medyan imputasyon → StandardScaler → LogisticRegression (L2, `class_weight="balanced"`). Her denek tek satır, dolayısıyla bütün bölmeler denek bazlı.
- **Dış döngü:** stratified 5-fold, 20 tekrar.
- **İç döngü:** stratified 5-fold. C ∈ logspace(−3, 3, 13), seçim ölçütü ROC-AUC.
- **Rastgelelik:** seed = 20261001. Tüm ön işleme, seçim ve ölçekleme iç döngüde kalır.
- **Birincil metrik:** ROC-AUC (tekrarlar üzerinden ortalama ve 2,5–97,5 persentil aralığı).
- **İkincil metrikler:** dengeli doğruluk, Golden Distance, NAoSP. Bunlar ana sonuç olarak sunulmaz.
- **Permütasyon testi:** 1000 kez etiketler karıştırılır ve iç içe CV'nin tamamı yeniden çalıştırılır (hesap süresini kısaltmak için permütasyon başına 5 tekrar).
  - p = (k + 1) / 1001; k, gerçek AUC'den büyük ya da ona eşit permütasyon AUC'si sayısı.
  - İki birincil test var: α = 0,05 / 2 = 0,025 (Bonferroni).

## (b) için transfer tasarımı
- sg ile cg, (a) ile aynı iç içe CV ile ayrıştırılır. Elde edilen AUC sg–cg ayrışmasının referans değeridir.
- Her dış katta katın modeli şu iki kümeyi skorlar:
  - dışarıda tutulan cg denekleri,
  - 24 sg2 deneğinin tamamı.
- Bir sg2 deneğinin skoru tüm katların ortalamasıdır. Bir cg deneği yalnızca dışarıda tutulduğu katta skorlanır.
- **Birincil sonuç:** transfer AUC'si, yani sg2 ile dışarıda tutulmuş cg skorlarının ayrışması. Ek olarak sg2'nin "suçlu" sınıflanma oranı (eşik 0,5) raporlanır.
- **Permütasyon:** eğitimdeki sg/cg etiketleri 1000 kez karıştırılır; her seferinde transfer AUC'si yeniden hesaplanır.
- **Betimsel alt analiz:** zamanca örtüşen cg alt kümesi (Mayıs–Haziran 2022, n = 9). n küçük olduğu için test yapılmaz.

## Yorum kuralları (önceden)
| Sonuç | Yorum |
|---|---|
| (a) AUC anlamlı > 0,5 | Kayıt dönemi farkı özniteliklerden ayırt edilebiliyor. sg–cg ayrışmasının bir kısmı batch olabilir. |
| (a) anlamsız | Bu güçle tespit edilebilir bir batch etkisi yok. Batch etkisinin olmadığı anlamına gelmez (aşağıdaki güç notuna bakın). |
| (b) sg–cg AUC yüksek, transfer AUC ≈ 0,5 | sg–cg ayrışması suçlu olma durumuna genellenmiyor. Batch, kayıt dönemi ve sg'ye özgü özellikler açıklaması güçlenir. |
| (b) transfer AUC yüksek | Gerçek grup farkıyla uyumlu, ancak **kurum/site etkisiyle de uyumlu** (sg ve sg2 aynı kurum). Yani (b) site confound'unu dışlayamaz; yalnızca dönem açıklamasını zayıflatır. |

## Duyarlılık analizleri (birincilden sonra, aynı pipeline)
1. Atipik spektrumlu 2 denek (1105sg2, 1114sg2) hariç.
2. EMG indeksi ve teta/alfa eğimi kovaryat olarak eklenir; her öznitelikten eğitim katında kalıntılanarak çıkarılır.
3. Tam kesit yerine H1 segmenti; sonuçlar yan yana raporlanır.
4. ap_offset çıkarılır (mutlak güç ya da amplifikatör farkını ayırmak için).
5. Model knee (2–30 Hz) öznitelikleri.

## Güç ve yorum sınırı
- Hanley–McNeil yaklaşımıyla (a)'da 45'e karşı 24 denekle AUC'nin standart hatası 0,5 civarında yaklaşık 0,074. %80 güçle tespit edilebilecek en küçük etki AUC ≈ 0,70.
- Dolayısıyla anlamsız bir (a) sonucu, AUC < 0,70 düzeyindeki batch etkilerini dışlamaz. Bu sınırlılık makalede açıkça yazılacak.

## Önkoşul: Adım 0, betimsel tablo, model yok
sg ile sg2 yalnızca kayıt dönemiyle değil, başka değişkenlerle de farklı olabilir. Bunlar (a)'nın yorumunu bozar. Modelden önce participants.tsv'den şu değişkenler için betimsel tablo çıkarılır:
- yaş, eğitim yılı, okul terki, madde kullanımı (esrar, kokain, alkol), ilk kullanım yaşı,
- suç tipi, tekrar suç, çete üyeliği, sosyoekonomik tabaka.

Ayrıca atipik spektrumlu 2 deneğin ve "R² kuralıyla çok kanal kaybeden" 4 deneğin hepsinin sg2'de olması (a)'yı doğrudan etkiler. Bu durum sonuçların yanında raporlanır.

## Çıktılar (planlanan)
- `03_batch_negcontrol_v1_<tarih>.py`
- `03_..._results.csv`: AUC, dengeli doğruluk, GD, NAoSP, p
- `03_..._perm_null.npz`
- `03_..._sg2_scores.csv`
- `03_..._coefs.csv`: katlar boyunca standartlaştırılmış katsayılar (yalnız betimsel)
- `03_..._rapor.md`
- Tahmini süre: 16 çekirdekte permütasyonlar dahil 15–30 dakika.

## Kararınız gereken noktalar
1. Permütasyonlarda dış döngü tekrarı 20 yerine 5 olsun mu? Gerçek değer 20 tekrarla hesaplanır.
2. Bonferroni α = 0,025 uygun mu?
3. Adım 0 (sg ile sg2 demografi karşılaştırması) modelden önce yapılsın mı? Önerim evet.
