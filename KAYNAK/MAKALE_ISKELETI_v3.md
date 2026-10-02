# MAKALE İSKELETİ v3 (2026-10-02). Yalnızca iskelet, metin yazılmadı.

**v2'den farklar:**
- 07d–e sonuçları eklendi.
- Başlık ve "genellenmiyor" iddiası 07d'nin kuralına göre belirlendi.
- 06'daki null sonucun kapsamı 07e'ye göre daraltıldı.
- DENETIM_RAPORU'ndaki D1–D12 uygulandı.
- Tablo S2'ye denetim raporunun 6. bölümündeki satırlar birebir eklendi.
- Tablo 1 ve Tablo S-n üretildi.
- Şekiller v2 olarak yeniden üretildi.

## Kural sonucu: başlık ve iddia (önceden belirlenmiş, 07d)
- **07d:** üç modelin hiçbiri sg2'ye transfer etmiyor (p = 0,22 / 0,19 / 0,29). Önceden belirlenen kural gereği **"genellenmiyor" iddiası korunuyor.**
- **İfadeye dair zorunlu not:** Metinde "no evidence of transfer to a second offender subgroup" denmeli. Gerekçe:
  - tasarımın tespit sınırı AUC ≈ 0,60–0,65,
  - gözlenen transfer AUC'leri 0,55–0,59.
- **07e:** kanal düzeyindeki ayrışma uzun göz kapalı blokta da var (0,746, p ≤ 0,005). Önceden belirlenen kural gereği **06'daki null sonuç ROI ve model seçimine özgü.** "Önceden belirlenmiş öznitelikler grupları ayırmıyor" ifadesi yalnızca ROI düzeyindeki 14 öznitelik için geçerli.

## Çerçeve
- **Naif doğruluk yüksek.** Bu çalışmada kurulan sızıntılı pipeline 0,91 AUC veriyor (D5).
- **Sızıntısız analizde de kanal düzeyinde ayrışma var.** sg ile cg 0,71–0,75 AUC ile ayrışıyor (göz açık, göz kapalı, uzun blok).
- **Ancak bu ayrışma şunları göstermiyor:**
  - (i) önceden belirlenmiş ROI düzeyindeki özniteliklerde görülmüyor (06: AUC 0,54; GA 0,44–0,63);
  - (ii) birincil test negatif (05);
  - (iii) ikinci suçlu alt grubuna (sg2) transfer ettiğine dair kanıt yok (07c–d).
- **Sonuç:** kohorta ya da alt gruba özgü, genellenebilirliği gösterilmemiş bir sinyal.

## Başlık önerileri (İngilizce)
1. *High accuracy, non-generalizable signal: leakage and recording confounds in resting-state EEG classification of juvenile offenders*
2. *Separable but not transferable: a leakage- and confound-aware audit of resting-state EEG in juvenile offenders*
3. *Channel-level EEG separates one offender subgroup from controls but does not transfer to another: leakage, confounds and pre-specification in an open dataset*

Öneri: 1 ya da 3. Metin "no evidence of transfer" ifadesini kullanmalı.

## Özet (en son yazılacak)
Methods bölümünde şu ifade geçecek: "pre-specified in a time-stamped analysis log (Table S2)". Keşifsel analizlerin düzeltmesiz olduğu belirtilecek (D9).

---

## 1. Giriş (konu başlıkları)
- Suçluluk ve antisosyal davranışta EEG biyobelirteci arayışı; yüksek doğruluk raporlayan çalışmalar.
- Sızıntı türleri: epok düzeyinde bölme; CV dışında öznitelik seçimi.
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
  - (v) keşifsel kanal düzeyi ayrışma ve genellenebilirlik.

