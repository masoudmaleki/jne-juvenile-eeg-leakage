# Denetim raporu 2 (2026-10-02): 07d–e ve v2 belgeleri

Denetimi yapan: sohbet tarafındaki Claude. Bu rapor, birinci denetim raporundan sonra üretilen dosyaları kapsar.

## 1. Kapsam ve doğrulananlar

**Okunanlar:**
- Güncel CLAUDE.md ve git_log.
- 07de: betik, rapor, ilerleme kaydı, sonuç ve transfer-katı CSV'leri.
- v2 raporları: 04b, 06, 07, 07abc.
- İskelet v3, şekil başlıkları v2, Tablo 1, Tablo S-n ve bunları üreten 09 betiği.
- 08 v2 betiği (Şekil 2 bölümü) ve v2 şekillerinin beşi.

**Kod (07de):** Hata yok.
- 07, 07abc ve 02 v2 fonksiyonları değiştirilmeden kullanılmış.
- Uzun blok 4 × 14.880 örneğe bölünmüş (= 465 s).
- Öznitelik sütunlarının düzeni 07 ile aynı.
- Çapraz doğrulama denek bazlı gruplanmış; permütasyonlar denek düzeyinde yapılmış.

**Sayılar:**
- 07de raporundaki değerler CSV ve şekillerle birebir aynı.
- Tablo 1'deki tüm oranlar ve p değerleri `participants.tsv`'den bağımsız olarak yeniden hesaplandı; birebir aynı çıktı.

**Şekiller:** D6–D8 düzeltmeleri uygulanmış.

**Doğrulanamayanlar:**
- Ham EEG'den öznitelik çıkarımının yeniden çalıştırılması (birinci raporda da aynı durum vardı).
- 08 v2 betiğinin tamamı satır satır okunmadı. Şekil çıktıları ise CSV'lerle tek tek karşılaştırıldı.

## 2. Düzeltilmesi gerekenler (yeni analiz gerektirmez)

**E1. 07de raporu, sg2'nin "suçlu" sınıflanma oranının yorumu yanlış.**
Raporda "modeller sg2'nin çoğunu kontrol olarak sınıflıyor; imza sg2'de görülmüyor" deniyor. Bu oran eşiğe bağlı ve sınıf dengesizliğinden etkileniyor. Modeller sg'nin de yaklaşık yarısını kontrol olarak sınıflıyor. Aynı modellerin ölçümleri yan yana:

| Model | cg yanlış pozitif oranı | sg2 "suçlu" oranı | sg duyarlılığı |
|---|---|---|---|
| A, tüm epoklar | 0,24 | 0,19 | 0,57 |
| B, tüm epoklar | 0,19 | 0,33 | 0,49 |
| B, göz açık | 0,28 | 0,35 | 0,58 |
| B, göz kapalı (07c) | 0,27 | 0,44 | 0,47 |

- Göz kapalı modelde sg2'nin "suçlu" oranı, sg'nin duyarlılığına çok yakın.
- Bu yüzden oranlardan "imza sg2'de görülmüyor" sonucu çıkarılamaz. Geçerli ölçüt, eşikten bağımsız transfer AUC'si ve ondan çıkan sonuç "transfer kanıtı yok".
- Ya oranlar bu üç sütunla birlikte verilmeli ya da metinden çıkarılmalı.

**E2. ROI ile kanal düzeyi karşılaştırması farklı gruplar üzerinden yapılıyor.** Bu, benim 07e kuralımdaki ifade hatasından kaynaklanıyor.
- Kural "06'daki null sonuç" diyordu. Oysa 06 suçlu grubu olarak sg + sg2'yi kullanıyor, 07e ise yalnızca sg'yi.
- Aynı grupları karşılaştıran doğru eşleştirme: **03(b) sg vs cg, ROI düzeyi + lojistik regresyon, AUC 0,53 (n = 111)** ile **07e sg vs cg, kanal düzeyi + SVM, AUC 0,746 (n = 100)**.
- 06'daki 0,54 düşük kalıyor, çünkü suçlu grubuna imzayı taşımadığı görülen sg2 de dahil (07c–d).
- Sonuç değişmiyor: ROI düzeyindeki null sonuç, ROI ve model seçimine özgü.
- Düzeltilecek yerler: CLAUDE.md (07e kuralına not), 07de raporu, 06 v2 raporu, iskelet v3 (Çerçeve (i), Tartışma, Sınırlılıklar), Şekil 4 başlığı.

**E3. İskelet v3, Çerçeve.** "sg vs cg 0,71–0,75 (göz açık, göz kapalı, uzun blok)" ifadesi yanlış. Göz kapalı epoklarda AUC 0,645. Doğrusu:
- 0,65–0,75 aralığı: kapalı 0,645; açık 0,709; tüm epoklar 0,734 / 0,754; uzun blok 0,746.

**E4. İddianın gücü.** "non-generalizable", "does not transfer" ve "no model transfers" ifadeleri, testin gösterdiğinden daha güçlü. Test yalnızca "no evidence of transfer" sonucunu destekliyor.
- Başlık önerisi: *High accuracy without demonstrated generalization: data leakage, recording confounds and subgroup-specific EEG differences in juvenile offenders.*
- Şekil 2 başlığı: "...but no model shows significant transfer to sg2".

