# 07d–e (KEŞİFSEL): sonuç raporu v2 (2026-10-02)

**v2 düzeltmeleri** (DENETIM_RAPORU_2; sayılar değişmedi):
- **E1:** sg2'nin "suçlu" sınıflanma oranının yorumu düzeltildi. Oran, cg yanlış pozitif oranı ve sg duyarlılığıyla birlikte veriliyor.
- **E2:** ROI ile kanal düzeyi karşılaştırması aynı gruplar üzerinden yapılıyor: 03(b) sg vs cg ile 07e sg vs cg.
- **Ek:** Uzun blok modelinin transferi 07f'de test edildi: `07f_longblock_transfer_rapor_v1_2026-10-02.md`.

**Tanım:** CLAUDE.md "07d–e". Sonuç görülmeden, DENETIM_RAPORU bölüm 7'ye göre yazıldı. Plandan sapma yok.
**Karar ölçütü:** tek ölçüt, permütasyon p < 0,05. Eşik boşluğu yok. Çoklu karşılaştırma düzeltmesi yapılmadı (D9).
**Betik:** `07de_transfer_longblock_v1_2026-10-02.py`.
- 07, 07abc (`transfer`) ve 02 v2 (`load_block`) fonksiyonları birebir kullanıldı.
- Checkpoint ve ilerleme kaydı içeriyor. Toplam süre yaklaşık 29 dakika.
**Okunanlar:**
- 07 öznitelikleri.
- sg2'nin 25 acq-epochs dosyası (A ve B öznitelikleri hesaplandı).
- 100 deneğin desc-preprocessed dosyası (uzun blok).
- Ham veriye yazılmadı.

## 07d: en güçlü modellerin sg2'ye transferi (07c yöntemi, kat içi; held-out cg ile sg2 = 24)
| Model (eğitim: sg 45 + cg 55) | Kaynak AUC (sg vs cg) | Transfer AUC (100 kat ortalaması; tekrarlar 2,5–97,5) | Sıfır dağılımı ortalaması [%95] | p | Karar | sg2'nin "suçlu" sınıflanma oranı |
|---|---|---|---|---|---|---|
| A log10 mutlak, tüm epoklar | 0,754 | **0,549** (0,520–0,594) | 0,503 [0,405–0,598] | **0,224** | transfer etmiyor | 0,19 |
| B göreli, tüm epoklar | 0,734 | **0,589** (0,552–0,637) | 0,510 [0,369–0,646] | **0,194** | transfer etmiyor | 0,33 |
| B göreli, göz açık | 0,709 | **0,553** (0,491–0,592) | 0,508 [0,391–0,636] | **0,289** | transfer etmiyor | 0,35 |
| (07c, karşılaştırma için) B göreli, göz kapalı | 0,645 | 0,569 | 0,508 | 0,264 | – | 0,44 |

sg2 = 25 (1084sg2 dahil) ile transfer AUC'leri: 0,549 / 0,602 / 0,563. Sonuç değişmiyor.

**Başlık kuralına göre (önceden belirlenmiş):** hiçbir model transfer etmiyor, dolayısıyla **"genellenmiyor" iddiası korunuyor.**

