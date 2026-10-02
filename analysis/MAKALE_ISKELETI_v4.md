# MAKALE İSKELETİ v4 (2026-10-02). Yalnızca iskelet, metin yazılmadı.

**v3'ten farklar:**
- 07f sonucu eklendi; başlık bu sonuca göre belirlendi.
- DENETIM_RAPORU_2'deki E2, E3, E4 ve E7 uygulandı.
- Tablo S2'ye denetim raporu 2'nin 3. bölümü eklendi.
- 07e betimsel haritası eklendi (Şekil S1).
- Şekil 2 v3'e güncellendi.

## Kural sonucu: başlık ve iddia (önceden belirlenmiş, 07d ve 07f)
- **Transfer testleri:** Beş modelin hiçbirinde sg2'ye anlamlı transfer yok (07c, 07d × 3, 07f).
  - Transfer AUC'leri 0,55–0,59, p = 0,10–0,29.
  - 07f (uzun blok modeli): 0,582, p = 0,104.
- **İddia:** Kural gereği iddia beş modelin hepsi için geçerli. İfade (E4): **"no evidence of transfer"**. Tespit sınırı AUC ≈ 0,60–0,65.
- **"non-generalizable", "does not transfer" ve "no model transfers" gibi ifadeler kullanılmaz (E4).**
- **06'nın kapsamı:** ROI düzeyindeki null sonuç, ROI ve model seçimine özgü. Aynı grupların karşılaştırması (E2): 03(b) sg vs cg, ROI + lojistik regresyon, 0,53 (n = 111) ile 07e sg vs cg, kanal + SVM, 0,746 (n = 100).

## Çerçeve
- Bu çalışmada kurulan naif pipeline yüksek doğruluk veriyor: 0,91 AUC (D5).
- **Sızıntısız kanal düzeyi analizde sg ile cg ayrışıyor: AUC 0,65–0,75** (E3):
  - göz kapalı epoklar 0,645,
  - göz açık 0,709,
  - tüm epoklar 0,734 / 0,754,
  - uzun göz kapalı blok 0,746.
- **Ancak bu ayrışma şunları göstermiyor:**
  - (i) ROI düzeyindeki önceden belirlenmiş özniteliklerde görülmüyor: aynı gruplarla 03(b) 0,53; suçlu = sg + sg2 ile 06'da 0,54 [0,44–0,63];
  - (ii) birincil test negatif (05);
  - (iii) ikinci suçlu alt grubuna (sg2) beş modelin hiçbirinde transfer kanıtı yok.
- **Sonuç:** alt gruba özgü ayrışma; genellenebilirliği gösterilmemiş.

## Başlık önerileri (İngilizce; E4'e uygun)
1. *High accuracy without demonstrated generalization: data leakage, recording confounds and subgroup-specific EEG differences in juvenile offenders* (DENETIM_RAPORU_2 önerisi)
2. *Separable within one subgroup, no evidence of transfer to another: a leakage- and confound-aware audit of resting-state EEG in juvenile offenders*
3. *Subgroup-specific resting-state EEG differences in juvenile offenders: leakage, recording confounds and the absence of evidence for transfer*

Öneri: 1.

## Özet (en son yazılacak)
- Methods: "pre-specified in a time-stamped analysis log (Table S2)"; keşifsel p değerleri düzeltmesiz (D9).
- Results: "no evidence of transfer (AUC 0.55–0.59; detection limit ≈ 0.60–0.65)".

---

## 1. Giriş (konu başlıkları)
- Suçlulukta EEG biyobelirteci arayışı; sızıntı türleri.
- Veri seti özelliği:
  - grup, kayıt yeri ve kayıt dönemiyle iç içe;
  - sg ile kontroller arasında hiç zamansal örtüşme yok;
  - sg2 kontrollere zamanca daha yakın ve kısmen örtüşüyor (D4);
  - madde kullanımı ve sosyoekonomik düzey farklı.