**E5. 07e'den sonra eskiyen cümleler.**
- **07abc v2:** "yeni analiz eklenmeyecek" cümlesi geçersiz, çünkü denetim sonrasında 07d–e eklendi. Bu bir not ile belirtilmeli.
- **07abc v2:** "kademeli tablo → oküler artık" yorumu zayıfladı:
  - Uzun ve tamamen göz kapalı blok 0,746 veriyor.
  - Göz kapalı epokların 0,645 vermesinin bir nedeni veri miktarı olabilir: o analizde denek başına 2 × 50 s veri var, 07e'de 4 × 116 s.
  - Bu yorum makalede ana açıklama olarak sunulmamalı.
- **07 v2:** Şunlara not eklenmeli: 05, 06 ve GD eki sonradan çalıştırıldı; "03 ile çelişki" 07e ile kısmen açıklandı (fark kayıt kesitinden değil, temsil ve modelden geliyor).
- **06 v2, Yorum bölümü:** 07e'ye göre güncellenmeli (bkz. E2).

**E6. Şekil 2.**
- (a) 07b sütununda etiket "p = 0.050", işaret ise dolu (p < 0,05). Etiket "p = 0.0498" olarak yazılmalı.
- "long block" yerine "long eyes-closed block".
- Başlıktaki C bloğu tanımına sağ frontal kanallar da eklenmeli: F4/F6/F8, AF8, FC2.

**E7. Tartışma.** sg'ye özgü imza için aday açıklamalar listesine iki madde eklenmeli:
- Uyanıklık farkı: uzun blokta teta/alfa eğimi kontrollerde daha hızlı yükseliyor.
- Kayıt saati: 14:00'ten sonra yapılan kayıtların oranı sg'de %29, cg'de %9.

**E8. CLAUDE.md'deki eskimiş satırlar.** Silinmemeli, tarihli not eklenmeli:
- "İLK DOĞRULANACAK ŞEY BU" ve "Şüpheli denekler (... doğrulanacak)": ikisi de doğrulandı.
- "Makale iskeleti: v1": güncel sürüm v3 (ya da v4).
- "06 SONUÇ: AUC 0,511 ... GA 0,44–0,63": D2'ye göre doğru ifade "0,54 [0,44–0,63]; tekrar ortalaması 0,51".
- "(b) sg2 ile cg (zamanca örtüşen kayıtlar)": D4'e göre "kısmen örtüşen".
- "Yüksek doğruluk çıkarsa batch etkisinin kanıtıdır": Adım 0 ile geçersizleşti.
- "Duyarlılık: ilk 60 s C bloğu (n = 139)": yapılmadı.

## 3. Tablo S2'ye eklenecekler

| Konu | Eklenecek bilgi |
|---|---|
| Planlanıp yapılmayan analizler | (1) Madde kullanmayan, eşleştirilmiş alt örneklem ve regresyonla confound çıkarma. (2) Grup içi analizler: tekrar suç, çete, şiddet. (3) n = 139 ile ilk 60 s C bloğu duyarlılık analizi. Neden: 2026-10-01'de 03'ten sonra yapılan çerçeve değişikliği ve "yeni analiz eklenmez" ilkesi. Seçici raporlama eleştirisine karşı bu liste açıkça yazılmalı. |
| 07d–e zaman damgası | Tanım ve sonuçlar aynı git commit'inde (cbedc41). Tanımın sonuçlardan önce yazıldığı yalnızca CLAUDE.md ve ilerleme kaydıyla (başlangıç 09:12:41) destekleniyor. |
| 07e kuralının ifade hatası | Kural sohbet tarafında yazıldı ve "06" diyordu; doğrusu 03(b) sg–cg (bkz. E2). Sonuç değişmiyor. |
| 07f | Tanımı (bölüm 4) ve sonucu. |

## 4. Eksik bir analiz: 07f (makaledeki iddia için gerekli)

**Neden gerekli:**
- 07d, en güçlü epok modellerinin sg2'ye transferini test etti.
- 07e'den sonra uzun blok modeli (0,746) en güçlü modellerden biri haline geldi, ama transferi test edilmedi.
- "Hiçbir modelde transfer kanıtı yok" iddiası bu modeli kapsamıyor.

**Tanım:**
- Model: 07e modeli (B seti, uzun blok, 4 × 116,25 s, sg 45 + cg 55 ile eğitilmiş).
- Test kümesi: sg2'nin uzun bloğu, 24 denek. sub-1084sg2'nin uzun bloğu olmadığı için dahil edilmiyor.
- 07c'nin kat içi transfer yöntemi aynen uygulanacak: 20 tekrar, 200 permütasyon × 5 tekrar.

**Karar (tek ölçüt):**
- p < 0,05 → "transfer ediyor"; makaledeki iddia daraltılır.
- Aksi halde iddia beş modelin hepsi için geçerli kalır.
- Çoklu karşılaştırma düzeltmesi yapılmaz; bu tercih "transfer kanıtı yok" iddiası açısından tutucu.

**Zaman kaydı:** Tanım CLAUDE.md'ye yazılacak ve analiz çalıştırılmadan önce **ayrı bir git commit'i** atılacak.

## 5. İsteğe bağlı
- **Önerilir: 07e için betimsel öznitelik haritası.** Kanal × bant düzeyinde sg vs cg etki büyüklüğü; test yapılmaz. Tartışmadaki "imza neye benziyor?" sorusu için gerekli.
- **Şimdi önerilmez: kontrol grubu içinde dönem karşılaştırması.** Şubat–Mart 2022 (n = 17) ile Temmuz–Eylül 2022 (n = 40). Güç düşük olduğu için null sonuç bilgi vermez. Hakem isterse yapılır.

## 6. Durum
- Analiz kodu ve sayılarda hata yok.
- 07f ve bölüm 2'deki metin düzeltmeleri tamamlanınca analiz aşaması kapanır.