**Sınırlar:**
- **Bu test yalnızca belirli bir büyüklüğün üstündeki transferi yakalayabilir.** Her katta yaklaşık 11 held-out cg ile 24 sg2 karşılaştırılıyor. Sıfır dağılımının %97,5 sınırı 0,60–0,65 arasında. Yani AUC ≈ 0,60–0,65'in altındaki transfer etkileri bu tasarımla tespit edilemiyor.
- **Gözlenen değerler 0,5'in biraz üstünde ama anlamlı değil** (0,55–0,59). Bu yüzden doğru ifade "sg2'ye genellendiğine dair kanıt yok", "kesin olarak genellenmiyor" değil.
- **(E1) sg2'nin "suçlu" sınıflanma oranı tek başına yorumlanamaz.** Bu oran karar eşiğine bağlı ve sınıf dengesizliğinden etkileniyor. Modeller sg'nin de yaklaşık yarısını kontrol olarak sınıflıyor. Aynı modellerin ölçümleri yan yana (cg yanlış pozitif oranı ve sg duyarlılığı sg vs cg iç içe CV'sinden; sg2 oranı transfer katlarından):

  | Model | cg yanlış pozitif oranı | sg2 "suçlu" oranı | sg duyarlılığı |
  |---|---|---|---|
  | A, tüm epoklar | 0,24 | 0,19 | 0,57 |
  | B, tüm epoklar | 0,19 | 0,33 | 0,49 |
  | B, göz açık | 0,28 | 0,35 | 0,58 |
  | B, göz kapalı (07c) | 0,27 | 0,44 | 0,47 |

  - Göz kapalı modelde sg2'nin "suçlu" oranı, sg duyarlılığına çok yakın.
  - Bu yüzden oranlardan "imza sg2'de görülmüyor" sonucu çıkarılamaz.
  - Geçerli ölçüt, eşikten bağımsız transfer AUC'si. Ondan çıkan sonuç: **transfer kanıtı yok.**

## 07e: kayıt kesitinin etkisi (uzun göz kapalı blok, 4 × 116,25 s, B seti, kanal dışlaması yok)
| | Değer |
|---|---|
| Denek AUC (20 tekrar; 2,5–97,5) | **0,746** (0,647–0,801) |
| Sıfır dağılımı ortalaması [%95] | 0,478 [0,377–0,594] |
| p (200 permütasyon) | **≤ 0,005** |
| Dengeli doğruluk / GD | 0,658 / 0,596 (Sen 0,51, Spe 0,81) |

**Önceden belirlenen kurala göre** p < 0,05: **kanal düzeyindeki ayrışma uzun göz kapalı blokta da var.**
- **(E2) Kuralın ifadesinde bir hata vardı.** Kural "06'daki null sonuç" diyordu. Ama 06 suçlu grubu olarak sg + sg2'yi kullanıyor, 07e ise yalnızca sg'yi.
  - Aynı grupları karşılaştıran doğru eşleştirme: **03(b) sg vs cg, ROI düzeyi + lojistik regresyon, AUC 0,53 (n = 111)** ile **07e sg vs cg, kanal düzeyi + SVM, AUC 0,746 (n = 100)**.
  - 06'nın 0,54'ü düşük kalıyor, çünkü suçlu grubuna imzayı taşıdığına dair kanıt bulunmayan sg2 de dahil (07c–d).
  - Sonuç değişmiyor: ROI düzeyindeki null sonuç, ROI ve model seçimine özgü. Bu makalede açıkça yazılmalı.
- 03(b) ile 07e arasındaki fark kayıt kesitine bağlanamaz, çünkü ikisi de aynı uzun bloğu kullanıyor. Fark şu ikisinden birine ya da ikisine birden bağlı:
  - öznitelik çözünürlüğü (kanal düzeyi ile ROI ortalaması),
  - model (seçimli RBF SVM ile L2 lojistik regresyon).

  Bu iki etki birbirinden ayrıştırılmadı.
- Ayrıca 07e'de kanal dışlaması yok; 03 ve 06'da 02 v3 kanal kuralı uygulanmıştı. Örneklemler de farklı: 03'te 111 denek, 07e'de 100. Bunlar da fark kaynağı olabilir.

## Birlikte yorum (keşifsel)
- **sg ile cg ayrışması tutarlı.** Kanal düzeyinde ayrışma bütün kesitlerde görülüyor: göz açık (0,709), göz kapalı epoklar (0,645) ve uzun blok (0,746). Bu, ayrışmanın yalnızca oturum başındaki epoklara ya da oküler artığa bağlı olmadığını gösteriyor. Uzun blok tamamen göz kapalı; buna karşın C bloğu dahil.
- **Bu imzanın sg2'ye taşındığına dair kanıt yok (E4).** Dört transfer testinin dördü de anlamlı değil; tespit edilebilirlik sınırı yaklaşık 0,60–0,65. Uzun blok modeli için 07f'ye bakın.
- **Bu tablo, imzanın "suçlu olma" ile değil, sg alt grubuna özgü özelliklerle ilişkili olmasıyla uyumlu.** Bu özellikler:
  - kayıt dönemi (2021 yazı, kontrollerle hiç örtüşme yok),
  - şiddet suçu oranı (%86'ya karşı %24),
  - 14:00'ten sonra yapılan kayıtların oranı (sg %29, cg %9),
  - ve başka bilinmeyen farklar olabilir.

  Hangisinin belirleyici olduğu bu veriyle ayırt edilemez.

## Çıktılar
`07de_transfer_longblock_v1_2026-10-02_{results,transfer_folds}.csv`, `_ckpt_*.jsonl`, `_progress.log`, `_sg2_features.npz`, `_longblock_features.npz`