- Amaçlar:
  - (i) veri bütünlüğü,
  - (ii) sızıntı,
  - (iii) önceden belirlenmiş birincil test,
  - (iv) ROI düzeyinde nicelenmiş null,
  - (v) keşifsel kanal düzeyi ayrışma ve transfer.

## 2. Yöntem
| Alt bölüm | Kaynak | Tablo / Şekil |
|---|---|---|
| 2.1 Katılımcılar | 09 | **Tablo 1** |
| 2.2 Kayıt ve önişleme (veri sağlayıcısı) | README; 01 | metin |
| 2.3 Veri denetimi ve örneklemler | 01; 09 | **Şekil 5a**; **Tablo S-n** |
| 2.4 Analiz günlüğü | CLAUDE.md, planlar, DENETIM_RAPORU 1–2, git (`git_log.txt`) | **Tablo S2** |
| 2.5 Öznitelikler | 02 v2 / v3 | Tablo S3 |
| 2.6 Batch negatif kontrolü | 03 | metin |
| 2.7 Sızıntı gösterimi (naif pipeline bu çalışmada kuruldu) | 04-A, 04-B | metin |
| 2.8 Birincil test | 05 | metin |
| 2.9 ROI düzeyinde nicelenme | 06 | metin |
| 2.10 Keşifsel: kanal düzeyi, kaynak, kesit, transfer | 07, 07a–f | metin |
| 2.11 İstatistik | iç içe CV; permütasyon (en küçük p = 1/201); bootstrap; DeLong; AUC birincil; dengeli doğruluk ve GD (D10); keşifsel p düzeltmesiz (D9); 03/06'da lojistik regresyon, 04-B/07'de SVM ve gerekçesi; transfer: kat içi AUC, eşikten bağımsız; sınıflanma oranları kullanılmaz (E1) | metin |

## 3. Sonuçlar
| Alt bölüm | Kaynak | Anahtar sayılar | Tablo / Şekil |
|---|---|---|---|
| 3.1 Veri bütünlüğü ve kohort | 01, 04-A, 09 | Örneklemler 135 / 136 / 112 / 100; Excel: 12 bilinmeyen ID, sg2 yok, istatistikler 3 değerden; 14:00 sonrası kayıt: sg 14/49, sg2 7/25, cg 6/66 | **Şekil 5**, Tablo 1, Tablo S-n, Kutu 1 |
| 3.2 Sızıntı | 04-B (+ GD) | Naif 0,89–0,91; karıştırılmış etiketle 0,79–0,85; P 0,66–0,73 | **Şekil 1**, Tablo 2 |
| 3.3 Birincil test | 05 | p = 0,395; r = −0,085 [−0,28; 0,11] | **Şekil 3**, Tablo 3 |
| 3.4 ROI düzeyinde önceden belirlenmiş öznitelikler | 06, 03 | Suçlu vs cg: AUC 0,54 (%95 GA 0,44–0,63; tekrar ortalaması 0,51); sg vs cg 0,53 (03(b), n = 111); sg vs sg2 0,63 (p = 0,053) | **Şekil 4**, Tablo 4 |
| 3.5 Keşifsel: kanal düzeyinde ayrışma | 07, 07a–b, 07e | Kapalı 0,645 (kural boşluğu); açık 0,709; tüm epoklar 0,734 / 0,754; kapalı ve C bloğu çıkarılmış 0,582 (p = 0,0498); uzun blok 0,746. Tek öznitelik etkileri küçük (\|g\| ≤ 0,58) | **Şekil 2a**, **Şekil S1** |
| 3.6 Keşifsel: sg2'ye transfer | 07c, 07d, 07f | Beş modelde transfer AUC 0,549–0,589, p = 0,104–0,289 → hiçbirinde transfer kanıtı yok; tespit sınırı ≈ 0,60–0,65 | **Şekil 2b**, Tablo S4 |

