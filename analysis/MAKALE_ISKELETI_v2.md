# MAKALE İSKELETİ v2 (2026-10-02). Yalnızca iskelet, metin yazılmadı.

**v1'den farklar:**
- Başlıklar yenilendi. "chance" ve "null" başlıkta yok; ana mesaj "yüksek doğruluk, genellenemeyen sinyal".
- "Pre-registered" ifadesi kullanılmıyor. Yerine: **"pre-specified in a time-stamped analysis log"**.
- Karar günlüğü (Tablo S2) ayrıntılı ve dürüst biçimde yazıldı.
- Sınırlılıklara yeni maddeler eklendi.
- Şekiller üretildi: `analysis/figures/`.

**Çerçeve:** Naif pipeline'lar yüksek doğruluk üretiyor. Sızıntısız analizde de orta düzeyde bir ayrışma kalıyor (P: 0,66–0,73; 07: 0,73). Ancak bu ayrışma:
- önceden belirlenmiş öznitelik setinde görülmüyor,
- birincil testte görülmüyor,
- diğer suçlu alt grubuna (sg2) genellenmiyor.

**Tek birincil hipotez testi:** 05. Bu statünün ne zaman verildiği için Tablo S2'ye bakın.

## Başlık önerileri (İngilizce)
1. *High accuracy, non-generalizable signal: leakage and recording confounds in resting-state EEG classification of juvenile offenders*
2. *Separable but not generalizable: a leakage- and confound-aware audit of resting-state EEG differences between juvenile offenders and controls*
3. *When EEG classifiers work for the wrong reasons: data leakage, cohort-specific signal and recording confounds in an open juvenile-offender dataset*

## Özet (en son yazılacak; yapılandırılmış)
Background / Methods / Results / Conclusions. Methods bölümünde şu ifade kullanılacak: "analyses were pre-specified in a time-stamped analysis log (Table S2)".

---

## 1. Giriş (yalnızca konu başlıkları)
- Suçluluk ve antisosyal davranışta EEG biyobelirteci arayışı; yüksek doğruluk raporlayan çalışmalar.
- EEG makine öğrenmesinde sızıntı türleri: epok ya da denek düzeyinde bölme, CV dışında öznitelik seçimi.
- Bu kohortla yapılmış önceki çalışmalar: nöropsikoloji (Data 2023), MRI (Data 2024). EEG yayını yok.
- Veri setinin özelliği: grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey iç içe.
- Amaçlar:
  - (i) veri bütünlüğü,
  - (ii) sızıntı gösterimi,
  - (iii) önceden belirlenmiş birincil test,
  - (iv) önceden belirlenmiş özniteliklerle ayrışmanın nicelenmesi,
  - (v) keşifsel kaynak ve genellenebilirlik ayrıştırması.

