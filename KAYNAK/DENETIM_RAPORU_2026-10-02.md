# Bağımsız denetim raporu (2026-10-02)

Denetimi yapan: sohbet tarafındaki Claude. Bu rapor, PyCharm'da üretilen bütün analizlerin bağımsız kontrolüdür.

## 1. Kapsam

**Okunanlar:**
- Raporlar ve planlar: 02 ile 07c arası, iskelet v2, şekil başlıkları.
- Betikler: 02 v2/v3, 03, 04a, 04b, 05, 06, 07, 07abc, 08, metrics_gd.
- Sonuç dosyaları (CSV/NPZ) ve 5 şekil.

**Bağımsız olarak yeniden hesaplananlar (kayıtlı değerlerle birebir aynı çıktı):**
- 05: U = 2114, p = 0,3946, r = −0,0848, HL = −0,0301. OLS-HC3 grup katsayısı +0,0054 [−0,068; 0,079], p = 0,886.
- 06: ortalama olasılıkla AUC 0,5380. Bootstrap %95 GA 0,4398–0,6333 (aynı seed ile).
- 04-A kimlik eşleşmesi: 100 deneğin 100'ü kendisiyle eşleşiyor.
  - Kendisiyle korelasyon r = 0,72–0,98 (medyan 0,915).
  - İkinci en iyi eşleşmeye göre en küçük fark 0,15.
  - Bilinmeyen 12 ID'nin en iyi eşleşmesi r = 0,25–0,66 aralığında, ve eşleştikleri denekler tutarsız.
- Kayıt ayı dağılımı (01 audit dosyasından).

**Doğrulanamayanlar:**
- Öznitelik çıkarımının ham EEG'den yeniden koşulması. Ham veri burada yok; bu adımda yalnızca kod okundu.
- Golden Distance'ın orijinal referans koddan bağımsız doğrulaması. Yalnızca iç tutarlılık denetimi yapıldı (`nav_closed`).
- Analiz günlüğündeki zaman damgaları. PyCharm'daki CLAUDE.md ve git log yüklenmedi. Projedeki `claude/CLAUDE.md` 2026-10-01 tarihli eski kopyadır.

## 2. Kod: hesaplama hatası bulunmadı
- Denek bazlı bölme hem dış hem iç döngüde StratifiedGroupKFold ile yapılıyor. `groups` parametresi iç döngüye de aktarılıyor; aktarılmasaydı kod hata verirdi.
- Ölçekleme, öznitelik seçimi, imputasyon ve kalıntılama CV'nin içinde yapılıyor.
- Label/Subject sızıntısı ve epok sırası (COCO) için assert kontrolleri var.
- Permütasyonlar denek düzeyinde; p = (k+1)/(N+1). 200 permütasyonla ulaşılabilecek en küçük p değeri 1/201 = 0,005.
- 04-B'deki naif hücreler kasıtlı olarak, planda tanımlandığı gibi sızıntılı kuruldu.

## 3. Sayılar: raporlar, CSV'ler ve şekiller tutarlı
Analiz 03, 04-B, GD eki, 05, 06, 07 ve 07a–c'de raporlanan her değer CSV ile eşleşiyor. Şekillerdeki değerler de CSV ile eşleşiyor.

## 4. Düzeltilmesi gereken metin ve şekil sorunları (yeni analiz gerektirmez)

**D1. 04-B raporu, bölüm 5.**
- 5.2'deki "mutlak genlik / kayıt koşulu" açıklaması 07 ile çürütüldü: göreli güç de AUC 0,734 veriyor.
- 5.4'teki "GD hesaplanmadı" ifadesi, aynı raporun 4b bölümüyle çelişiyor.

**D2. 06 raporu ve iskeletin 3.4 bölümü.** Nokta tahmini ile güven aralığı farklı yöntemlerden geliyor.
- Doğru ifade: **"AUC 0,54 (%95 GA 0,44–0,63; tekrar ortalaması 0,51)"**.
- "Üst sınır hafif iyimser" cümlesi yanlış. İki etki ters yönde çalışıyor:
  - Olasılıkların ortalaması alındığında AUC ve dolayısıyla U yükselir. Bu, dışlama iddiasını zayıflatır (tutucu yön).
  - Yeniden fit oynaklığı GA'ya dahil edilmediği için GA daralır (tutucu olmayan yön).
  - Net yön belirsiz; ifade "yaklaşık" olmalı.

**D3. "Frontal kanallar çıkarıldı" ifadesi yanlış; çıkarılan C bloğu (32 kanal).**
- C bloğu şunları içeriyor: Fp1/Fpz/Fp2, AF7/AF3/AFz/AF4/AF8, F1/Fz/F2/F4/F6/F8, FC1/FCz/FC2.
- Analizde kalan frontal kanallar: F3/F5/F7, FC3/FC5, FT7 (D bloğu) ve FC4/FC6, FT8 (B bloğu).
- Şekil 2b'de:
  - "frontal delta" yerine "C bloğu delta",
  - "posterior alfa" yerine "A bloğu alfa" yazılmalı. A bloğu, Cz'den oksipitale uzanan orta hat ile parieto-oksipital bölgeyi kapsıyor.
  - Panelde örneklem: cg 55, sg 45, sg2 24.

