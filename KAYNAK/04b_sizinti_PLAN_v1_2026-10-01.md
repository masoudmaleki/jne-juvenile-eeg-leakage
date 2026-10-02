# 04-B Sızıntı gösterimi: plan v1 (2026-10-01, ONAYLANDI)

**Kararlar:**
- Kurtosis birincil analizde içeride, duyarlılık analizinde dışarıda.
- Kol 2'de RF permütasyonu yapılmaz.
- Naif kolda k = 100 ve 10-fold.
- Uygulama notu: SVM'de AUC için Platt olasılığı yerine `decision_function` kullanılır. Denek skoru, deneğin satırlarındaki karar değerlerinin ortalamasıdır.

Bu plan, 04_05_PLAN_v2'deki 04-B bölümünün yerine geçer ve 04-A bulgularına göre güncellenmiştir.

**Amaç:** Yayımlanan Excel öznitelikleriyle kurulan naif bir pipeline'ın ne kadar şişkin doğruluk ürettiğini göstermek. Aynı veriyle denek bazlı, doğru kurulmuş pipeline'ın gerçek düzeyi bunun karşısına konacak. Bu bir yöntem gösterimi; suçlu ile kontrol arasında bir bulgu iddiası değildir.

## Veri
- **Kaynak:** `CAR_FREC_DATS.mat`. Excel ile birebir aynı; tek farkı, Excel'de 0 bayt olan THETA C_2 B12 kanalının burada dolu olması.
- **Örneklem:** Excel'in 112 deneği (cg 66, sg 46). Etiket Excel'deki `Label` sütunu; kontrol için önekle karşılaştırıldı.
- **Satır yapısı:** her satır bir denek × koşul-epok (C_1, O_1, C_2, O_2), toplam 448 satır. Her satırda 4 bant × 128 kanal × 7 istatistik = 3.584 öznitelik.
- **Kurallar (a, b):**
  - `Label` ve `Subject` öznitelik matrisine girmez; kodda `assert` ile kontrol edilir.
  - Bir deneğin 4 satırı aynı etiketi taşır; kodda `assert` ile kontrol edilir.
  - StandardScaler her hücrede CV'nin içinde fit edilir.
- **Kurtosis:** Birincil analizde, yayımlandığı haliyle içeride bırakılır. Naif bir kullanıcı da onu içeride bırakırdı ve iki kolda aynı öznitelik seti kullanılır. Kurtosis'in çıkarıldığı versiyon (3.072 öznitelik) duyarlılık analizidir.

## Kol 1: Naif pipeline (literatürde sık görülen hata)
1. **Seçim tüm veride:** 448 satırın tamamında ANOVA F ile en iyi k = 100 öznitelik seçilir (`SelectKBest(f_classif)`). Seçim CV'den önce yapılır.
2. **Satır bazlı CV:** `StratifiedKFold(10, shuffle=True)`. Aynı deneğin epokları hem eğitim hem test kümesine düşebilir.
3. **Model:** StandardScaler (kat içinde) → **SVM** (RBF, C = 1, γ = "scale", `probability=True`) ya da **RF** (500 ağaç).
4. **Metrik:** satır düzeyinde ROC-AUC, doğruluk ve dengeli doğruluk.
5. Seed'leri farklı 10 tekrar yapılır; ortalaması raporlanır.

## Kol 2: Denek bazlı iç içe CV (doğru pipeline)
1. **Dış döngü:** `StratifiedGroupKFold(5, shuffle=True)`, grup = denek, 20 tekrar. Bir deneğin 4 satırı hep aynı katta kalır.
2. **İç döngü:** `StratifiedGroupKFold(5)`.
   - Pipeline: StandardScaler → `SelectKBest(f_classif, k)` → model. Ölçekleme ve seçim iç döngüde kalır.
   - Taranan değerler: k ∈ {10, 50, 100, 500}. SVM için C ∈ {0,1, 1, 10}. RF için yalnız k (500 ağaç).
3. **Denek skoru:** deneğin 4 satırının dış-kat olasılıklarının ortalaması.
4. **Birincil metrik:** denek düzeyinde ROC-AUC. Ek olarak dengeli doğruluk ve kıyaslama için satır düzeyinde AUC.

## Ayrıştırma (2 × 2, iç içe olmayan, k = 100 sabit, varsayılan parametreler)
| | Seçim tüm veride | Seçim CV içinde |
|---|---|---|
| Satır bazlı 10-fold (shuffle) | **N1 = Kol 1** | N2 |
| Denek bazlı GroupKFold (5) | N3 | N4 (iç içe olmayan; Kol 2 ile kıyas için) |

Sızıntı payları şöyle okunur:
- N1 − N2 farkı: öznitelik seçiminden kaynaklanan sızıntı.
- N2 − N4 farkı: epok ya da denek sızıntısı.

## Sıfır kontrolü (sinyal yokken ne olur?)
- Etiketler **denek düzeyinde** karıştırılır, böylece bir deneğin 4 satırı birlikte kalır. Bu 200 kez yapılır.
  - **Kol 1:** SVM ve RF, ikisi de karıştırılmış etiketlerle çalıştırılır.
  - **Kol 2:** yalnızca SVM, ve permütasyon başına 5 tekrarla. RF'nin iç içe permütasyonu yaklaşık 2 saat süreceği için yapılmaz.
- **Beklenti:** Naif kol, karıştırılmış etiketlerde de AUC > 0,5 üretir; bunun nedeni seçim yanlılığı ve aynı deneğin epoklarının hem eğitimde hem testte olması. Doğru kol ≈ 0,5 üretir.
- Raporlanacak: karıştırılmış etiketli sıfır dağılımının ortalaması ve %95 aralığı. Her iki kol için gerçek AUC'nin bu dağılıma göre permütasyon p değeri.

## Duyarlılık analizleri (yalnızca gerçek değer)
1. Kimliği doğrulanmış 100 denek (cg 55, sg 45).
2. Kurtosis çıkarılmış (3.072 öznitelik).
3. Yalnız göz kapalı epoklar (C_1, C_2; 224 satır).

## Raporlama ve yorum
- **Ana tablo:** her satırda bir hücre (N1–N4, Kol 2) × model (SVM, RF). Sütunlar: AUC, dengeli doğruluk, karıştırılmış etiketli AUC.
- **Ana mesaj:** Naif ve doğru pipeline arasındaki fark. Bu fark, aynı veriyle raporlanabilecek "yüksek doğruluk" ile gerçek ayrıştırma gücü arasındaki farktır.
- **Dikkat:** Kol 2'nin sonucu, 03'teki 14 öznitelikli sonucu doğrulamak ya da çürütmek için kullanılmaz. Excel kohortu yayımlanan veriyle aynı değil (04-A Bölüm 5).
- GD ve NAoSP, formülleriniz verildiğinde eklenecek.

## Çıktılar ve süre
- `04b_leakage_v1_<tarih>.py`, `_results.csv`, `_null.npz`, `_rapor.md`.
- Tahmini süre: 15 çekirdekte 30–60 dakika. RF ile Kol 2 gerçek değeri en uzun süren kısım.

## Kararınız gereken noktalar
1. **Kurtosis:** birincil analizde içeride (yayımlandığı haliyle), duyarlılıkta dışarıda olsun mu?
2. **Kol 2 RF permütasyonu:** yapılmasın mı (yaklaşık 2 saat)? Yapılmazsa yalnızca SVM'nin sıfır dağılımı raporlanır.
3. **Naif kol için k = 100 ve 10-fold uygun mu?** Literatürdeki tipik değerler bunlar. Raporda bunların "örnek naif pipeline" olduğu belirtilir.