## 2. Yöntem
| Alt bölüm | Kaynak | Tablo / Şekil |
|---|---|---|
| 2.1 Katılımcılar | `participants.tsv`; 09 | **Tablo 1** (sg / sg2 / suçlu toplamı / cg; Mann–Whitney ya da Fisher; kayıt saati dahil, D11–D12) |
| 2.2 Kayıt ve önişleme (veri sağlayıcısı) | README; 01 | metin |
| 2.3 Veri denetimi ve örneklemler | 01; 09 | **Şekil 5a** (paralel örneklemler, D8); **Tablo S-n** |
| 2.4 Analiz günlüğü | CLAUDE.md, planlar, DENETIM_RAPORU, git | **Tablo S2** |
| 2.5 Öznitelikler | 02 v2 / v3 | Tablo S3 |
| 2.6 Batch negatif kontrolü | 03 | metin |
| 2.7 Sızıntı gösterimi (naif pipeline bu çalışmada kuruldu, D5) | 04-A, 04-B | metin |
| 2.8 Birincil test | 05 | metin |
| 2.9 ROI düzeyinde nicelenme | 06 | metin |
| 2.10 Keşifsel analizler: kanal düzeyi, kaynak, transfer, kesit | 07, 07a–e | metin |
| 2.11 İstatistik | iç içe CV, permütasyon (en küçük p = 1/201), bootstrap, DeLong; AUC birincil; dengeli doğruluk ve GD (GD, ACC/Sen/Spe/F1'i özetler; D10). **Keşifsel p değerleri düzeltmesiz (D9).** Model farkı: 03 ve 06'da önceden belirlenmiş lojistik regresyon; 04-B ve 07'de P ile karşılaştırılabilirlik için SVM | metin |

## 3. Sonuçlar
| Alt bölüm | Kaynak | Anahtar sayılar | Tablo / Şekil |
|---|---|---|---|
| 3.1 Veri bütünlüğü ve kohort | 01, 04-A, 09 | Örneklemler 135 / 136 / 112 / 100; Excel: 12 bilinmeyen ID, sg2 yok, istatistikler 3 değerden; 14:00 sonrası kayıt oranı sg 14/49, sg2 7/25, cg 6/66 | **Şekil 5**, Tablo 1, Tablo S-n, Kutu 1 |
| 3.2 Sızıntı | 04-B (+ GD) | Naif 0,89–0,91; karıştırılmış etiketle 0,79–0,85; P 0,66–0,73 | **Şekil 1**, Tablo 2 |
| 3.3 Birincil test | 05 | p = 0,395; r = −0,085 [−0,28; 0,11] | **Şekil 3**, Tablo 3 |
| 3.4 ROI düzeyinde önceden belirlenmiş öznitelikler | 06, 03 | **AUC 0,54 (%95 GA 0,44–0,63; tekrar ortalaması 0,51)** (D2); sg vs cg 0,53; sg vs sg2 0,63 (p = 0,053) | **Şekil 4**, Tablo 4 |
| 3.5 Keşifsel: kanal düzeyinde ayrışma ve genellenebilirlik | 07, 07a–e | Tüm epoklar 0,754 / 0,734; açık 0,709; kapalı 0,645 (kural boşluğu); kapalı ve C bloğu çıkarılmış 0,582; **uzun blok 0,746**; transfer 0,549–0,589, hepsi p > 0,19 | **Şekil 2**, Tablo S4 |

## 4. Tartışma (konu başlıkları)
- Naif doğruluk, sızıntısız ayrışma ve genellenebilirlik arasındaki fark.
- **06 ile 07e arasındaki fark:** aynı blokta ROI düzeyi ve lojistik regresyon 0,54 verirken kanal düzeyi ve SVM 0,746 veriyor. Öznitelik çözünürlüğü, model ve kanal dışlaması birbirinden ayrıştırılmadı.
- **İmzanın sg'ye özgü olması:**
  - delta artışı yalnız sg'de, alfa düşüşü sg2'de de var;
  - aday açıklamalar ayrıştırılamıyor: kayıt dönemi, şiddet suçu oranı, öğleden sonra kayıt oranı.
- **Yaş:** sg kontrollerden yaşça büyük. Ergenlikte yaşla beklenen değişim (delta azalır, alfa artar) gözlenen farkın tersi yönde. Dolayısıyla yaş bu ayrışmayı açıklamaz, aksine maskeler (DENETIM 8; literatürle doğrulanacak).
- **Madde kullanımı:** sg2'de daha yüksek, ama sg2'de delta artışı yok. Bu, madde açıklamasını zayıflatıyor (betimsel; test edilmedi).
- Analiz günlüğünün değeri ve sınırları; kural boşluğu; birincil statünün sonradan verilmesi.
- Türetilmiş özniteliklerin (Excel) yeniden üretilemezliği.
- Klinik ya da adli çıkarım yapılmamalı.

## 5. Sınırlılıklar
- Grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey ayrıştırılamıyor. sg ile cg arasında hiç zamansal örtüşme yok. sg2 ile cg aynı ayda yalnızca Mayıs–Haziran 2022'de kaydedilmiş (sg2 11, cg 9); 07 örnekleminde bu dönemde yalnızca 5 cg var (D4).
- Aynı kurum varsayımı doğrulanmadı.
- **Güç:**
  - (a) testinde AUC < 0,70 etkiler tespit edilemiyor.
  - 06'da AUC ≲ 0,63 etkiler dışlanamıyor; bu sınır yaklaşık (D2).
  - **07c–d'de transfer AUC ≲ 0,60–0,65 etkiler tespit edilemiyor.**
- **06'nın null sonucu ROI ve model seçimine özgü (07e).**
- EOG ve ECG kanalları yayımlanmamış. Önişleme veri sağlayıcısında yapılmış. Uzun blokta uyanıklık düşüşü.
- Kayıt saati dengesizliği: 14:00 sonrası kayıt oranı sg %29, cg %9 (D12).
- **Keşifsel p değerleri düzeltmesiz (D9).**
- Birincil statü sonradan verildi. 07a'da kural boşluğu var. QC değişikliği sonradan yapıldı (Tablo S2).
- 03'ten sonra ve 05'in birincil ilan edilmesinden önce, 42 tek değişkenli test yapıldı (Tablo S2, satır 4b).
- Kaydın doğrulanabilirliği: günlükteki zaman damgaları analistin kendi kaydı; git geçmişi 2026-10-02'de başlıyor.
- 07'deki sözel eşikler analist tarafından operasyonelleştirildi.
- Excel kohortu yayımlanan veriyle eşleşmiyor.

## Tablo S2: Karar günlüğü
| # | Tarih | Karar ya da olay | Sonuç görülmeden mi? | Kaynak |
|---|---|---|---|---|
| 1 | 2026-10-01 | Veri denetimi (01) | Grup analizi yok | `01_data_audit_v2`, CLAUDE.md |
| 2 | 2026-10-01 | Öznitelik pilotu → birincil öznitelik tanımı kilitlendi | Evet (yalnız QC görüldü) | CLAUDE.md |
| 3 | 2026-10-01 | QC değişikliği: atipik spektrum kuralı | Grup karşılaştırması yapılmadan, QC verisi görüldükten sonra | CLAUDE.md; `02_features_v3` |
| 4 | 2026-10-01 | 03 planı v1 → Adım 0 → plan v2 | Evet | `03_..._PLAN_v1/v2` |
| 5 | 2026-10-01 | 03 sonuçları görüldü | – | `03_..._rapor` |
| 6 | 2026-10-01 | Çerçeve değişikliği; 05 "tek birincil test" ilan edildi; 06 tanımlandı | **HAYIR. 03'ten sonra.** Alfa reaktivitesi baştan planlanmıştı; birincil statü sonradan verildi | CLAUDE.md |
| 7 | 2026-10-01 | 04 ile 05 planı v1 ve v2 | Evet | `04_05_PLAN_v2` |
| 8 | 2026-10-01 | 04-A → 04-B kararları | Evet | `04b_sizinti_PLAN_v1` |
| 9 | 2026-10-02 | 04-B sonuçları | – | `04b_..._rapor` |
| 10 | 2026-10-02 | 07 tanımı (eşikler analist tarafından p < 0,05 olarak operasyonelleştirildi) | Evet | CLAUDE.md |
| 11 | 2026-10-02 | 07 sonucu → DUR | – | `07_..._rapor` |
| 12 | 2026-10-02 | 07a–c tanımı ve eşikleri | Evet | CLAUDE.md |
| 13 | 2026-10-02 | 07a–c sonucu: kural boşluğu → "belirsiz"; eşik değiştirilmedi | Boşluk sonuçtan sonra fark edildi | `07abc_..._rapor` |
| 14 | 2026-10-02 | 05 ve 06 plana uygun çalıştırıldı | Evet | `05_ / 06_..._rapor` |
| 15 | 2026-10-02 | Git deposu ve ilk commit | – | `git_log.txt` |
| **Denetim raporundan eklenenler (DENETIM_RAPORU_2026-10-02.md bölüm 6; birebir)** | | | | |
| 1b | 2026-10-01 ~19:50 | 02 v2'nin grup bazlı QC betimselleri görüldükten sonra iki karar verildi: H1 sonuçları tam kesitle yan yana raporlanacak, teta/alfa eğimi kovaryat olacak. Kayıt saati grup bazında betimsel olarak kontrol edildi. | | DENETIM_RAPORU §6 |
| 3b | 2026-10-01 ~19:50 | Atipik spektrum kuralı benimsendiğinde, etkilenen deneklerin sg2'de olduğu ve hem esrar hem kokain kullandıkları biliniyordu. Kural bu denekleri birincil analizde tuttu. | | DENETIM_RAPORU §6 |
| 4a | 2026-10-01 ~20:35 | Adım 0 demografisi önce sohbette hesaplandı, ardından betikle yeniden üretildi. | | DENETIM_RAPORU §6 |
| 4b | 2026-10-01 ~22:20 | **03'ün sonuçlarından sonra ve 05 birincil test ilan edilmeden önce, 14 önceden belirlenmiş öznitelik için 42 tek değişkenli Mann–Whitney testi yapıldı** (sg–cg, sg2–cg, sg–sg2; düzeltmesiz; en küçük p ≈ 0,025). Testler göreli alfayı da içeriyordu. Bu testler hiçbir öznitelik seçimine girdi olmadı. 05'in birincil test seçimi aynı adımda yapıldı. | | DENETIM_RAPORU §6 |
| 11b | 2026-10-02 ~07:44 | 07a–c'nin tasarımı, 07'nin betimsel öznitelik haritasından türetildi (en güçlü 50 öznitelik: C bloğu delta ve alfa). 07a–c, kendi sonuçları görülmeden tanımlandı. | | DENETIM_RAPORU §6 |
| 12b | 2026-10-02 | 07a–c'nin eşikleri sohbet tarafında önerildi. 0,60–0,65 boşluğu bu öneriden kaynaklanıyor. | | DENETIM_RAPORU §6 |
| **Sonraki adımlar** | | | | |
| 16 | 2026-10-02 | Bağımsız denetim raporu (DENETIM_RAPORU): D1–D12 metin ve şekil düzeltmeleri; 07d–e önerildi | – | DENETIM_RAPORU |
| 17 | 2026-10-02 | 07d–e tanımı ve tek ölçütlü karar kuralları CLAUDE.md'ye yazıldı | Evet | CLAUDE.md "07d–e" |
| 18 | 2026-10-02 | 07d–e sonuçları: transfer yok (iddia korunur); uzun blokta ayrışma var (06 null ROI/model seçimine özgü) | – | `07de_..._rapor` |

## Şekiller (v2: `analysis/figures/*_v2.*`; İngilizce başlık taslakları `FIGURE_CAPTIONS_v2.md`)
| No | İçerik |
|---|---|
| Şekil 1 | Sızıntı (ROC-AUC; epok ve seçim sızıntısı gölgeleri; seçim alt etiketleri; karıştırılmış etiketler; GD) |
| Şekil 2 | (a) sg vs cg, bütün kesitler, uzun blok dahil; (b) sg2'ye transfer (07c–d); (c) C bloğu delta ve A bloğu alfa |
| Şekil 3 | Birincil test |
| Şekil 4 | ROI düzeyinde null (AUC 0,54, GA 0,44–0,63) |
| Şekil 5 | Paralel örneklemler, Excel ile veri seti Venn'i, kayıt tarihleri |

## Tablolar
- **Tablo 1:** `09_tables_v1_2026-10-02_Table1.md` (D11–D12).
- **Tablo S-n:** `09_tables_v1_2026-10-02_TableSn.md`.
- **Diğer tablolar:** Tablo 2–4 ve S1, S3–S5 v2'deki gibi. Tablo S4'e 07d–e eklenecek.
