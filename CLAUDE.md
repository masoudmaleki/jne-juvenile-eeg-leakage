## ANALİZ DONDURULDU (2026-10-02). Yeni analiz, öznitelik, model ya da analiz betiği çalıştırılmaz. Yalnız kayıtlı sonuçları okuyan şekil ve tablo betikleri çalıştırılabilir; sayılar değişmez. İstisna: hakem isteği. Bu durumda önce CLAUDE.md'ye tanım yazılır, ayrı commit atılır, sonra çalıştırılır.

# Proje: Suçlu çocuklar vs kontrol — dinlenim EEG (OpenNeuro ds006923 / NEMAR on006923)

Yazar: Doç. Dr. Mesut Melek (Gümüşhane Üni.). İletişim dili Türkçe; sert ve dürüst geri bildirim istenir.
Hedef: SCI-E Q2 (iyi kurulursa Q1'e yakın) makale. Hazır Excel öznitelikleriyle yapılacak düz bir "PSD + ML" çalışması Q3'te kalır.

## Veri seti
- 140 erkek: 74 suçlu (sg = 49, sg2 = 25), 66 kontrol (cg). Yaş 14–19.
- Biosemi ActiveTwo, 128 EEG + 3 ECG + 2 EOG kanalı. 2048 Hz kayıt, 128 Hz'e indirilmiş. Şebeke frekansı 60 Hz. events.tsv yok.
- Protokol: 4 dk göz kapalı/açık dönüşümlü (C-O-C-O), ardından 8 dk göz kapalı.
- `*_acq-epochs_eeg.set`: 4 epok (README'ye göre kırpma sonrası yaklaşık 50 s; yan dosyadaki "60 s" bilgisi güvenilmez).
- `*_desc-preprocessed_eeg.set`: Yan dosyada 720 s yazıyor, yani 12 dakikanın tamamı muhtemelen içeride (README bunun aksini söylüyor). İLK DOĞRULANACAK ŞEY BU. [Not 2026-10-02: DOĞRULANDI (01 audit) — preprocessed = tam ~740 s kayıt; bkz. "Audit sonuçları".]
  Önişleme: 1–40 Hz FIR, ortalama referans, ASR, ICA + ICLabel.
- `code/` klasöründe hazır öznitelikler var: 2048 Excel dosyası (4 bant × C/O × 2 epok × 128 kanal) ve `CAR_FREC_DATS.mat`. Pipeline'ı üreten betik yok.
- Yan JSON dosyalarındaki üstveri şablon halinde: 140 deneğin hepsinde kurum "Oasis" yazıyor, kontroller dahil. Site bilgisi bu dosyalardan çıkarılamaz.

## Kritik confound'lar (participants.tsv)
- Esrar: suçlu 55/74, kontrol 0/66. Kokain: 49/74 vs 0/66. Okul terki: 60/74 vs 0/66.
- Sosyoekonomik tabaka 1: 68/74 vs 21/66. Kayıt yeri farklı: ıslah kurumu vs okul.
- Madde kullanmayan suçlu (esrar = kokain = Hayır): 19 kişi. Buna tabaka 1 şartı eklenince 15 suçluya karşı 21 kontrol kalıyor.
- => Ham suçlu/kontrol sınıflandırması büyük olasılıkla madde kullanımını, site farkını ve sosyoekonomik farkı öğrenir. Yüksek doğruluk tek başına bulgu değildir.

## Şüpheli denekler (annex dosya boyutlarından çıkarıldı, açılıp doğrulanacak)
[Not 2026-10-02: DOĞRULANDI (01 audit); güncel durum "Audit sonuçları" bölümünde. sub-1084sg2 için "~20 s" bilgisi yanlıştı: veri harici .fdt'de ve dosya yok.]
- sub-1009sg, 1013sg, 1020sg, 1021sg: epoklu dosya ~7 MB (normali ~13,6 MB, muhtemelen 2 epok), işlenmiş dosya ~11 MB (normali ~50 MB).
- sub-1084sg2: işlenmiş dosya 1,3 MB (~20 s).
- Kısa kayıtların hepsi suçlu grupta. Bu denekler dışlanmalı ya da ayrıca raporlanmalı.

## Audit sonuçları (2026-10-01, analysis/01_data_audit_v2) — DOĞRULANDI
- preprocessed .set = tam kayıt (~740 s), 128 Hz, 128 EEG kanalı, tek parça. Event kodu 64 = göz kapalı, 128 = göz açık.
  Dizi: C60 | O60 | C60 | O60 | C~480 s (uzun göz kapalı blok) | O~1 s.
- acq-epochs = preprocessed'in alt kesitleri (her C/O işaretinden 5 s sonra başlayan 50 s; fark 0 µV). Yeni bilgi içermiyor, ana kaynak preprocessed.
- EX1–EX8 (EOG/ECG) kanalları çıkarılmış, dosyada yok. Kanal rank'ı 128, düz ya da NaN kanal yok.
- Dışlanacak / ayrı ele alınacak denekler:
  - sub-1009sg, 1013sg, 1020sg, 1021sg: yalnızca ~157 s ve yalnızca C|O (60 s + 80 s). Uzun kapalı blok yok.
  - sub-1084sg2: veri harici .fdt'de ve dosya yok, kanal sayısı 136 (EX kanalları çıkarılmamış). Okunamıyor.
  - sub-2019cg: uzun blok 474 s ve O işaretiyle bitmiyor (kullanılabilir).
- Uzun göz kapalı blok kullanılabilir: cg 66, sg 45, sg2 24 → toplam 135.
- **KAYIT TARİHİ CONFOUND'U (en kritik):** sg 2021-07…09, sg2 2021-12…2022-06, cg 2022-02…09.
  sg ile cg arasında zamansal örtüşme sıfır. Ancak sg2 ile cg 2022 Mayıs–Haziran'da örtüşüyor (Nisan 2022'de cg kaydı yok).
  Ham dosya yolları: D:\Infractores (sg, sg2) / D:\Control (cg).
- Genlik (preprocessed, tam COCOCO dizili ve okunabilir 134 denek): kanal SD medyanı cg 7,1, sg 6,7, sg2 7,2 µV (Kruskal-Wallis p≈0,14). Mutlak güç yerine göreli güç / aperiodik düzeltilmiş öznitelik kullanılmalı.

## Önceden belirlenmiş birincil analiz (2026-10-01'de kilitlendi; sonuçlara bakarak DEĞİŞTİRİLMEZ)
- Kesit: 3. göz kapalı işareti + 5 s'den başlayan sabit 465 s (sub-2019cg'nin 474 s'lik bloğuna sığar). Ayrıca iki yarı (H1, H2; her biri 232,5 s).
- PSD: Welch, 4 s Hann penceresi, %50 örtüşme (0,25 Hz çözünürlük).
- Göreli güç: delta 1–4, teta 4–8, alfa 8–13, beta 13–30 Hz; payda 1–30 Hz toplamı. Gama öznitelik DEĞİL (yalnız EMG kontrolü).
- FOOOF (fooof 1.1, specparam kurulmayacak): BİRİNCİL = aperiodik 'fixed', 3–30 Hz.
  'knee', 2–30 Hz yalnızca duyarlılık analizi; ikisi arasında sonuçlara bakarak seçim yapılmaz.
- IAF: birincil = FOOOF'un 7–13 Hz'deki en güçlü tepesi; ikincil = aperiodik bileşeni çıkarılmış (düzleştirilmiş) spektrumda 7–13 Hz ağırlık merkezi (CoG). PSD argmax kullanılmaz.
- EMG / kanal dışlama (denek içi, tam kesit üzerinden belirlenir, yarılarda aynı kanal seti):
  EMG indeksi = log10 PSD – log10 f doğrusal eğimi, 30–40 Hz (daha düz/pozitif = daha fazla kas).
  Kanal dışlanır: birincil FOOOF R² < 0,9 VEYA EMG indeksi robust z > 3 (medyan ± 3·1,4826·MAD, tek yönlü).
  ROI öznitelikleri kalan kanalların ortalama spektrumundan hesaplanır. EMG indeksi grup analizlerinde ortak değişkendir.
- Uyanıklık: öznitelikler tam kesit + H1 + H2 için ayrı; 30 s pencerelerde teta/alfa oranı zaman serisi kaydedilir, eğimi (log oran / dk) uyanıklık göstergesidir.
  Raporlama: H1 sonuçları tam kesit sonuçlarıyla yan yana verilir; teta/alfa eğimi (global) kovaryat olarak kullanılır.
- Denek düzeyi QC (2026-10-01 eklendi; ROI dosyası v3):
  Kanalların > %25'i (> 32/128) dışlanırsa denek "atipik spektrum" olarak bayraklanır. Bu deneklerde yalnız EMG kuralı (robust z > 3)
  uygulanır, R² kuralı uygulanmaz; ROI kalan tüm kanallarla hesaplanır. Birincil analizde DAHİL, duyarlılık analizinde HARİÇ.
  Bayraklanan: sub-1105sg2 (R² kuralıyla 88 kanal), sub-1114sg2 (57 kanal).
  NOT: Bu QC değişikliği grup karşılaştırması yapılmadan, yalnızca QC verisine bakılarak yapıldı
  (tetikleyen: R² kuralının iki denekte tüm spektrumu atipik olan, kas artefaktı olmayan kanalları budaması).

## MAKALE ÇERÇEVESİ (2026-10-01'de belirlendi; batch negatif kontrolü sonrası)
"Suçluluk biyobelirteci" DEĞİL → "titiz null sonuç + sızıntı/confound denetimi".
Dayanak: 03 batch negatif kontrolü (analysis/03_batch_negcontrol_v1_2026-10-01_rapor.md):
14 spektral öznitelikle sg vs cg AUC 0,53; (a) sg vs sg2 AUC 0,63, p=0,053 (α=0,025).

### Önceden belirlenmiş analizler (ayrıntılar: analysis/04_05_PLAN_v*_2026-10-01.md, onaylanınca kilitlenir)
- **04 Sızıntı gösterimi:** v1.0.0/code Excel öznitelikleri (2048 dosya, 14.336 öznitelik; yalnız sg+cg, sg2 yok).
  Önce bütünlük denetimi: sabit/NaN sütunlar (Kurtosis ≈ 1,5 sabit), denek ID eşleşmesi (11 cg ID'si + sub-1011sg participants.tsv'de yok).
  Naif pipeline (epok bazlı CV + tüm veride ANOVA top-k + SVM/RF) ile aynı verinin denek bazlı iç içe CV versiyonu karşılaştırılır.
  **04-A bulguları (2026-10-01, analysis/04a_excel_audit_v1_2026-10-01_rapor.md) — DOĞRULANDI:**
  - 2048 Excel = 4 bant × {C_1,O_1,C_2,O_2} × 128 kanal; her biri 112 denek (cg 66 Label=0, sg 46 Label=1), 7 istatistik
    (Power, RMS, Standarddesv, Minimun, Maximun, Symetry, Kurtosis). NaN yok.
  - THETA_EP_C_2_can_B12.xlsx 0 bayt (yayımlanan zip'te de). CAR_FREC_DATS.mat (Datos[bant][koşul][kanal]) Excel ile birebir aynı ve B12'yi içerir → 04-B kaynağı .mat.
  - RMS/SD/Min/Max/Symetry/Kurtosis her hücrede TAM 3 değerden hesaplanmış (SD n−1). 3 değerin kurtosis'i her zaman 1,5 → Kurtosis bilgisiz.
    3 değerin frekans noktası olup olmadığı belirsiz (tüm bantlarda 3 → tek bir eşit aralıklı ızgarayla uyumsuz). Power ayrı hesaplanmış.
  - Excel kohortu yayımlanan veriyle EŞLEŞMİYOR: 12 Excel ID'si (cg 2013, 2024, 2025, 2027, 2035, 2039, 2041, 2058, 2069, 2073, 2076; sg 1011)
    veri setinde yok ve hiçbir kayıtla sinyal düzeyinde eşleşmiyor (r ≤ 0,66). Veri setindeki 40 denek Excel'de yok (sg2'nin tamamı, kısa kayıtlı 4 sg, 11 cg).
    Ortak 100 deneğin 100'ü acq-epochs ile kendisiyle eşleşiyor (r medyanı 0,915). Excel sonuçları yayımlanan EEG'den yeniden üretilemez.
  - 04-B kararları: Kurtosis birincil analizde içeride, duyarlılıkta çıkarılır; Kol 2 RF permütasyonu yapılmaz; naif kol k = 100, 10-fold.
  **04-B sonuçları (2026-10-02, analysis/04b_leakage_v1_2026-10-01_rapor.md):**
  - Naif N1 (tüm veride ANOVA top-100 + satır bazlı 10-fold): satır AUC RF 0,870 / SVM 0,855, doğruluk 0,79 / 0,76.
    Denek düzeyinde karıştırılmış etiketlerle bile satır AUC 0,78 / 0,74, doğruluk 0,73 / 0,69 → naif performansın çoğu sinyalsiz elde ediliyor.
  - Doğru P (denek bazlı iç içe): denek AUC RF 0,727 / SVM 0,658 (SVM sıfır dağılımı 0,48, p = 0,010).
  - Sızıntı ayrıştırması (satır AUC): epok/denek sızıntısı N2−N4 ≈ +0,21; tüm veride seçim N1−N2 +0,01–0,03, N3−N4 +0,04–0,09.
  - Duyarlılık: Kurtosis'siz aynı; doğrulanmış 100 denek P 0,685 / 0,615; yalnız göz kapalı P 0,654 / 0,603.
  - Yorum sınırı: P'nin şans üstü olması grup bulgusu DEĞİL (birincil değil; mutlak genliğe bağlı öznitelikler; 03'te genlikten
    bağımsız 14 öznitelikle sg vs cg 0,53; Excel kohortu yayımlanan veriyle eşleşmiyor) → 07 genlik ayrıştırması bunu sınar.
- **07 Genlik ayrıştırması (KEŞİFSEL; 2026-10-02'de SONUÇ GÖRÜLMEDEN tanımlandı):**
  Soru: 04-B P'deki şans üstü ayrışma mutlak genlikten mi geliyor?
  - Örneklem: kimliği doğrulanmış 100 denek (Excel ∩ veri seti; cg 55, sg 45); veri yayımlanan acq-epochs (4 epok: C1, O1, C2, O2).
  - Satır = denek × epok (400). Welch 4 s Hann, %50 örtüşme. Bantlar delta 1–4, teta 4–8, alfa 8–13, beta 13–30 Hz; 128 kanal → 512 öznitelik.
    (A) log10 mutlak bant gücü; (B) göreli bant gücü = bant / 1–30 Hz toplamı.
  - Pipeline = 04-B P (aynen): StandardScaler → SelectKBest(f_classif, k ∈ {10, 50, 100, 500}) → SVM RBF (C ∈ {0,1, 1, 10});
    dış StratifiedGroupKFold(5, shuffle) × 20 tekrar, iç StratifiedGroupKFold(5); denek skoru = satır karar değerlerinin ortalaması.
    Birincil metrik denek AUC; ek: dengeli doğruluk, GD [ACC, Sen, Spe, F1] (analysis/metrics_gd.py).
  - Sıfır: denek düzeyinde etiket karıştırma × 200, permütasyon başına 5 tekrar; p = (k+1)/201.
  - Operasyonel tanım: "ayrışma var" = permütasyon p < 0,05; "≈ şans" = p ≥ 0,05 (set başına, düzeltmesiz; keşifsel).
  - Yorum kuralı (önceden):
    A var, B ≈ şans → ayrışma mutlak genlikten (batch/kayıt koşulu ile tutarlı) → 05'e devam.
    A ve B ikisi de var → gerçek spektral fark ihtimali → DUR, kullanıcıya dön.
    A ≈ şans, B var → beklenmedik → DUR, kullanıcıya dön.
    İkisi de ≈ şans → 04-B'deki ayrışma Excel'e/kohorta özgü; raporla, 05'e devam.
  - **SONUÇ (2026-10-02, analysis/07_amplitude_decomp_v1_2026-10-02_rapor.md):** A AUC 0,754, B AUC 0,734; ikisi de p = 0,005
    (sıfır ≈ 0,48) → KURAL: DUR. 05/06 çalıştırılmadı, kullanıcı kararı bekleniyor.
    Betimsel: A'da cg > sg (genel genlik); B'de sg'de göreli delta ↑ (frontal ağırlıklı), alfa ↓.
    Kullanıcı değerlendirmesi: "mutlak genlik" hipotezi çürüdü → 07a–c.
- **07a–c (KEŞİFSEL; 2026-10-02'de SONUÇ GÖRÜLMEDEN tanımlandı).** Hepsi B seti (göreli bant gücü, 1–30 Hz paydası), 07 ile aynı
  100 denek (sg 45, cg 55) ve aynı P pipeline (SVM, k ∈ {10, 50, 100, 500}, C ∈ {0,1, 1, 10}; k > öznitelik sayısıysa tüm öznitelikler),
  dış 5-fold × 20 tekrar, 200 permütasyon (permütasyon başına 5 tekrar), checkpoint.
  - 07a: yalnız göz kapalı (C1 + C2; 200 satır) ve yalnız göz açık (O1 + O2; 200 satır), ayrı ayrı. Denek AUC.
  - 07b: yalnız göz kapalı, frontal C bloğu (C1–C32) çıkarılmış (96 kanal × 4 bant = 384 öznitelik).
  - 07c: 07a'nın göz kapalı modeli sg + cg ile eğitilir. Her dış katta aynı model held-out cg ile sg2'yi skorlar;
    kat-içi transfer AUC'si (03 yöntemi) 100 kat üzerinden ortalanır. sg2 = 24 (03 ile tutarlı; sub-1084sg2 hariç);
    25'li versiyon (1084sg2 acq-epochs ile) ek satır. Permütasyon: eğitim sg/cg etiketleri denek düzeyinde karıştırılır.
    Betimsel: sg / sg2 / cg için göz kapalı göreli delta (tüm kanallar, frontal C) ve alfa (tüm kanallar, A bloğu) medyanları.
  - "Yüksek" = AUC ≥ 0,65 ve permütasyon p < 0,05. "Korunuyor" (07b) = 07b AUC ≥ 0,65 ve p < 0,05.
  - Karar kuralları (önceden):
    - 07a kapalı AUC ≤ 0,60 ve 07a açık yüksek → oküler artefakt açıklaması.
    - 07a kapalı yüksek ve 07b korunuyor → gerçek spektral fark ihtimali; ardından 07c:
      07c AUC ≥ 0,60 ve p < 0,05 → kayıt dönemi/batch açıklaması zayıf; 07c AUC < 0,60 veya p ≥ 0,05 → batch açıklaması güçlü.
    - Kapsanmayan durumlar (ör. 07a kapalı 0,60–0,65 arası, 07a kapalı yüksek ama 07b korunmuyor → frontal kaynaklı) → "belirsiz"; raporla.
    - Her durumda sonuçtan sonra DUR. 05 yalnız kullanıcı onayıyla çalıştırılır.
  - **SONUÇ (2026-10-02, analysis/07abc_source_decomp_v1_2026-10-02_rapor.md): KURAL → BELİRSİZ (kural boşluğu: 0,60–0,65 arası
    tanımsızdı; eşik sonradan DEĞİŞTİRİLMEZ). Keşifsel ayrıştırma burada BİTTİ; yeni öznitelik/analiz yok.**
    07a kapalı 0,645 (p 0,015; eşiğin hemen altı), 07a açık 0,709 (p 0,005), 07b 0,582 (p 0,050), 07c transfer 0,569 (p 0,26).
    Betimsel (göz kapalı): göreli delta ↑ yalnız sg'de (sg2 ≈ cg); alfa ↓ sg2'de de (daha güçlü). Ayrışma açık > kapalı > kapalı-frontalsız.
- **07d–e (KEŞİFSEL; 2026-10-02'de SONUÇ GÖRÜLMEDEN tanımlandı; kaynak: DENETIM_RAPORU_2026-10-02.md bölüm 7).**
  Ortak: 07 ile aynı 100 denek (sg 45, cg 55) ve aynı P pipeline (SVM; k ∈ {10, 50, 100, 500}, C ∈ {0,1, 1, 10}),
  dış 5-fold × 20 tekrar, 200 permütasyon × 5 tekrar, checkpoint ve ilerleme kaydı. Karar: TEK ölçüt, permütasyon p < 0,05 (eşik boşluğu yok).
  Düzeltme yok; keşifsel p değerleri düzeltmesiz raporlanır (D9).
  - 07d (en güçlü modellerin sg2'ye transferi): 07c'nin kat-içi transfer yöntemi aynen (her dış katta held-out cg vs sg2, aynı model;
    kat AUC'leri ortalanır; sıfır: eğitim sg/cg etiketleri denek düzeyinde karıştırılır). sg2 = 24 (1084sg2 hariç; 25 ek satır).
    Üç model: (1) A log10 mutlak güç, tüm epoklar; (2) B göreli güç, tüm epoklar; (3) B göreli güç, göz açık (O1 + O2).
    sg2 için eğitimdekiyle aynı epoklar; sg2'nin A öznitelikleri de hesaplanır.
    Karar (model başına): p < 0,05 → "transfer ediyor"; aksi halde "transfer etmiyor".
    Herhangi bir model transfer ederse makale başlığındaki "genellenmiyor" iddiası daraltılır.
  - 07e (kayıt kesitinin etkisi): aynı 100 denek; 02 ile aynı 465 s'lik uzun göz kapalı blok (3. C işareti + 5 s),
    4 ardışık örtüşmesiz 116,25 s parçaya bölünür (satır = denek × parça, 400 satır). B seti (128 kanal × 4 bant;
    Welch 4 s Hann %50; payda 1–30 Hz); kanal dışlaması YOK.
    Karar: p < 0,05 → kanal düzeyindeki ayrışma uzun blokta da var; 06'daki null sonuç ROI ve model seçimine özgüdür (açıkça yazılır).
    [Not 2026-10-02 (DENETIM_RAPORU_2, E2): kuralın ifade hatası — "06" (sg+sg2 vs cg) değil, aynı grupları karşılaştıran
    03(b) sg vs cg (ROI + LR, 0,53, n = 111) ile 07e (kanal + SVM, 0,746, n = 100) eşleştirilmeli. Sonuç değişmez.]
    p ≥ 0,05 → ayrışma oturum başındaki kapalı/açık epoklarla sınırlı.
  - **SONUÇ (2026-10-02, analysis/07de_transfer_longblock_rapor_v1_2026-10-02.md):**
    07d transfer AUC: A tüm 0,549 (p 0,22), B tüm 0,589 (p 0,19), B açık 0,553 (p 0,29) → hiçbiri transfer etmiyor →
    "genellenmiyor" iddiası KORUNUR (tespit sınırı ≈ 0,60–0,65; ifade: "sg2'ye genellendiğine dair kanıt yok").
    [Not 2026-10-02 (DENETIM_RAPORU_3, F2): "tespit sınırı ≈ 0,60–0,65" anlamlılık eşiği ile dışlanabilen etkiyi karıştırıyor.
    Anlamlılık eşiği (sıfırın tek yönlü %95'i) 0,586–0,638; 07g %95 GA: A tüm 0,439–0,662, B tüm 0,475–0,702, B açık 0,446–0,660
    → veri "transfer yok" ile "orta düzeyde transfer" arasındaki her şeyle uyumlu. "Transfer etmiyor" = kural etiketi (= transfer kanıtı yok).]
    07e uzun blok AUC 0,746 (p ≤ 0,005) → kanal düzeyi ayrışma uzun blokta da var → 06 null ROI/model seçimine ÖZGÜ (açıkça yazılacak). [Not 2026-10-02 (F7): analiz seçimlerine özgü (ROI ya da kanal düzeyi, model, kanal dışlaması, örneklem 111/100)]
- **07f (KEŞİFSEL; 2026-10-02'de SONUÇ GÖRÜLMEDEN tanımlandı; kaynak: analysis/DENETIM_RAPORU_2_2026-10-02.md bölüm 4).**
  Amaç: 07e uzun blok modeli (0,746) en güçlü modellerden biri; transferi test edilmedi.
  - Model: 07e modeli (B seti, uzun göz kapalı blok, 4 × 116,25 s, kanal dışlaması yok; sg 45 + cg 55 ile eğitim; P pipeline aynen).
  - Test kümesi: sg2'nin uzun bloğu, 24 denek (sub-1084sg2'nin uzun bloğu yok → dahil değil).
  - Yöntem: 07c kat-içi transfer AUC'si aynen (her dış katta held-out cg vs sg2, aynı model; 100 kat ortalaması);
    20 tekrar; sıfır: eğitim sg/cg etiketleri denek düzeyinde karıştırılır, 200 permütasyon × 5 tekrar; checkpoint.
  - Karar (tek ölçüt): p < 0,05 → "transfer ediyor"; makaledeki iddia daraltılır. Aksi halde "transfer kanıtı yok" iddiası beş modelin hepsi için geçerli.
    Çoklu karşılaştırma düzeltmesi yok ("transfer kanıtı yok" iddiası açısından tutucu).
  - Zaman kaydı: bu tanım, analiz çalıştırılmadan önce ayrı bir git commit'i ile kaydedildi.
  - **SONUÇ (2026-10-02; tanım commit 6a4439c, sonuç commit 11790e8; analysis/07f_longblock_transfer_rapor_v1_2026-10-02.md):**
    transfer AUC 0,582 (tekrarlar 0,526–0,631), sıfır 0,504, p = 0,104 → transfer kanıtı YOK →
    "no evidence of transfer" iddiası beş modelin hepsi için geçerli (07c, 07d × 3, 07f).
    [Not 2026-10-02 (DENETIM_RAPORU_3, F2): anlamlılık eşiği 0,601; 07g %95 GA 0,463–0,704 → AUC > 0,70 yaklaşık dışlanır;
    orta düzeyde transfer dışlanamaz. "İmza sg'ye özgü" ve "kaynak ile transfer arasında açık fark" ifadeleri desteklenmiyor (fark test edilmedi).
    Commit içerikleri doğrulandı: analysis/git_show_07f.txt (6a4439c yalnız CLAUDE.md, +9 satır).]
- **07g (YALNIZ NİCELENDİRME, karar kuralı YOK; 2026-10-02'de SONUÇ GÖRÜLMEDEN tanımlandı; kaynak: analysis/DENETIM_RAPORU_3_2026-10-02.md bölüm 3).**
  Amaç: keşifsel AUC'ler için %95 GA; F2'deki yaklaşık GA'ların yerine kesin değerler. Hiçbir iddia bu sonuca göre güçlendirilmez.
  - Kaynak modeller (6): 07 A_log_abs, 07 B_relative (tüm epoklar), 07a kapalı, 07a açık, 07b (kapalı, C bloğu çıkarılmış), 07e uzun blok.
    Gerçek çalıştırma aynı seed'lerle (M7.SEED + r, r = 0–19) aynı fonksiyonlarla (M7.nested'in birebir kopyası, denek skoru da döner)
    tekrarlanır. Her tekrarın denek AUC'si checkpoint'teki kayıtlı değerle |fark| ≤ 1e-12 olmalı; değilse çalışma DURUR.
    Denek skoru = 20 tekrardaki (denek ortalaması) karar değerlerinin ortalaması. GA: sınıf içi tabakalı denek bootstrap'ı
    (06 ile aynı: sg ve cg ayrı ayrı yerine koyarak; 2000 yineleme; rng = default_rng(20261001), model başına yeniden başlatılır; percentile).
    Raporda hem kayıtlı nokta tahmini (tekrar AUC ortalaması) hem ortalama skordan AUC verilir.
  - Transfer modelleri (5): 07c (B kapalı), 07d A tüm, 07d B tüm, 07d B açık, 07f (B uzun blok). Aynı seed'ler, aynı transfer yöntemi
    (07abc transfer'in birebir kopyası; ek olarak her katın held-out cg denek kimlikleri ve skorları ile 25 sg2 deneğinin skorları kaydedilir).
    Her katın auc_sg2_24 (ve varsa auc_sg2_25) değeri kayıtlı transfer_folds CSV'siyle |fark| ≤ 1e-12 olmalı; değilse DURUR.
    GA: ağırlıklı denek bootstrap'ı. Her yinelemede cg (55) ve sg2 (24) için çok terimli çarpanlar çekilir (w ~ Multinomial(n, 1/n));
    aynı çarpanlar o yinelemedeki tüm katlarda kullanılır. Kat AUC'si = ΣΣ wᵢwⱼ[1(sⱼ > sᵢ) + ½·1(sⱼ = sᵢ)] / (Σwᵢ · Σwⱼ)
    (i held-out cg, j sg2). Held-out cg ağırlık toplamı 0 olan katlar o yinelemede ortalamaya alınmaz. 100 katın ortalaması; 2000 yineleme;
    rng = default_rng(20261001), model başına yeniden başlatılır; percentile GA. Nokta tahmini = kayıtlı kat AUC ortalaması.
  - Betimsel duyarlılık (yeniden eğitim yok, GA yok): atipik spektrumlu sg2 denekleri sub-1105sg2 ve sub-1114sg2 hariç (22 sg2) transfer AUC'leri.
  - Raporlama biçimi: "AUC (GA L–U); AUC > U yaklaşık olarak dışlanır". Sınırlılık: GA yalnız denek örneklemesini içerir; model eğitimindeki
    (seed/katlama) oynaklık dahil değildir.
  - Zaman kaydı: bu tanım, analiz çalıştırılmadan önce ayrı bir git commit'i ile kaydedildi.
  - **SONUÇ (2026-10-02; tanım commit e81e61b, sonuç commit e5dfeb6; analysis/07g_auc_ci_rapor_v1_2026-10-02.md, analysis/07g_auc_ci_v1_2026-10-02_results.csv):**
    Doğrulama GEÇTİ: 1120 AUC (120 kaynak tekrarı + 1000 transfer katı) kayıtlıyla aynı (maks |fark| 5,55e-17).
    Kaynak (ortalama skordan AUC, GA; tekrar ortalaması): 07 A 0,771 (0,672–0,860; 0,754), 07 B 0,800 (0,706–0,886; 0,734),
    07a kapalı 0,709 (0,604–0,809; 0,645), 07a açık 0,767 (0,669–0,859; 0,709), 07b 0,609 (0,495–0,725; 0,582), 07e 0,781 (0,685–0,867; 0,746).
    Transfer (GA): 07c 0,569 (0,439–0,688), 07d A 0,549 (0,439–0,662), 07d B 0,589 (0,475–0,702), 07d B açık 0,553 (0,446–0,660),
    07f 0,582 (0,463–0,704). Atipik 2 sg2 hariç (betimsel): 0,534–0,566. Hiçbir iddia güçlendirilmedi.
- 07e betimsel öznitelik haritası (test yok): analysis/07e_feature_map_v1_2026-10-02.csv, figures/FigS_07e_feature_map_v1.*
  (|g| ≤ 0,58; sg'de göreli delta ↑ (C, D blokları), teta ↓ (en belirgin C bloğu), alfa ≈ 0).
  [Not 2026-10-02 (DENETIM_RAPORU_3, F4): en büyük 10 etkinin 10'u, en büyük 20'nin 18'i C bloğunda (frontopolar/ön-frontal); beta ↓ da var;
  A bloğu alfa medyan g = 0,015. |g| ≤ 0,58 "küçük–orta". Uzun blok göz kapalı olsa da oküler/deri kaynaklı açıklama DIŞLANMAZ (EOG yok).]
- DENETIM_RAPORU_4_2026-10-02.md G1–G7 uygulandı (2026-10-02): 07g rapor v2, iskelet v6 (Tablo S2 satır 35–38), figures/FIGURE_CAPTIONS_v5.md,
  08 v4 → Şekil 2 v4 (b panelinde 07g GA'ları; sayı değişmedi), analysis/git_show_07g.txt. Makale metninde GA'lar iki ondalıkla.
  "%80 güç" sayısı makaleye girmez (G3). Güncel teslim kopyaları: GUNCEL/ (00_BENI_OKU.md). Analiz aşaması KAPANDI.
- DENETIM_RAPORU_3_2026-10-02.md F1–F7 uygulandı (2026-10-02): 06 v4, 07 v4, 07abc v4, 07de v3, 07f v2, figures/FIGURE_CAPTIONS_v4.md,
  09 v2 (Tablo S-n v2, Tablo S4 v1), iskelet v5 (Tablo S2 satır 25–34). "Tespit sınırı", "subgroup-specific", "sg'ye özgü" ifadeleri kullanılmaz.
  Denetimler "bağımsız" DEĞİL: aynı yapay zekâ modelinin (Claude) ayrı oturumu (F6).
- DENETIM_RAPORU_2026-10-02.md D1–D12 uygulandı: v2 raporlar (04b, 06, 07, 07abc), 08 v2 şekiller, 09 Tablo 1 / Tablo S-n, iskelet v3.
- 04-B GD eki tamam (analysis/04b_leakage_gd_v1_2026-10-02_results.csv; AUC'ler kayıtlıyla aynı, maks fark 1e-16).
- **05 SONUÇ (birincil, 2026-10-02):** n = 136 (suçlu 70, cg 66); ARI medyanı 0,636 vs 0,678; Mann-Whitney p = 0,395;
  rank-biserial −0,085 [−0,28; 0,11]; HL −0,030 [−0,10; 0,04]; yaş + EMG kovaryatlı p = 0,89. NEGATİF.
- [Not 2026-10-02 (D2): doğru ifade "AUC 0,54 [%95 GA 0,44–0,63]; tekrar ortalaması 0,51"; dışlama yaklaşık.]
- **06 SONUÇ (2026-10-02):** suçlu (69) vs cg (66), 14 öznitelik: AUC 0,511 (tekrarlar 0,46–0,57); bootstrap GA 0,44–0,63
  (DeLong 0,44–0,64) → AUC > 0,63 (Cohen d ≈ 0,48) %95 güvenle dışlanır.
- Makale iskeleti: analysis/MAKALE_ISKELETI_v1.md. [Not 2026-10-02: güncel sürüm analysis/MAKALE_ISKELETI_v4.md.] [Not 2026-10-02 (DENETIM_RAPORU_4): güncel sürüm analysis/MAKALE_ISKELETI_v6.md.] [Not 2026-10-02 (DENETIM_RAPORU_3): güncel sürüm analysis/MAKALE_ISKELETI_v5.md; başlık: "High accuracy without demonstrated generalization: data leakage and recording confounds in resting-state EEG classification of juvenile offenders".]
- **GD:** analysis/metrics_gd.py (referans koddan uyarlandı; 7 örnekte fark 0). Girdi [ACC, Duyarlılık, Özgüllük, F1], pozitif = suçlu.
  04-B ve 07 tablolarına ek sütun; ana metrik AUC. NAoSP şimdilik yok.
- **05 Alfa reaktivitesi: TEK birincil hipotez testi.** Posterior ROI, (göz kapalı alfa − göz açık alfa) / (kapalı + açık),
  ilk 4 dakikadaki C/O blokları (her blok işaretten 5 s sonra başlar). Suçlu (sg+sg2) vs cg, Mann-Whitney U, iki yönlü, α=0,05.
  Kovaryat duyarlılığı: yaş, EMG.
- **Null sonucun nicelenmesi:** sg+sg2 vs cg iç içe CV AUC'si (03 ile aynı 14 öznitelik ve pipeline) için bootstrap %95 GA;
  GA üst sınırından "dışlanabilen en küçük etki" ifadesi.
- **Bundan sonra yeni öznitelik veya model EKLENMEZ.** Eklenirse "keşifsel" olarak etiketlenir ve birincil sonuçlarla karıştırılmaz.
  (Aşağıdaki "Planlanan analizler" listesi bu çerçeveye tabidir; birincil test yalnız 05'tir.)

## Analiz ilkeleri
- Birincil veri: 480 s göz kapalı blok (n=135). Duyarlılık analizinde tüm deneklerin ilk 60 s C bloğu kullanılır (n=139). [Not 2026-10-02: YAPILMADI — 2026-10-01 çerçeve değişikliği ve "yeni analiz eklenmez" ilkesi; Tablo S2'de planlanıp yapılmayanlar listesinde.]
- Batch negatif kontrolü ZORUNLU:
  (a) sg ile sg2 ayrılabiliyor mu? İkisi de suçlu, sadece kayıt dönemi farklı. Yüksek doğruluk çıkarsa batch etkisinin kanıtıdır.
      [Not 2026-10-02: Adım 0 ile GEÇERSİZ — sg ile sg2 şiddet suçu, alkol ve yaşta da farklı; pozitif sonuç "batch" diye yorumlanamaz (03 plan v2).]
  (b) sg + cg üzerinde eğitilen model, sg2 ile cg'yi (zamanca örtüşen kayıtlar) ayırabiliyor mu?
      [Not 2026-10-02 (D4): "örtüşen" değil "kısmen örtüşen" — aynı ay yalnız Mayıs–Haziran 2022 (sg2 11, cg 9).]
- Doğrulama denek bazında yapılır (LOSO/LOO). Epok düzeyinde bölme yasak. Öznitelik seçimi ve ölçekleme iç döngüde kalır.
- Planlanan analizler:
  1. Confound kontrollü tasarım: madde kullanmayan, eşleştirilmiş alt örneklem + regresyonla confound çıkarma.
  2. Grup içi analizler: tekrar suç (24/50), çete üyeliği (23/51), şiddet suçu vs diğer suçlar.
     ⚠ "Şiddet vs diğer suç" KEŞİFSEL: sg/sg2 alt grubu ve kayıt dönemiyle confound'lu
     (birincil suç şiddet [Homicide, Sexual_Abuse, Violence, Abduction, Kidnapping]: sg 39/45 vs sg2 6/24, Fisher p=5e-7;
     analysis/03_step0_demografi_v1_2026-10-01.csv). Doğrulayıcı sonuç olarak sunulamaz.
  3. Alfa reaktivitesi (göz kapalı/açık oranı).
  4. sg ve sg2 karşılaştırması (olası batch etkisi).
- Raporlama: Dengesiz sınıflarda Golden Distance / NAoSP kullanılır, ama ana katkı olarak sunulmaz.
- Literatür: Aynı kohortla nöropsikoloji (Data 2023, BA 0,885) ve MRI (Data 2024, doğruluk ~0,52–0,66) çalışmaları var. Bu veri setiyle yapılmış bir EEG yayını 2026-09 itibarıyla bulunmadı. Veri 2025-11-11'den beri açık.

## YAZIM AŞAMASI KARARLARI
- 2026-10-02: Hedef dergi Journal of Neural Engineering (IOP Publishing, hibrit). JCR 2026: Engineering, Biomedical Q2 (53/130); Neurosciences Q2 (109/330). Kaynak: LetPub/Peeref; Clarivate'ten teyit edilecek.
- Makale türü: Paper. Uzunluk normalde ≤12.000 kelime (≈14 dergi sayfası). Hedef ana metin ~9.400 kelime. Ana görseller: Şekil 1–5, Tablo 1–4.
- Özet: Objective / Approach / Main results / Significance başlıkları, ≤300 kelime.
- Kaynak stili: Vancouver (numaralı).
- Hakemlik: tek-kör (single-anonymous). Analiz günlüğü ve depo bağlantıları anonimleştirilmez.
- Ekler varsayılan olarak hakemliğe girmez. İddiayı taşıyan içerik ana metinde kalır: 07d/07f karar kuralları, beş transfer AUC'si, p değerleri ve GA'lar. Ek dosya başına ≤50 MB, toplam ≤150 MB.
- YZ beyanı: Teşekkür bölümünde IOP şablonuyla ayrı beyan. Yöntem'de analizlerde kullanılan araç ve model adları yazılır: Claude Code, model Claude Opus 5.5 (git Co-Authored-By kaydı: 15 commit'in 15'inde; ilk c325305, son 591d126; başka model adı yok). Sohbet tarafındaki denetimlerin modelleri yazar tarafından eklenecek.
- Açık erişim: TÜBİTAK–IOP Oku-Yayımla 2026–2028 (EKUAL). Sorumlu yazarın kurumu EKUAL üyesi olmalı.
- 2026-10-02: Makale LaTeX ile yazılacak (IOP iopjournal sınıfı, ioplatextemplate.zip). Bölümleri sohbet tarafı ayrı .tex dosyaları olarak yazar. Tabloların .tex hâlini PyCharm kayıtlı CSV'lerden üretir; hiçbir sayı elle yazılmaz. Kaynaklar manuscript/refs.bib dosyasında (BibTeX, numaralı).
- Grup etiketleri betikte tek bir sözlükten (LABELS) gelir. Ad kararı verilince yalnız bu sözlük değişir.
