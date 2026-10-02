# 04-B Sızıntı gösterimi: sonuç raporu (2026-10-02)

**Plan:** `04b_sizinti_PLAN_v1_2026-10-01.md` (onaylı). Plandan sapma yok.
**Betik:** `04b_leakage_v1_2026-10-01.py`. Seed 20261001. Toplam süre yaklaşık 92 dakika (15 çekirdek).
**Veri:** `CAR_FREC_DATS.mat`, 112 denek (cg 66, sg 46). 448 satır × 3.584 öznitelik.
**Doğrulamalar:** Label ve Subject sütunlarının öznitelik setine girmediği `assert` ile doğrulandı. StandardScaler her hücrede CV'nin içinde fit edildi.
**Çıktılar:** `04b_leakage_v1_2026-10-01_results.csv` (özet), `_reps.csv` (tekrar bazında), `_null.npz` (sıfır dağılımları).

## 1. Ana tablo (birincil analiz)
| Hücre | CV | Öznitelik seçimi | Model | Satır AUC | Satır doğruluk | Denek AUC (tekrarlar arası 2,5–97,5) | Denek dengeli doğruluk |
|---|---|---|---|---|---|---|---|
| **N1 naif** | satır 10-fold | tüm veride | RF | **0,870** | **0,793** | 0,914 (0,90–0,92) | 0,798 |
| **N1 naif** | satır 10-fold | tüm veride | SVM | **0,855** | **0,757** | 0,886 (0,87–0,89) | 0,757 |
| N2 | satır 10-fold | CV içinde | RF / SVM | 0,861 / 0,826 | 0,788 / 0,732 | 0,910 / 0,867 | 0,795 / 0,744 |
| N3 | denek 5-fold | tüm veride | RF / SVM | 0,679 / 0,710 | 0,633 / 0,655 | 0,700 / 0,743 | 0,599 / 0,634 |
| N4 | denek 5-fold | CV içinde | RF / SVM | 0,641 / 0,620 | 0,601 / 0,596 | 0,657 / 0,639 | 0,577 / 0,572 |
| **P doğru, iç içe** | denek 5-fold × 20 | iç döngüde (k, C) | RF | 0,699 | 0,661 | **0,727 (0,67–0,79)** | 0,638 |
| **P doğru, iç içe** | denek 5-fold × 20 | iç döngüde (k, C) | SVM | 0,635 | 0,611 | **0,658 (0,59–0,75)** | 0,593 |

## 2. Sıfır kontrolü: etiketler denek düzeyinde 200 kez karıştırıldı
| Pipeline | Gerçek | Karıştırılmış etiketlerle ortalama [%95 aralık] | p |
|---|---|---|---|
| N1 RF, satır AUC | 0,870 | **0,780** [0,685–0,839] | 0,005 |
| N1 RF, satır doğruluk | 0,793 | **0,725** | – |
| N1 RF, denek AUC | 0,914 | **0,845** | – |
| N1 SVM, satır AUC | 0,855 | **0,735** [0,672–0,798] | 0,005 |
| N1 SVM, satır doğruluk | 0,757 | **0,693** | – |
| P SVM, denek AUC | 0,658 | **0,482** [0,400–0,578] | **0,010** |

**Okuma:**
- Naif pipeline, grup bilgisi tamamen yok edilmişken de satır düzeyinde %69–73 doğruluk, 0,73–0,78 AUC üretiyor. Denek düzeyindeki AUC ise 0,79–0,85.
- Bunun nedeni şu: bir deneğin 4 epoğu hem eğitim hem test kümesine düşüyor. Model deneğin "parmak izini" öğreniyor, ve karıştırılmış etiket deneğin bütün satırlarında aynı kaldığı için parmak izi etikete taşınıyor.
- Doğru pipeline aynı koşulda şans düzeyinde kalıyor (0,48).

## 3. Sızıntının ayrıştırılması (satır AUC)
| Kaynak | Karşılaştırma | RF | SVM |
|---|---|---|---|
| Öznitelik seçiminin tüm veride yapılması (satır CV altında) | N1 − N2 | +0,009 | +0,029 |
| Öznitelik seçiminin tüm veride yapılması (denek CV altında) | N3 − N4 | +0,038 | +0,090 |
| Epok/denek sızıntısı (satır CV) | N2 − N4 | **+0,220** | **+0,206** |

Bu veride şişkinliğin baskın kaynağı epok bazlı CV. Tüm veride öznitelik seçimi ikincil bir katkı yapıyor: denek bazlı CV altında 0,04–0,09.