## 4. Tartışma (konu başlıkları)
- **Doğruluk, ayrışma ve genellenebilirlik:** naif doğruluk (0,91), sızıntısız kanal düzeyi ayrışma (0,65–0,75) ve transfer kanıtının olmaması arasındaki fark.
- **ROI ile kanal düzeyi (E2):** aynı gruplar ve aynı blokta 0,53 ile 0,746. Öznitelik çözünürlüğü, model, kanal dışlaması ve örneklem birbirinden ayrıştırılmadı.
- **İmzanın doğası:**
  - çok sayıda küçük etkinin birleşimi (Şekil S1);
  - uzun blokta göreli delta ↑ ve teta ↓;
  - 4 dakikalık epoklarda C bloğu delta ↑; alfa ↓ sg2'de daha güçlü.
- **"Kademeli tablo → oküler artık" yorumu ana açıklama değil (E5):** uzun ve tamamen göz kapalı blok da 0,746 veriyor; 0,645'in nedeni veri miktarı olabilir.
- **sg'ye özgü imza için aday açıklamalar** (ayrıştırılamıyor):
  - kayıt dönemi (2021 yazı; kontrollerle hiç örtüşme yok);
  - şiddet suçu oranı (%86'ya karşı %24);
  - **(E7) uyanıklık farkı:** uzun blokta teta/alfa eğimi kontrollerde daha hızlı yükseliyor (02 betimsel: global medyan cg 0,026, sg 0,014 log10/dk);
  - **(E7) kayıt saati:** 14:00 sonrası kayıt oranı sg %29, cg %9.
- **Yaş:** gözlenen farkın yönü yaşla beklenenin tersi. Yaş bu ayrışmayı açıklamaz, aksine maskeler (DENETIM 8).
- **Madde kullanımı:** sg2'de daha yüksek ama sg2'de delta artışı yok. Bu, madde açıklamasını zayıflatıyor (betimsel).
- Analiz günlüğü: değeri ve sınırları; planlanıp yapılmayan analizler.
- Türetilmiş Excel özniteliklerinin yeniden üretilemezliği.
- Klinik ya da adli çıkarım yapılmamalı.

## 5. Sınırlılıklar
- Grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey ayrıştırılamıyor.
  - sg ile cg arasında hiç zamansal örtüşme yok.
  - sg2 ile cg aynı ayda yalnızca Mayıs–Haziran 2022'de kaydedilmiş.
- Aynı kurum varsayımı doğrulanmadı.
- **Güç:**
  - (a) testinde AUC < 0,70 etkiler tespit edilemiyor.
  - 06'da AUC ≲ 0,63 etkiler dışlanamıyor (yaklaşık).
  - **Transfer testlerinde (07c, 07d, 07f) AUC ≲ 0,60–0,65 etkiler tespit edilemiyor.**
- **ROI düzeyindeki null sonuç, ROI ve model seçimine özgü (07e; doğru eşleştirme 03(b), E2).**
- EOG ve ECG kanalları yayımlanmamış. Önişleme veri sağlayıcısında yapılmış. Uzun blokta uyanıklık düşüşü var.
- Kayıt saati dengesizliği (D12).
- Keşifsel p değerleri düzeltmesiz (D9).
- **Analiz kaydına ilişkin:**
  - Birincil statü sonradan verildi.
  - 07a'da kural boşluğu var.
  - QC değişikliği sonradan yapıldı.
  - 42 tek değişkenli test yapıldı (S2, 4b).
  - 07e kuralının ifadesinde hata vardı (S2).
- **Zaman damgaları:**
  - 07f'ye kadar zaman damgaları analistin kendi kaydı.
  - 07d–e'de tanım ile sonuç aynı commit'te.
  - Yalnızca 07f'nin tanımı, sonuçtan önce ayrı bir commit ile kaydedildi.
- Planlanıp yapılmayan analizler (S2).
- Excel kohortu yayımlanan veriyle eşleşmiyor.

## Tablo S2: Karar günlüğü
v3'teki 1–18 numaralı satırlar ve denetim raporu 1'den alınan 1b, 3b, 4a, 4b, 11b, 12b satırları değişmeden korunuyor (bkz. `MAKALE_ISKELETI_v3.md`). Ek satırlar:

| # | Tarih | Karar ya da olay | Sonuç görülmeden mi? | Kaynak |
|---|---|---|---|---|
| **Denetim raporu 2'den eklenenler (DENETIM_RAPORU_2_2026-10-02.md bölüm 3)** | | | | |
| 19 | — | **Planlanıp yapılmayan analizler:** (1) Madde kullanmayan, eşleştirilmiş alt örneklem ve regresyonla confound çıkarma. (2) Grup içi analizler: tekrar suç, çete, şiddet. (3) n = 139 ile ilk 60 s C bloğu duyarlılık analizi. Neden: 2026-10-01'de 03'ten sonra yapılan çerçeve değişikliği ve "yeni analiz eklenmez" ilkesi. Seçici raporlama eleştirisine karşı bu liste açıkça yazılmalı. | – | DENETIM_RAPORU_2 §3 |
| 20 | 2026-10-02 | **07d–e zaman damgası:** Tanım ve sonuçlar aynı git commit'inde (cbedc41). Tanımın sonuçlardan önce yazıldığı yalnızca CLAUDE.md ve ilerleme kaydıyla (başlangıç 09:12:41) destekleniyor. | Bkz. açıklama | DENETIM_RAPORU_2 §3 |
| 21 | 2026-10-02 | **07e kuralının ifade hatası:** Kural sohbet tarafında yazıldı ve "06" diyordu; doğrusu 03(b) sg–cg (bkz. E2). Sonuç değişmiyor. | Hata sonuçtan sonra fark edildi; kural değiştirilmedi, not eklendi | DENETIM_RAPORU_2 §3; CLAUDE.md notu |
| 22 | 2026-10-02 10:11 | **07f tanımı** (DENETIM_RAPORU_2 §4): uzun blok modelinin sg2'ye transferi; karar p < 0,05. Ayrı bir commit'le kaydedildi: **6a4439c**. | **Evet. Ayrı commit, analizden önce** | git 6a4439c |
| 23 | 2026-10-02 10:20 | **07f sonucu:** transfer AUC 0,582, p = 0,104 → transfer kanıtı yok; iddia beş modelin hepsi için geçerli. Commit: **11790e8**. | – | git 11790e8; `07f_..._rapor` |
| 24 | 2026-10-02 | DENETIM_RAPORU_2: E1–E8 metin ve şekil düzeltmeleri (v2/v3 dosyaları, eskiler korundu); 07e betimsel harita (test yok) | – | DENETIM_RAPORU_2 |

## Şekiller
| No | Dosya | İçerik |
|---|---|---|
| Şekil 1 | `Fig1_leakage_v2` | Sızıntı |
| **Şekil 2** | **`Fig2_exploratory_cascade_v3`** | (a) sg vs cg, bütün kesitler (p = 0,0498 etiketi; "long eyes-closed block"); (b) sg2'ye transfer, 5 model (07f dahil); (c) C bloğu delta ve A bloğu alfa |
| Şekil 3 | `Fig3_primary_alpha_reactivity_v2` | Birincil test |
| Şekil 4 | `Fig4_prespecified_null_v2` | ROI düzeyinde null (başlıkta E2 ifadesi) |
| Şekil 5 | `Fig5_cohort_v2` | Kohort |
| **Şekil S1** | **`FigS_07e_feature_map_v1`** | 07e kanal × bant Hedges g (betimsel) |

İngilizce başlık taslakları: `figures/FIGURE_CAPTIONS_v3.md`.

## Tablolar
- **Tablo 1** ve **Tablo S-n:** `09_tables_v1_2026-10-02_*`.
- **Tablo S4:** keşifsel analizler (07–07f) ve GD.
- **Diğerleri:** v3'teki gibi.
