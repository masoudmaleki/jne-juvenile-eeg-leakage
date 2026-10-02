# MAKALE İSKELETİ v5 (2026-10-02). Yalnızca iskelet, metin yazılmadı.

**v4'ten farklar (DENETIM_RAPORU_3):**
- 07g sonucu eklendi: keşifsel AUC'lerin kesin %95 GA'ları (tanım e81e61b, sonuç e5dfeb6). F2'deki yaklaşık GA'lar yerine bunlar kullanıldı.
- F1–F7 uygulandı. Başlık F3'teki ilk tercih oldu; eski başlık önerileri 1 ve 3 kaldırıldı.
- "Tespit sınırı ≈ 0,60–0,65" ifadesi her yerden kaldırıldı (F2). Bunun yerine anlamlılık eşiği ve GA ayrı ayrı veriliyor.
- Tablo S2'ye 25–33 numaralı satırlar eklendi (F6 ve bölüm 5, K7–K10). Tablo S-n v2'ye ve yeni Tablo S4'e geçildi.

## Kural sonucu: başlık ve iddia (önceden belirlenmiş, 07d ve 07f)
- **Transfer testleri:** Beş modelin hiçbirinde sg2'ye anlamlı transfer yok (07c, 07d × 3, 07f).
  - Transfer AUC'leri 0,549–0,589, p = 0,104–0,289.
  - 07f (uzun blok modeli): 0,582, p = 0,104.