## 4. Duyarlılık analizleri (denek AUC; gerçek değer)
| Varyant | N1 RF / SVM | P RF / SVM |
|---|---|---|
| Birincil (112 denek) | 0,914 / 0,886 | 0,727 / 0,658 |
| Kimliği doğrulanmış 100 denek | 0,919 / 0,842 | 0,685 / 0,615 |
| Kurtosis çıkarılmış | 0,914 / 0,886 | 0,733 / 0,683 |
| Yalnız göz kapalı epoklar (224 satır) | 0,859 / 0,783 | 0,654 / 0,603 |

- Kurtosis'in çıkarılması sonucu neredeyse hiç değiştirmiyor. Beklenen bir durum: bilgi taşımadığı için ANOVA seçiminde öne çıkmıyor.
- Kimliği doğrulanamayan 12 denek çıkarılınca doğru pipeline'ın AUC'si 0,04 düşüyor.

## 4b. Golden Distance ek sütunu (2026-10-02)
**Betik:** `04b_leakage_gd_v1_2026-10-02.py`. GD girdisi [ACC, Duyarlılık, Özgüllük, F1]; pozitif sınıf sg. Düşük GD daha iyi. Ana metrik AUC olmaya devam ediyor.
**Yeniden üretilebilirlik:** Hücreler aynı seed'lerle yeniden çalıştırıldı. 480 satırın 480'i kayıtlı sonuçlarla eşleşti; en büyük AUC farkı 1,1×10⁻¹⁶.

| Hücre | Model | Satır AUC | Satır GD | Denek AUC | Denek GD | Denek Sen / Spe |
|---|---|---|---|---|---|---|
| N1 naif | RF | 0,870 | 0,422 | 0,914 | 0,385 | 0,64 / 0,96 |
| N1 naif | SVM | 0,855 | 0,453 | 0,886 | 0,442 | 0,70 / 0,82 |
| N2 | RF / SVM | 0,861 / 0,826 | 0,430 / 0,492 | 0,910 / 0,867 | 0,390 / 0,462 | |
| N3 | RF / SVM | 0,679 / 0,710 | 0,664 / 0,621 | 0,700 / 0,743 | 0,679 / 0,624 | |
| N4 | RF / SVM | 0,641 / 0,620 | 0,708 / 0,713 | 0,657 / 0,639 | 0,713 / 0,710 | |
| P doğru | RF | 0,699 | 0,641 | 0,727 | 0,637 | 0,43 / 0,85 |
| P doğru | SVM | 0,635 | 0,681 | 0,658 | 0,681 | 0,45 / 0,74 |

- GD, AUC ile aynı sırayı veriyor: naif hücrelerde yaklaşık 0,39–0,45, doğru pipeline'da 0,64–0,68.
- Doğru pipeline'da duyarlılık düşük (0,43–0,45). Bu, dengesiz sınıflarda modelin çoğunluk sınıfına (cg) kaydığını gösteriyor. AUC bu durumu göstermez, GD gösterir.
- Duyarlılık analizleri için GD değerleri: `04b_leakage_gd_v1_2026-10-02_results.csv`.

## 5. Yorum ve sınırlar
1. **Sızıntı gösterimi (ana mesaj):** Aynı veriyle naif pipeline denek düzeyinde 0,89–0,91 AUC ve satır düzeyinde %76–79 doğruluk raporluyor. Bu performansın büyük kısmı, karıştırılmış etiketlerle de elde ediliyor. Doğru pipeline 0,66–0,73'e iniyor.
2. **Doğru pipeline şansın üstünde** (P SVM p = 0,010). Ama bu sonuç bir grup bulgusu olarak yorumlanamaz:
   - Önceden belirlenmiş birincil bir test değil; tek birincil test 05.
   - Excel öznitelikleri mutlak genliğe bağlı: Power, RMS, Min, Max. Mutlak genlik kayıt yeri (kurum ya da okul), kayıt dönemi ve kazanç farklarına duyarlı. 03'teki genlikten bağımsız 14 öznitelikle sg vs cg AUC'si 0,53'tü. Bu iki sonuç birlikte, ayrışmanın mutlak genlik ya da kayıt koşulu farkından gelebileceğiyle tutarlı. Ama ikisi aynı kohort ve aynı yöntem olmadığı için bu doğrudan test edilmiş değil.
   - Excel kohortu yayımlanan veriyle eşleşmiyor: 12 denek yayımlanmamış, sg2 yok (04-A). Sonuç yayımlanan EEG'den yeniden üretilemez.
3. **P SVM'nin p değeri hakkında:** Sıfır dağılımı permütasyon başına 5 tekrarla, gerçek değer ise 20 tekrarla hesaplandı (plana uygun). 5 tekrar sıfır dağılımını genişlettiği için bu p biraz tutucudur. P RF için permütasyon yapılmadı (kararınız).
4. GD ve NAoSP hesaplanmadı; formülleriniz verildiğinde eklenecek.
