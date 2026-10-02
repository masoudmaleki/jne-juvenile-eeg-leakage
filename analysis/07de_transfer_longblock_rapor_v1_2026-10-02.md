# 07d–e (KEŞİFSEL): sonuç raporu (2026-10-02)

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
- **Modeller sg2'nin çoğunu kontrol olarak sınıflıyor.** "Suçlu" olarak sınıflanan sg2 oranı 0,19–0,35. sg ile cg arasında öğrenilen imza sg2'de görülmüyor.

## 07e: kayıt kesitinin etkisi (uzun göz kapalı blok, 4 × 116,25 s, B seti, kanal dışlaması yok)
| | Değer |
|---|---|
| Denek AUC (20 tekrar; 2,5–97,5) | **0,746** (0,647–0,801) |
| Sıfır dağılımı ortalaması [%95] | 0,478 [0,377–0,594] |
| p (200 permütasyon) | **≤ 0,005** |
| Dengeli doğruluk / GD | 0,658 / 0,596 (Sen 0,51, Spe 0,81) |

**Önceden belirlenen kurala göre** p < 0,05: **kanal düzeyindeki ayrışma uzun göz kapalı blokta da var.**
- 06'daki null sonuç (ROI düzeyinde 14 öznitelik, lojistik regresyon, AUC 0,54) **ROI ve model seçimine özgü**. Bu makalede açıkça yazılmalı.
- 06 ile 07e arasındaki fark artık kayıt kesitine bağlanamaz. İki analiz aynı bloğu kullanıyor; fark şu ikisinden birine ya da ikisine birden bağlı:
  - öznitelik çözünürlüğü (kanal düzeyi ile ROI ortalaması),
  - model (seçimli RBF SVM ile L2 lojistik regresyon).

  Bu iki etki birbirinden ayrıştırılmadı.
- Ayrıca 07e'de kanal dışlaması yok; 06'da 02 v3 kanal kuralı uygulanmıştı. Bu da bir fark kaynağı olabilir.

## Birlikte yorum (keşifsel)
- **sg ile cg ayrışması tutarlı.** Kanal düzeyinde ayrışma bütün kesitlerde görülüyor: göz açık (0,709), göz kapalı epoklar (0,645) ve uzun blok (0,746). Bu, ayrışmanın yalnızca oturum başındaki epoklara ya da oküler artığa bağlı olmadığını gösteriyor. Uzun blok tamamen göz kapalı; buna karşın C bloğu dahil.
- **Bu imza sg2'ye taşınmıyor.** Dört transfer testinin dördü de anlamlı değil; tespit edilebilirlik sınırı yaklaşık 0,60–0,65.
- **Bu tablo, imzanın "suçlu olma" ile değil, sg alt grubuna özgü özelliklerle ilişkili olmasıyla uyumlu.** Bu özellikler:
  - kayıt dönemi (2021 yazı, kontrollerle hiç örtüşme yok),
  - şiddet suçu oranı (%86'ya karşı %24),
  - 14:00'ten sonra yapılan kayıtların oranı (sg %29, cg %9),
  - ve başka bilinmeyen farklar olabilir.

  Hangisinin belirleyici olduğu bu veriyle ayırt edilemez.

## Çıktılar
`07de_transfer_longblock_v1_2026-10-02_{results,transfer_folds}.csv`, `_ckpt_*.jsonl`, `_progress.log`, `_sg2_features.npz`, `_longblock_features.npz`