- **İddia:** Kural gereği iddia beş modelin hepsi için geçerli. İfade (E4): **"no evidence of transfer"**.
- **Belirsizlik (F2, 07g):**
  - Anlamlılık eşiği: sıfır dağılımının tek yönlü %95 persentili 0,586–0,638.
  - %95 GA (denek bootstrap'ı): 07c 0,439–0,688; 07d A 0,439–0,662; 07d B 0,475–0,702; 07d B açık 0,446–0,660; 07f 0,463–0,704.
  - Buna göre AUC > ~0,66–0,70 yaklaşık olarak dışlanıyor. Veri "transfer yok" ile "orta düzeyde transfer" arasındaki her şeyle uyumlu.
- **Şu ifadeler kullanılmaz:**
  - "non-generalizable", "does not transfer", "no model transfers" (E4);
  - "subgroup-specific" ve "sg'ye özgü" (F3);
  - "tespit sınırı" (F2).
- **06'nın kapsamı (F7):** ROI düzeyindeki null sonuç, analiz seçimlerine özgü: ROI ya da kanal düzeyi, model, kanal dışlaması ve örneklem (111/100). Aynı grupların karşılaştırması (E2): 03(b) sg vs cg, ROI + lojistik regresyon, 0,53 (n = 111) ile 07e sg vs cg, kanal + SVM, 0,746 (n = 100).
- **F1:** ROI düzeyinde sg vs cg (0,53) ile sg + sg2 vs cg (0,54) aynı düzeyde. 06'daki null sonuç sg2'nin dahil edilmesinden kaynaklanmıyor.

## Çerçeve
- Bu çalışmada kurulan naif pipeline yüksek doğruluk veriyor: 0,91 AUC (D5).
- **Sızıntısız kanal düzeyi analizde sg ile cg ayrışıyor: AUC 0,65–0,75 (tekrar ortalaması)** (E3):
  - göz kapalı epoklar 0,645,
  - göz açık 0,709,
  - tüm epoklar 0,734 / 0,754,
  - uzun göz kapalı blok 0,746 (07g: ortalama skordan 0,781, GA 0,685–0,867).
- **Ancak bu ayrışma şunları göstermiyor:**
  - (i) ROI düzeyindeki önceden belirlenmiş özniteliklerde görülmüyor: aynı gruplarla 03(b) 0,53; suçlu = sg + sg2 ile 06'da 0,54 [0,44–0,63];
  - (ii) birincil test negatif (05);
  - (iii) ikinci suçlu alt grubuna (sg2) beş modelin hiçbirinde transfer kanıtı yok.
- **Sonuç (F3):** bir alt grupta gözlenen, diğer alt gruba transferi gösterilemeyen ayrışma.

## Başlık (F3)
**High accuracy without demonstrated generalization: data leakage and recording confounds in resting-state EEG classification of juvenile offenders**

Kabul edilebilir alternatif: *Separable within one subgroup, no evidence of transfer to another: a leakage- and confound-aware audit of resting-state EEG in juvenile offenders*.
Kaldırılan öneriler (v4'teki 1 ve 3): "subgroup-specific" iddiası içeriyorlardı (F3, K8).

## Özet (en son yazılacak)
- Methods: "pre-specified in a time-stamped analysis log (Table S2)"; keşifsel p değerleri düzeltmesiz (D9). Denetim: "audits in a separate session of the same AI model (Claude)", "bağımsız denetim" değil (F6).
- Results: "no evidence of transfer (AUC 0.55–0.59; 95% CIs up to 0.66–0.70)". "Detection limit" ifadesi yok (F2).

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
| 2.3 Veri denetimi ve örneklemler | 01; 09 | **Şekil 5a**; **Tablo S-n v2** |
| 2.4 Analiz günlüğü | CLAUDE.md, planlar, DENETIM_RAPORU 1–3, git (`git_log.txt`, `git_show_07f.txt`). Denetimler "aynı yapay zekâ modelinin ayrı bir oturumunda yapılan denetim (Claude)" olarak tanımlanır; "bağımsız denetim" denmez. Derginin yapay zekâ beyanıyla tutarlı olmalı (F6). | **Tablo S2** |
| 2.5 Öznitelikler | 02 v2 / v3 | Tablo S3 |
| 2.6 Batch negatif kontrolü | 03 | metin |
| 2.7 Sızıntı gösterimi (naif pipeline bu çalışmada kuruldu) | 04-A, 04-B | metin |
| 2.8 Birincil test | 05 | metin |
| 2.9 ROI düzeyinde nicelenme | 06 | metin |
| 2.10 Keşifsel: kanal düzeyi, kaynak, kesit, transfer | 07, 07a–g. **Örneklem gerekçesi (F7):** 07 serisi, 04-B ile karşılaştırılabilir olsun diye kimliği doğrulanmış 100 denekle (Excel ∩ yayımlanan veri; cg 55, sg 45) yapıldı. Bu tercih 07e ve 07f'de de sürdürüldü. | metin |
| 2.11 İstatistik | iç içe CV; permütasyon (en küçük p = 1/201); bootstrap; DeLong; AUC birincil; dengeli doğruluk ve GD (D10); keşifsel p düzeltmesiz (D9); 03/06'da lojistik regresyon, 04-B/07'de SVM ve gerekçesi; transfer: kat içi AUC, eşikten bağımsız; sınıflanma oranları kullanılmaz (E1). **07g GA'ları:** kaynak modellerde sınıf içi tabakalı denek bootstrap'ı (06 ile aynı), transferde ağırlıklı (çok terimli) denek bootstrap'ı; 2000 yineleme; yalnız denek örneklemesi, model eğitimindeki oynaklık dahil değil. | metin |

## 3. Sonuçlar
| Alt bölüm | Kaynak | Anahtar sayılar | Tablo / Şekil |
|---|---|---|---|
| 3.1 Veri bütünlüğü ve kohort | 01, 04-A, 09 | Örneklemler 135 / 136 / 112 / 100; Excel: 12 bilinmeyen ID, sg2 yok, istatistikler 3 değerden; 14:00 sonrası kayıt: sg 14/49, sg2 7/25, cg 6/66 | **Şekil 5**, Tablo 1, Tablo S-n v2, Kutu 1 |
| 3.2 Sızıntı | 04-B (+ GD) | Naif 0,89–0,91; karıştırılmış etiketle 0,79–0,85; P 0,66–0,73 | **Şekil 1**, Tablo 2 |
| 3.3 Birincil test | 05 | p = 0,395; r = −0,085 [−0,28; 0,11] | **Şekil 3**, Tablo 3 |
| 3.4 ROI düzeyinde önceden belirlenmiş öznitelikler | 06, 03 | Suçlu vs cg: AUC 0,54 (%95 GA 0,44–0,63; tekrar ortalaması 0,51); sg vs cg 0,53 (03(b), n = 111); sg vs sg2 0,63 (p = 0,053). sg2'nin dahil edilmesi null sonucu açıklamaz (F1) | **Şekil 4**, Tablo 4 |
| 3.5 Keşifsel: kanal düzeyinde ayrışma | 07, 07a–b, 07e, 07g | Tekrar ortalaması: kapalı 0,645 (kural boşluğu); açık 0,709; tüm epoklar 0,734 / 0,754; kapalı ve C bloğu çıkarılmış 0,582 (p = 0,0498); uzun blok 0,746. 07g GA'ları (ortalama skordan AUC): uzun blok 0,781 (0,685–0,867), 07b 0,609 (0,495–0,725); diğerleri Tablo S4. Tek öznitelik etkileri **küçük–orta (\|g\| ≤ 0,58)** (F7); en büyükleri frontopolar elektrotlarda (F4) | **Şekil 2a**, **Şekil S1**, Tablo S4 |
| 3.6 Keşifsel: sg2'ye transfer | 07c, 07d, 07f, 07g | Beş modelde transfer AUC 0,549–0,589, p = 0,104–0,289 → hiçbirinde transfer kanıtı yok. Anlamlılık eşiği 0,586–0,638. %95 GA üst sınırları 0,660–0,704 → AUC > ~0,70 yaklaşık dışlanır, orta düzeyde transfer dışlanamaz (F2). Atipik 2 sg2 hariç (betimsel): 0,534–0,566 | **Şekil 2b**, Tablo S4 |

## 4. Tartışma (konu başlıkları)
- **Doğruluk, ayrışma ve genellenebilirlik:** naif doğruluk (0,91), sızıntısız kanal düzeyi ayrışma (0,65–0,75) ve transferin gösterilememesi arasındaki fark. Kaynak AUC ile transfer AUC'si arasındaki fark test edilmedi; "fark var" denmez (F2).
- **ROI ile kanal düzeyi (E2, F1, F7):** aynı gruplar ve aynı blokta 0,53 ile 0,746. Öznitelik çözünürlüğü, model, kanal dışlaması ve örneklem (111/100) birbirinden ayrıştırılmadı. sg2'nin dahil edilmesi açıklama değil (F1).
- **İmzanın doğası (F4):**
  - En büyük etkiler frontopolar ve ön-frontal elektrotlarda (C bloğu; en büyük 10 etkinin 10'u, en büyük 20'nin 18'i): sg'de göreli delta ↑, teta ↓, beta ↓.
  - Uzun blokta alfa farkı yok (A bloğu medyan g = 0,015). 4 dakikalık epoklarda görülen alfa ↓ uzun blokta görülmüyor.
  - Uzun blok sonucu, göz açıkken oluşan kırpma ve sakkad artefaktını tek açıklama olmaktan çıkarıyor. Ama en büyük etkiler frontopolar elektrotlarda ve düşük frekansta. Göz kapalıyken oluşan göz hareketleri, deri potansiyelleri ve sinirsel kaynak bu veriyle birbirinden ayrılamıyor. EOG yayımlanmadı.
  - 07b de aynı yöne işaret ediyor: C bloğu çıkarılınca göz kapalı epoklarda 0,645 → 0,582.
  - **Yön notu:** Uzun blokta uyuklama göstergesi (teta/alfa eğimi) kontrollerde daha yüksek, ama frontopolar delta sg'de daha yüksek. Uyuklamaya bağlı yavaş göz hareketleri bu farkın yönünü tek başına açıklamaz.
- **sg–cg farkı için aday açıklamalar** (F3; ayrıştırılamıyor):
  - kayıt dönemi (2021 yazı; kontrollerle hiç örtüşme yok);
  - şiddet suçu oranı (%86'ya karşı %24);
  - **(E7) uyanıklık farkı:** uzun blokta teta/alfa eğimi kontrollerde daha hızlı yükseliyor (02 betimsel: global medyan cg 0,026, sg 0,014 log10/dk);
  - **(E7) kayıt saati:** 14:00 sonrası kayıt oranı sg %29, cg %9;
  - frontopolar artefakt kaynakları (F4).
- **Yaş (F7):** delta için gözlenen farkın yönü yaşla beklenenin tersi; yaş bu delta farkını açıklamaz, aksine maskeler (DENETIM 8). Bu argüman yalnız delta için geçerli; uzun blokta alfa farkı yok. **Literatürle doğrulanacak.**
- **Madde kullanımı (F7):** sg2'de daha yüksek, ama göz kapalı epoklarda (2 × 50 s; 07abc betimsel) sg2'de delta artışı yok. Uzun blok için sg2 haritası yok. Madde açıklamasını zayıflatıyor, ama yalnız betimsel ve yalnız epoklar için.
- Analiz günlüğü: değeri ve sınırları; planlanıp yapılmayan analizler; denetimlerin aynı modelin ayrı oturumunda yapılması (F6).
- Türetilmiş Excel özniteliklerinin yeniden üretilemezliği.
- Klinik ya da adli çıkarım yapılmamalı.

## 5. Sınırlılıklar
- Grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey ayrıştırılamıyor.
  - sg ile cg arasında hiç zamansal örtüşme yok.
  - sg2 ile cg aynı ayda yalnızca Mayıs–Haziran 2022'de kaydedilmiş.
- Aynı kurum varsayımı doğrulanmadı.
- **Güç (F2):**
  - (a) testinde AUC < 0,70 etkiler tespit edilemiyor.
  - 06'da AUC ≲ 0,63 etkiler dışlanamıyor (yaklaşık).
  - **Transfer testlerinde (07c, 07d, 07f):** anlamlılık için gözlenen AUC'nin 0,586–0,638'i geçmesi gerekirdi; %80 güç için gerçek transfer AUC'si yaklaşık 0,66 olmalı (DENETIM_RAPORU_3 benzetimi); %95 GA'lar 0,70'e kadar uzanıyor (07g). Orta düzeyde transfer dışlanamaz.
  - 07g GA'ları model eğitimindeki oynaklığı içermiyor. Kaynak modellerde GA, 20 tekrarın ortalama skorundan hesaplanan AUC üzerinde; bu AUC tekrar ortalamasından yüksek (ör. 07 B: 0,800 ile 0,734).
- **ROI düzeyindeki null sonuç, analiz seçimlerine özgü (07e; doğru eşleştirme 03(b), E2; F7).**
- EOG ve ECG kanalları yayımlanmamış; frontopolar etkilerin kaynağı belirlenemiyor (F4). Önişleme veri sağlayıcısında yapılmış. Uzun blokta uyanıklık düşüşü var.
- Kayıt saati dengesizliği (D12).
- Keşifsel p değerleri düzeltmesiz (D9).
- **Analiz kaydına ilişkin:**
  - Birincil statü sonradan verildi.
  - 07a'da kural boşluğu var.
  - QC değişikliği sonradan yapıldı.
  - 42 tek değişkenli test yapıldı (S2, 4b).
  - 07e kuralının ifadesinde hata vardı (S2).
  - 07f ve 07g, önceki sonuçlar görüldükten sonra önerildi (S2, 25 ve 31).
- **Zaman damgaları:**
  - 07f'den önceki zaman damgaları analistin kendi kaydı.
  - 07d–e'de tanım ile sonuç aynı commit'te.
  - 07f ve 07g'nin tanımları sonuçtan önce ayrı commit'lerle kaydedildi (6a4439c, e81e61b). 07f commit içerikleri doğrulandı (`git_show_07f.txt`).
- Denetimler bağımsız değil: aynı yapay zekâ modelinin (Claude) ayrı oturumlarında yapıldı (F6).
- Planlanıp yapılmayan analizler (S2).
- Excel kohortu yayımlanan veriyle eşleşmiyor.

## Tablo S2: Karar günlüğü
v3'teki 1–18 numaralı satırlar ve denetim raporu 1'den alınan 1b, 3b, 4a, 4b, 11b, 12b satırları değişmeden korunuyor (bkz. `MAKALE_ISKELETI_v3.md`). 19–24 numaralı satırlar v4'teki gibi (aşağıda aynen). Ek satırlar 25–33.

| # | Tarih | Karar ya da olay | Sonuç görülmeden mi? | Kaynak |
|---|---|---|---|---|
| **Denetim raporu 2'den eklenenler (DENETIM_RAPORU_2_2026-10-02.md bölüm 3)** | | | | |
| 19 | — | **Planlanıp yapılmayan analizler:** (1) Madde kullanmayan, eşleştirilmiş alt örneklem ve regresyonla confound çıkarma. (2) Grup içi analizler: tekrar suç, çete, şiddet. (3) n = 139 ile ilk 60 s C bloğu duyarlılık analizi. Neden: 2026-10-01'de 03'ten sonra yapılan çerçeve değişikliği ve "yeni analiz eklenmez" ilkesi. Seçici raporlama eleştirisine karşı bu liste açıkça yazılmalı. | – | DENETIM_RAPORU_2 §3 |
| 20 | 2026-10-02 | **07d–e zaman damgası:** Tanım ve sonuçlar aynı git commit'inde (cbedc41). Tanımın sonuçlardan önce yazıldığı yalnızca CLAUDE.md ve ilerleme kaydıyla (başlangıç 09:12:41) destekleniyor. | Bkz. açıklama | DENETIM_RAPORU_2 §3 |
| 21 | 2026-10-02 | **07e kuralının ifade hatası:** Kural sohbet tarafında yazıldı ve "06" diyordu; doğrusu 03(b) sg–cg (bkz. E2). Sonuç değişmiyor. | Hata sonuçtan sonra fark edildi; kural değiştirilmedi, not eklendi | DENETIM_RAPORU_2 §3; CLAUDE.md notu |
| 22 | 2026-10-02 10:11 | **07f tanımı** (DENETIM_RAPORU_2 §4): uzun blok modelinin sg2'ye transferi; karar p < 0,05. Ayrı bir commit'le kaydedildi: **6a4439c**. | **Evet. Ayrı commit, analizden önce** | git 6a4439c |
| 23 | 2026-10-02 10:20 | **07f sonucu:** transfer AUC 0,582, p = 0,104 → transfer kanıtı yok; iddia beş modelin hepsi için geçerli. Commit: **11790e8**. | – | git 11790e8; `07f_..._rapor` |
| 24 | 2026-10-02 | DENETIM_RAPORU_2: E1–E8 metin ve şekil düzeltmeleri (v2/v3 dosyaları, eskiler korundu); 07e betimsel harita (test yok) | – | DENETIM_RAPORU_2 |
| **Denetim raporu 3'ten eklenenler (DENETIM_RAPORU_3_2026-10-02.md, F6 ve bölüm 5)** | | | | |
| 25 | 2026-10-02 | **07f'nin önerilme zamanı:** 07f, 07e'nin sonucu (0,746) görüldükten sonra önerildi. Kendi sonucu görülmeden tanımlandı ve yalnızca iddiayı daraltabilecek yönde kuruldu (p < 0,05 → "transfer ediyor", iddia daraltılır). | 07e sonucu görülmüştü; 07f sonucu görülmeden | DENETIM_RAPORU_3 F6 |
| 26 | 2026-10-02 | **07f commit içerik doğrulaması:** `git show` çıktısı `git_show_07f.txt`'de. 6a4439c yalnız CLAUDE.md'ye 9 satır ekliyor; 11790e8 yalnız 07f betiği ve çıktıları (7 dosya). | – | `git_show_07f.txt` |
| 27 | 2026-10-02 | **K7 (F1):** DENETIM_RAPORU_2, E2'deki "06'nın 0,54'ü sg2 yüzünden düşük" ifadesi yanlıştı. sg2 hariç ROI düzeyinde de ayrışma yok (03(b) 0,53; 06 OOF ile sg vs cg 0,549, sg2 vs cg 0,518). Düzeltildi: 06 v4, 07de v3. | Hata sonuçlardan sonra fark edildi; sayı değişmedi | DENETIM_RAPORU_3 §5 |
| 28 | 2026-10-02 | **K8 (F3):** DENETIM_RAPORU_2, E4'teki başlık önerisinde "subgroup-specific" aşırı iddiaydı. Başlık F3'teki ilk tercihle değiştirildi; çerçeve "transferi gösterilemeyen ayrışma" oldu. | – | DENETIM_RAPORU_3 §5 |
| 29 | 2026-10-02 | **K9 (F4):** DENETIM_RAPORU_2, E5'teki "uzun göz kapalı blok, ayrışmanın göz artefaktına bağlı olmadığını gösteriyor" ifadesi desteklenmiyor. En büyük etkiler frontopolar; EOG yok. Düzeltildi: 07 v4, 07abc v4, 07de v3, Şekil S1 ve 2c başlıkları, iskelet v5. | – | DENETIM_RAPORU_3 §5 |
| 30 | 2026-10-02 | **K10 (F2):** "Tespit edilebilirlik sınırı ≈ 0,60–0,65" ifadesi (analist ve denetim tarafında) anlamlılık eşiği ile dışlanabilen etkiyi karıştırıyordu. 07g'nin kesin GA'larıyla değiştirildi. | – | DENETIM_RAPORU_3 §5 |
| 31 | 2026-10-02 12:08 | **07g tanımı** (DENETIM_RAPORU_3 §3): keşifsel AUC'lerin %95 GA'ları; yalnız nicelendirme, karar kuralı yok; yeniden üretilen AUC'ler kayıtlıyla birebir aynı olmazsa dur. Ayrı commit: **e81e61b**. 07–07f sonuçları görüldükten sonra önerildi. | **Evet (07g sonucu açısından). Ayrı commit, analizden önce** | git e81e61b |
| 32 | 2026-10-02 12:12 | **07g sonucu:** 1120 AUC değeri kayıtlıyla aynı (maks fark 5,55e-17). Transfer GA üst sınırları 0,660–0,704. Hiçbir iddia güçlendirilmedi. İlk çalıştırma doğrulamadan sonra konsol kodlama hatasıyla durdu; kayıtlı skorlarla yeniden çalıştırıldı. Commit: **e5dfeb6**. | – | git e5dfeb6; `07g_auc_ci_rapor_v1` |
| 33 | 2026-10-02 | **Denetimlerin tanımı (F6):** DENETIM_RAPORU 1–3, aynı yapay zekâ modelinin (Claude) ayrı bir oturumunda yapıldı. Yöntem bölümünde ve S2'de "bağımsız denetim" denmez; derginin yapay zekâ beyanıyla tutarlı olmalı. | – | DENETIM_RAPORU_3 F6 |
| 34 | 2026-10-02 | DENETIM_RAPORU_3: F1–F7 metin düzeltmeleri (06 v4, 07 v4, 07abc v4, 07de v3, 07f v2, şekil başlıkları v4, Tablo S-n v2, Tablo S4 v1, iskelet v5; eskiler korundu). | – | DENETIM_RAPORU_3 |

## Şekiller
| No | Dosya | İçerik |
|---|---|---|
| Şekil 1 | `Fig1_leakage_v2` | Sızıntı |
| **Şekil 2** | `Fig2_exploratory_cascade_v3` (dosya değişmedi; başlık v4) | (a) sg vs cg, bütün kesitler (p = 0,0498 etiketi; "long eyes-closed block"); (b) sg2'ye transfer, 5 model; başlıkta anlamlılık eşiği ve 07g GA'ları (F2); (c) göz kapalı epoklar (2 × 50 s), C bloğu delta ve A bloğu alfa; uzun blokta alfa farkı yok (F4) |
| Şekil 3 | `Fig3_primary_alpha_reactivity_v2` | Birincil test |
| Şekil 4 | `Fig4_prespecified_null_v2` | ROI düzeyinde null; başlıkta örneklem farkı 111/100 ve analiz seçimleri (F7) |
| Şekil 5 | `Fig5_cohort_v2` | Kohort |
| **Şekil S1** | `FigS_07e_feature_map_v1` (dosya değişmedi; başlık v4) | 07e kanal × bant Hedges g (betimsel); frontopolar yoğunlaşma, beta ↓, alfa farkı yok; "küçük–orta" (F4) |

İngilizce başlık taslakları: `figures/FIGURE_CAPTIONS_v4.md`.

## Tablolar
- **Tablo 1:** `09_tables_v1_2026-10-02_Table1.*` (değişmedi).
- **Tablo S-n:** `09_tables_v2_2026-10-02_TableSn.*` (07f ve 07g satırları eklendi).
- **Tablo S4:** `09_tables_v2_2026-10-02_TableS4.*`: keşifsel analizler 07–07f; AUC (tekrar ortalaması ve ortalama skordan), 07g %95 GA, sıfır ortalaması, p, dengeli doğruluk, GD, Sen/Spe/F1, sg2 "suçlu" oranı, atipik sg2 hariç transfer AUC'si.
- **Diğerleri:** v3'teki gibi.