**D4. sg2'nin kayıt dönemi.** "Eşzamanlı" ya da "aynı dönem" ifadeleri yanlış.
- Aylara göre kayıt sayıları:

| Grup | Kayıt ayları (kayıt sayısı) |
|---|---|
| sg2 | Ara 2021 (4), Nis 2022 (10), May 2022 (7), Haz 2022 (4) |
| cg | Şub–Mar 2022 (17), May 2022 (3), Haz 2022 (6), Tem–Eyl 2022 (40) |
| sg | Tem–Eyl 2021 |

- Aynı ayda kaydedilen tek dönem Mayıs–Haziran 2022 (sg2 11, cg 9). 07 örnekleminde bu dönemde yalnızca Haziran 2022'de 5 cg var.
- sg ile cg arasında hiç örtüşme yok.
- Doğru ifade: "sg2 kontrollere zamanca daha yakın ve kısmen örtüşüyor."

**D5. Naif pipeline veri sahiplerine atfedilmemeli.** Veri sahipleri bir sınıflandırma yayımlamadı. Naif pipeline, literatürde sık görülen hatayı temsil etmek üzere bu çalışmada kuruldu.

**D6. Şekil 1a.**
- Başlıktaki "Accuracy" ifadesi yanlış; çizilen metrik ROC-AUC.
- "Leaky" gölgesi yalnızca N1–N2'yi kapsıyor. Oysa N3'te de öznitelik seçimi sızıntısı var.
- Betikte tanımlanan `sub` alt etiketleri şekle hiç çizilmemiş.

**D7. Şekil 2a.**
- 0,60–0,65 kural boşluğu bandı yalnızca 07a göz kapalı sütunu için geçerli; bütün panele yayılmamalı.
- En küçük p değerleri "p ≤ 0,005" olarak yazılmalı.
- Başlık 07d sonucuna göre güncellenmeli.

**D8. Şekil 5a.** Doğrusal ok zinciri 135'ten 136'ya artış varmış gibi okunuyor. Bunun yerine 140'tan dallanan paralel kutular çizilmeli:
- 135 (uzun blok; 02, 03, 06)
- 136 (epoklar; 05)
- 112 / 100 (Excel; 04-B)
- 100 + 24 sg2 (07, 07a–e)

**D9.** Keşifsel analizlerin p değerleri çoklu karşılaştırma düzeltmesi yapılmadan verildi. Bu, yöntem bölümünde ve tablolarda belirtilmeli.

**D10. GD ifadesi.**
- Yanlış: "AUC göstermez, GD gösterir".
- Doğru: "Duyarlılık ve özgüllük bunu gösterir; GD bunları tek bir sayıda özetler."

**D11. Tablo 1 ve Tablo S-n.**
- Tablo 1: sg, sg2, cg ve suçlu toplamı ayrı sütunlarda.
- Tablo S-n: her analizin örneklemi.
- Testler önceden ve tek seçilmeli: sürekli ya da sıralı değişkenler için Mann–Whitney, ikili değişkenler için Fisher.
- Yaş için iki farklı p değeri var: Mann–Whitney 0,054, Welch 0,041. Yalnızca Mann–Whitney raporlanmalı.

**D12. Kayıt saati Tablo 1'e eklenmeli.**
- Ortalama kayıt saatleri benzer: yaklaşık 11:30–11:55.
- Ama 14:00'ten sonra yapılan kayıtların oranı farklı: sg 14/49, sg2 7/25, cg 6/66.

## 5. Sohbet tarafının önceki ifadelerindeki düzeltmeler
- **K1.** "sg2 kontrollerle aynı dönemde kaydedildi" ifadesi abartılıydı. Doğru bilgi D4'te.
- **K2.** "Veri sahiplerinin yöntemiyle 0,9" ifadesi yanlıştı. 0,9, bu çalışmada kurulan naif pipeline'ın sonucu (bkz. D5).
- **K3.** "Frontal kanallar çıkarılınca AUC 0,58" ifadesi eksikti. Çıkarılan C bloğuydu (bkz. D3).
- **K4.** "06: AUC 0,51 (GA 0,44–0,63)" ifadesi farklı yöntemlerden gelen iki değeri karıştırıyordu (bkz. D2).
- **K5.** "03 frontal kanalları görmedi" ifadesi kesin değildi. 03 frontal kanalları tek tek görmedi, ama global ROI ortalamasında frontal kanallar vardı.
- **K6.** "Kayıt saati açıklamıyor" ifadesi fazla kesindi. Ortalamalar benzer, ama sg'de öğleden sonra yapılan kayıtların oranı daha yüksek (bkz. D12).