## 2. Yöntem
| Alt bölüm | Kaynak analiz | Tablo / Şekil |
|---|---|---|
| 2.1 Veri seti ve katılımcılar | `participants.tsv`; 03 Adım 0 | **Tablo 1** (sg / sg2 / cg demografi ve confound'lar) |
| 2.2 Kayıt ve önişleme (veri sağlayıcısı) | README, yan dosyalar; 01 | metin |
| 2.3 Veri denetimi ve dışlamalar | 01 | **Şekil 5a**; Tablo S1 |
| 2.4 Analiz günlüğü ("pre-specified in a time-stamped analysis log") | CLAUDE.md, plan dosyaları, git | **Tablo S2** (aşağıda) |
| 2.5 Öznitelikler | 02 v2 / v3 | Tablo S3; Şekil S2 |
| 2.6 Batch negatif kontrolü | 03 | metin |
| 2.7 Sızıntı gösterimi | 04-A, 04-B | metin |
| 2.8 Birincil test: alfa reaktivitesi | 05 | metin |
| 2.9 Ayrışmanın nicelenmesi | 06 | metin |
| 2.10 Keşifsel analizler | 07, 07a–c | metin |
| 2.11 İstatistik ve metrikler | iç içe CV, permütasyon, bootstrap, DeLong; AUC birincil; dengeli doğruluk ve GD ek | metin |

## 3. Sonuçlar
| Alt bölüm | Kaynak | Anahtar sayılar | Tablo / Şekil |
|---|---|---|---|
| 3.1 Veri bütünlüğü ve kohort | 01, 04-A | 140 → 135 / 136; kayıt dönemi ayrışması; Excel: 12 bilinmeyen ID, sg2 yok, istatistikler 3 değerden, 0 baytlık dosya | **Şekil 5**; Kutu 1 (n = 3 ispatı) |
| 3.2 Sızıntı | 04-B (+ GD) | Naif denek AUC 0,89–0,91; karıştırılmış etiketle 0,79–0,85; doğru pipeline 0,66–0,73 | **Şekil 1**, **Tablo 2** |
| 3.3 Birincil test | 05 | p = 0,395; r = −0,085 [−0,28; 0,11] | **Şekil 3**, **Tablo 3** |
| 3.4 Önceden belirlenmiş öznitelikler | 06, 03 | Suçlu vs cg 0,51 (GA 0,44–0,63); sg vs cg 0,53; sg vs sg2 0,63 (p = 0,053); transfer 0,44 | **Şekil 4**, **Tablo 4** |
| 3.5 Keşifsel: ayrışma var ama genellenmiyor | 07, 07a–c | A 0,754 / B 0,734; açık 0,709 > kapalı 0,645 > frontalsız 0,582; transfer sg2 0,569 (p = 0,26); kural boşluğu | **Şekil 2**; Tablo S4 |

## 4. Tartışma (konu başlıkları)
- **Naif doğruluk ile genellenebilir sinyal arasındaki fark:**
  - Naif pipeline 0,91 veriyor.
  - Sızıntısız pipeline 0,66–0,73 veriyor.
  - Bu ayrışma sg2'ye taşınmıyor ve birincil testte görülmüyor.
- **Ayrışmanın doğası:**
  - göz açık ve frontal katkı,
  - sg'ye özgü delta artışı,
  - kayıt dönemi, kayıt yeri, suç profili ve madde kullanımı birbirinden ayrıştırılamıyor.
- Önceden belirlenmiş öznitelikler (aperiodik düzeltilmiş, ROI düzeyinde) ile keşifsel kanal düzeyi öznitelikler arasındaki fark.
- Analiz günlüğünün değeri ve sınırları (Tablo S2): kural boşluğu, birincil statünün sonradan verilmesi.
- Türetilmiş öznitelik dosyalarının (Excel) yeniden üretilemezliği; açık veri için öneriler.
- Klinik ya da adli çıkarım yapılmaması gerektiği.

## 5. Sınırlılıklar
- Grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey ayrıştırılamıyor; sg ile cg arasında zamansal örtüşme yok.
- Aynı kurum varsayımı doğrulanmadı (yalnızca dosya yolu).
- Güç: (a) testinde AUC < 0,70 etkiler tespit edilemiyor. 06'da AUC ≤ 0,63 düzeyindeki etkiler dışlanamıyor.
- EOG ve ECG kanalları yayımlanmamış; oküler artık doğrudan kontrol edilemiyor.
- Önişleme veri sağlayıcısında yapılmış (ASR, ICA, ICLabel).
- 8 dakikalık blokta uyanıklık düşüşü.
- 06'nın GA'sı model eğitimindeki oynaklığı içermiyor.
- **Yeni (v2):**
  - **Birincil statü sonradan verildi.** Alfa reaktivitesi baştan planlanan analizler arasındaydı. Ama "tek birincil test" statüsü 03'ün sonuçları (14 öznitelikle sg vs cg AUC 0,53) görüldükten SONRA verildi.
  - **07a'da kural boşluğu.** Karar kuralı 0,60–0,65 aralığını tanımlamıyordu. Gözlenen 0,645 bu boşluğa düştü; sonuç "belirsiz" olarak raporlandı ve eşik sonradan değiştirilmedi.
  - **QC değişikliği sonradan yapıldı.** Atipik spektrum kuralı, öznitelik çıkarımından sonra yalnızca QC verisine bakılarak eklendi; grup karşılaştırması yapılmamıştı. Etkilenen 2 deneğin ikisi de sg2'de.
  - **Kaydın doğrulanabilirliği sınırlı.** Analiz günlüğündeki tarihleri analist kendisi kaydetti; harici bir zaman damgası, OSF ya da kriptografik doğrulama yok. Git geçmişi analizlerin tamamlanmasından sonra başlıyor (2026-10-02). "Önceden belirlenmiş" ifadesi bu sınırla birlikte okunmalı.
  - **07'deki eşikler sözel verildi.** "≈0,7" ve "yüksek" gibi eşikler, sonuçlar görülmeden analist tarafından permütasyon p < 0,05 olarak operasyonelleştirildi.
- Excel kohortu yayımlanan veriyle eşleşmiyor; 04-B sonuçları yayımlanan EEG'ye genellenemez.

## Tablo S2: Karar günlüğü (dürüst sürüm)
| # | Tarih | Karar ya da olay | Sonuç görülmeden mi? | Kaynak |
|---|---|---|---|---|
| 1 | 2026-10-01 | Veri denetimi (01): süreler, event'ler, dışlamalar, kayıt tarihi confound'u | Grup analizi yok | `01_data_audit_v2`, CLAUDE.md |
| 2 | 2026-10-01 | Öznitelik pilotu (3 denek) → birincil öznitelik tanımı kilitlendi: FOOOF fixed 3–30, knee duyarlılık, göreli güç 1–30, IAF, EMG/R² kanal kuralı, uyanıklık | Evet. Pilotta yalnızca QC görüldü, grup karşılaştırması yok | CLAUDE.md "Önceden belirlenmiş birincil analiz" |
| 3 | 2026-10-01 | **QC değişikliği:** atipik spektrum kuralı (> %25 kanal dışlanırsa yalnız EMG kuralı; birincilde dahil, duyarlılıkta hariç) | Grup karşılaştırması yapılmadan, 135 deneğin QC verisi görüldükten sonra | CLAUDE.md; `02_features_v3` |
| 4 | 2026-10-01 | 03 planı v1 → Adım 0 (sg ile sg2 demografisi) → plan v2: yorum tablosu revize edildi, transfer AUC kat içi | Evet. Adım 0 demografi, EEG sonucu değil | `03_..._PLAN_v1/v2` |
| 5 | 2026-10-01 | 03 sonuçları görüldü: sg vs cg 0,53; sg vs sg2 0,63 (p = 0,053) | – | `03_..._rapor` |
| 6 | 2026-10-01 | **Çerçeve değişikliği ve birincil statü:** makale "null + sızıntı denetimi" olarak çerçevelendi. **05 alfa reaktivitesi "tek birincil test" ilan edildi.** 06 tanımlandı. Yeni öznitelik eklenirse keşifsel sayılacak | **HAYIR. 03'ün sonuçları görüldükten SONRA.** Alfa reaktivitesi baştan "planlanan analizler" listesindeydi, ama birincil statüsü sonradan verildi. 05'in kendi sonucu henüz görülmemişti | CLAUDE.md "MAKALE ÇERÇEVESİ" |
| 7 | 2026-10-01 | 04 ile 05 planı v1 ve v2 (örnek birimi, n = 136, sabit 8–13 Hz, OOF bootstrap, 05 yorum kuralı) | Evet | `04_05_PLAN_v2` |
| 8 | 2026-10-01 | 04-A denetimi → 04-B kararları (Kurtosis içeride, RF permütasyonu yok, k = 100) | Evet. 04-A veri bütünlüğü, sınıflandırma sonucu değil | `04b_sizinti_PLAN_v1` |
| 9 | 2026-10-02 | 04-B sonuçları: P 0,66–0,73 (SVM p = 0,010) | – | `04b_..._rapor` |
| 10 | 2026-10-02 | 07 tanımı ve karar kuralı; "≈0,7 / ≈0,5" analist tarafından p < 0,05 olarak operasyonelleştirildi | Evet | CLAUDE.md "07" |
| 11 | 2026-10-02 | 07 sonucu: A ve B ikisi de anlamlı → kural: DUR | – | `07_..._rapor` |
| 12 | 2026-10-02 | 07a–c tanımı ve eşikleri (kullanıcı; "yüksek" = AUC ≥ 0,65 ve p < 0,05) | Evet | CLAUDE.md "07a–c" |
| 13 | 2026-10-02 | 07a–c sonucu: **kural boşluğu** (0,60–0,65 tanımsız; 0,645) → "belirsiz"; eşik değiştirilmedi; keşifsel ayrıştırma sonlandırıldı | Boşluk sonuçtan sonra fark edildi; kural değiştirilmedi | `07abc_..._rapor` |
| 14 | 2026-10-02 | 05 ve 06 plana birebir uygun çalıştırıldı (05: p = 0,395; 06: AUC 0,51, GA 0,44–0,63) | Evet (plan #7) | `05_ / 06_..._rapor` |
| 15 | 2026-10-02 | Git deposu oluşturuldu; ilk commit. Önceki adımların tarihleri dosya içi kayıtlara dayanıyor | – | git log |

## Şekiller (üretildi: `analysis/figures/`, 300 dpi PNG ve PDF; İngilizce başlık taslakları `figures/FIGURE_CAPTIONS_v1.md` dosyasında)
| No | İçerik | Kaynak |
|---|---|---|
| **Şekil 1** | Sızıntı: hücre × model denek AUC (N1–N4, P); karıştırılmış etiket dağılımı ile gerçek değer; GD | `04b_*` |
| **Şekil 2** | Keşifsel kademe ve transfer; eşikler ve kural boşluğu; gruplara göre göreli delta ve alfa | `07_*`, `07abc_*` |
| **Şekil 3** | Birincil test: ARI dağılımları; HL ve rank-biserial GA | `05_*` |
| **Şekil 4** | Önceden belirlenmiş özniteliklerle ayrışma: orman grafiği (GA ile CV tekrar aralığı ayrı işaretli) | `06_*`, `03_*` |
| **Şekil 5** | Kohort: akış, Excel ile veri seti örtüşmesi, kayıt tarihi zaman çizelgesi | `01_*`, `04a_*` |

## Tablolar
- **Ana tablolar:** Tablo 1 demografi, Tablo 2 sızıntı ve GD, Tablo 3 birincil test, Tablo 4 önceden belirlenmiş öznitelikler.
- **Ek tablolar:** S1 dışlamalar, S2 karar günlüğü, S3 öznitelik parametreleri, S4 keşifsel ve GD, S5 Excel denetimi.

## Veri ve kod erişimi
- Veri: OpenNeuro ds006923 / NEMAR on006923 (v1.0.0).
- Kod: `analysis/` (git deposu); seed 20261001; MNE 1.10, scikit-learn 1.7.1, fooof 1.1, statsmodels 0.14.6.
