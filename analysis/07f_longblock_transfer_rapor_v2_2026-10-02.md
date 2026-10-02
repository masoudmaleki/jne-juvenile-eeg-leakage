# 07f (KEŞİFSEL): uzun blok modelinin sg2'ye transferi, sonuç raporu v2 (2026-10-02)

**v2 düzeltmeleri** (DENETIM_RAPORU_3, F2; sayılar değişmedi, 07g GA'ları eklendi):
- Yorum 1 ve 3 yeniden yazıldı. v1'deki "tespit sınırı 0,60–0,65" ifadesi anlamlılık eşiğiyle dışlanabilen etkiyi karıştırıyordu. v1'deki "kaynak ayrışma ile transfer arasında açık bir fark var" ifadesi kaldırıldı, çünkü bu fark hiç test edilmedi.
- Commit içerikleri doğrulandı (`git_show_07f.txt`): 6a4439c yalnız CLAUDE.md'ye 9 satır ekliyor; 11790e8 yalnız 07f betiği ve çıktılarını (7 dosya) içeriyor.

**Tanım:** CLAUDE.md "07f"; kaynak DENETIM_RAPORU_2 bölüm 4.
**Zaman kaydı (git):**
- Tanım: `6a4439c` (10:11:48). Bu commit analiz çalıştırılmadan önce atıldı ve yalnızca tanımı içeriyor.
- Analiz: 10:12'de başladı (ilerleme kaydı).
- Sonuç: `11790e8`; yalnızca 07f'nin betiği ve çıktılarını içeriyor.

**Betik:** `07f_longblock_transfer_v1_2026-10-02.py`. 07de (`longblock_B`, `job_tr_real`, `job_tr_null`, `summ`) ve 07abc (`transfer`) fonksiyonları birebir kullanıldı. Checkpoint var. Toplam süre yaklaşık 8 dakika.
**Okunanlar:** 07e'nin uzun blok öznitelikleri (sg 45 + cg 55); sg2'nin 24 desc-preprocessed dosyası (uzun blok). Ham veriye yazılmadı.

## Yöntem
- **Model:** 07e ile aynı.
  - Öznitelikler: B seti (göreli bant gücü, 128 kanal × 4 bant).
  - Veri: uzun göz kapalı blok, 4 × 116,25 s; kanal dışlaması yok.
  - Pipeline: P (SVM; k ve C iç döngüde seçiliyor).
- **Transfer:** 07c'nin kat içi yöntemi. Her dış katta aynı model hem held-out cg'yi hem 24 sg2'yi skorluyor; o katın AUC'si hesaplanıyor; 5 kat × 20 tekrar = 100 katın ortalaması alınıyor.
- **Sıfır dağılımı:** eğitimdeki sg/cg etiketleri denek düzeyinde karıştırılıyor; 200 permütasyon × 5 tekrar.
- **sg2:** 24 denek. sub-1084sg2'nin uzun bloğu olmadığı için dahil değil.
- **Karar:** tek ölçüt, p < 0,05. Çoklu karşılaştırma düzeltmesi yok.

## Sonuç
| | Değer |
|---|---|
| Kaynak model (07e), sg vs cg | AUC 0,746 (p ≤ 0,005) |
| **Transfer AUC, held-out cg vs sg2** (100 kat; tekrarlar 2,5–97,5) | **0,582** (0,526–0,631) |
| Sıfır dağılımı ortalaması [%95] | 0,504 [0,385–0,621] |
| **p (200 permütasyon)** | **0,104** |
| sg2'nin "suçlu" sınıflanma oranı (eşik 0) | 0,30. Bu oran tek başına yorumlanamaz (E1). |

**Önceden belirlenen kurala göre:** p ≥ 0,05 → **transfer kanıtı yok.** "Transfer kanıtı yok" iddiası beş modelin hepsi için geçerli kalıyor:

| Model | Kaynak AUC (sg vs cg) | Transfer AUC | p |
|---|---|---|---|
| 07c, B göz kapalı | 0,645 | 0,569 | 0,264 |
| 07d, A tüm epoklar | 0,754 | 0,549 | 0,224 |
| 07d, B tüm epoklar | 0,734 | 0,589 | 0,194 |
| 07d, B göz açık | 0,709 | 0,553 | 0,289 |
| **07f, B uzun blok** | **0,746** | **0,582** | **0,104** |

## Yorum ve sınırlar (v2)
- **Doğru ifade "no evidence of transfer".** "Transfer etmiyor" değil.
- **Üç ayrı büyüklük karıştırılmamalı (F2):**
  - **Anlamlılık eşiği:** Gözlenen transfer AUC'sinin anlamlı olması için sıfır dağılımının tek yönlü %95 persentilini geçmesi gerekirdi: 07f'de 0,601 (beş modelde 0,586–0,638).
  - **%80 güç:** DENETIM_RAPORU_3'teki benzetime göre gerçek transfer AUC'sinin yaklaşık 0,66 olması gerekir (bu çalışmada yeniden hesaplanmadı).
  - **Gözlenen değerle uyumlu aralık (07g):** 07f transfer AUC'si **0,582 (%95 GA 0,463–0,704)**. AUC > 0,70 yaklaşık olarak dışlanır.
- **Veri "transfer yok" ile "orta düzeyde transfer" arasındaki her şeyle uyumlu.** Beş modelin GA üst sınırları 0,660–0,704 (07g).
- **Beş transfer AUC'sinin beşi de 0,5'in üzerinde (0,55–0,59), ama hiçbiri anlamlı değil.** Bunlar bağımsız testler değil (aynı denekler, benzer öznitelikler), dolayısıyla birleştirilerek yorumlanamaz.
- **~~Kaynak ayrışma ile transfer arasında açık bir fark var.~~ [v2, F2: kaldırıldı.]** Kaynak AUC (sg vs cg) ile transfer AUC'si (cg vs sg2) arasındaki fark test edilmedi; iki AUC farklı denek kümelerinde ve farklı yöntemlerle (iç içe CV ile kat içi transfer) hesaplandı. Bu yüzden "imza sg'ye özgü" sonucu çıkarılamaz.
- **GA'nın sınırı:** 07g GA'ları yalnız denek örneklemesini içerir; model eğitimindeki (seed, katlama) oynaklık dahil değil.

## Çıktılar
`07f_longblock_transfer_v1_2026-10-02_{results,transfer_folds}.csv`, `_ckpt_tr_real.jsonl`, `_ckpt_tr_null.jsonl`, `_progress.log`, `_sg2_longblock_features.npz`