## 6. Tablo S2'ye eklenmesi gereken adımlar (PyCharm tarafının bilmediği)

| Zaman (yaklaşık) | Olay |
|---|---|
| 2026-10-01 ~19:50 | 02 v2'nin grup bazlı QC betimselleri görüldükten sonra iki karar verildi: H1 sonuçları tam kesitle yan yana raporlanacak, teta/alfa eğimi kovaryat olacak. Kayıt saati grup bazında betimsel olarak kontrol edildi. |
| 2026-10-01 ~19:50 | Atipik spektrum kuralı benimsendiğinde, etkilenen deneklerin sg2'de olduğu ve hem esrar hem kokain kullandıkları biliniyordu. Kural bu denekleri birincil analizde tuttu. |
| 2026-10-01 ~20:35 | Adım 0 demografisi önce sohbette hesaplandı, ardından betikle yeniden üretildi. |
| 2026-10-01 ~22:20 | **03'ün sonuçlarından sonra ve 05 birincil test ilan edilmeden önce, 14 önceden belirlenmiş öznitelik için 42 tek değişkenli Mann–Whitney testi yapıldı** (sg–cg, sg2–cg, sg–sg2; düzeltmesiz; en küçük p ≈ 0,025). Testler göreli alfayı da içeriyordu. Bu testler hiçbir öznitelik seçimine girdi olmadı. 05'in birincil test seçimi aynı adımda yapıldı. |
| 2026-10-02 ~07:44 | 07a–c'nin tasarımı, 07'nin betimsel öznitelik haritasından türetildi (en güçlü 50 öznitelik: C bloğu delta ve alfa). 07a–c, kendi sonuçları görülmeden tanımlandı. |
| 2026-10-02 | 07a–c'nin eşikleri sohbet tarafında önerildi. 0,60–0,65 boşluğu bu öneriden kaynaklanıyor. |

## 7. Makaledeki iddialar için eksik iki analiz

Her iki analizde karar kuralı **tek bir ölçüte** dayanıyor (permütasyon p < 0,05). Böylece eşik boşluğu oluşmuyor.

**07d. En güçlü modellerin sg2'ye transferi.**
- Şu anki "genellenmiyor" iddiası yalnızca göz kapalı modele (AUC 0,645) dayanıyor. En güçlü üç model test edilmedi: A tüm epoklar 0,754, B tüm epoklar 0,734, B göz açık 0,709.
- Yöntem: 07c'deki transfer yöntemi aynen uygulanacak. sg2 için eğitimde kullanılan epokların aynısı alınacak.
- Karar: p < 0,05 → "transfer ediyor"; aksi halde "transfer etmiyor".
- Düzeltme yapılmayacak. Bu seçim, "genellenmiyor" iddiası açısından tutucu.
- **Herhangi bir model transfer ederse başlıktaki iddia daraltılır.**

**07e. Kayıt kesitinin etkisinin ayrıştırılması.**
- Amaç: 06 (0,54) ile 07a göz kapalı (0,645) arasındaki farkın kaynağını bulmak.
- Yöntem:
  - Aynı 100 denek kullanılacak.
  - 465 s'lik uzun göz kapalı blok, 4 ardışık ve örtüşmesiz 116,25 s'lik parçaya bölünecek.
  - Öznitelik seti B (göreli bant gücü) olacak.
  - 07 pipeline'ı aynen uygulanacak; kanal dışlaması yapılmayacak.
- Karar:
  - p < 0,05 → Kanal düzeyindeki ayrışma uzun blokta da var. Bu durumda 06'daki null sonuç ROI ve model seçimine özgüdür, ve bu açıkça yazılmalı.
  - p ≥ 0,05 → Ayrışma, oturum başındaki kapalı/açık epoklarla sınırlı.

## 8. Tartışma için notlar (yeni analiz değil; literatürle doğrulanacak)
- **Yaş:** sg kontrollerden daha yaşlı (yaş ortalaması 17,2'ye karşı 16,3). Ergenlikte yaş arttıkça göreli delta azalır, alfa artar. Gözlenen fark bunun tersi (sg'de daha fazla delta, daha az alfa). Dolayısıyla yaş farkı bu ayrışmayı açıklamaz; aksine maskeler.
- **Madde kullanımı:** sg2'de alkol ve kokain kullanımı sg'den daha yüksek, ama sg2'de delta artışı yok. Bu durum, delta imzasının madde kullanımından kaynaklandığı açıklamasını zayıflatıyor. Alfa düşüşü ise sg2'de daha güçlü. Bu gözlem betimsel, test edilmedi.
- **Model farkı:** 07'de SVM kullanılmasının nedeni, 04-B'nin P pipeline'ıyla karşılaştırılabilirlik. 03 ve 06'da ise önceden belirlenmiş lojistik regresyon kullanıldı. Bu fark yöntem bölümünde açıklanmalı.
