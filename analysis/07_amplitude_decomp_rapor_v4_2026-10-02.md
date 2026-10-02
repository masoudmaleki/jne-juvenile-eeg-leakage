# 07 Genlik ayrıştırması (KEŞİFSEL): sonuç raporu v4 (2026-10-02)

**v4 notu** (DENETIM_RAPORU_3, F4; sayılar değişmedi): Yorum 2'ye not eklendi. Uzun göz kapalı blok (07e) oküler açıklamayı dışlamıyor; ayrıntı aşağıda.
**v4 notu** (07g): A ve B için %95 GA'lar `07g_auc_ci_rapor_v1_2026-10-02.md` raporunda.

**v3 notları** (DENETIM_RAPORU_2, E5; sayılar değişmedi):
- Bu raporun "Hazır ama çalıştırılmayan" bölümündeki adımlar sonradan çalıştırıldı:
  - 05 ve 06 plana uygun çalıştırıldı (`05_..._rapor`, `06_..._rapor_v3`).
  - 04-B'nin GD eki çalıştırıldı; AUC'ler kayıtlı sonuçlarla aynı çıktı.
- "03 ile çelişki" (yorum, madde 3) 07e ile kısmen açıklandı. Kanal düzeyi SVM, 03 ile aynı uzun göz kapalı blokta da sg ile cg'yi ayırıyor (0,746). Dolayısıyla fark kayıt kesitinden değil, temsil ve modelden geliyor: kanal düzeyi ile ROI düzeyi, SVM ile lojistik regresyon. Kanal dışlaması ve örneklem farkı da rol oynayabilir.

**v2 düzeltmeleri** (DENETIM_RAPORU; sayılar değişmedi):
- **D3:** "Frontal" yerine C bloğu. C bloğu = Fp, AF, F1/Fz/F2/F4/F6/F8, FC1/FCz/FC2.
- **D7:** En küçük p değeri p ≤ 0,005 olarak yazıldı; bu değer 200 permütasyonla ulaşılabilecek en küçük değer.
- **D9:** p değerleri düzeltmesiz.
- **Sonraki adımlar:** "Karar için seçenekler" bölümündeki (ii) yolu 07a–e ile uygulandı. Sonuçlar için 07abc ve 07de raporlarına bakın.

**Tanım:** CLAUDE.md "07 Genlik ayrıştırması". Sonuç görülmeden önce yazıldı. Plandan sapma yok.
**Betik:** `07_amplitude_decomp_v1_2026-10-02.py`. Checkpoint ve ilerleme kaydı içeriyor. Toplam süre yaklaşık 16 dakika.
**Örneklem:** Kimliği doğrulanmış 100 denek: sg 45, cg 55. Yayımlanan acq-epochs dosyalarından 4 epok, toplam 400 satır, set başına 512 öznitelik.
**Okunanlar:** `04a_..._ids.csv`, 100 deneğin acq-epochs `.set` dosyası. Ham veriye yazılmadı.

## Sonuç: önceden belirlenen kural "DUR" diyor
| Set | Denek AUC (20 tekrar; 2,5–97,5) | Sıfır dağılımı ortalaması [%95] | p (200 perm.) | Dengeli doğruluk | GD ↓ | ACC / Sen / Spe / F1 |
|---|---|---|---|---|---|---|
| (A) log10 mutlak güç | **0,754** (0,708–0,801) | 0,479 [0,382–0,598] | **≤ 0,005** | 0,667 | 0,573 | 0,68 / 0,57 / 0,76 / 0,61 |
| (B) göreli güç (1–30 Hz) | **0,734** (0,674–0,794) | 0,479 [0,383–0,593] | **≤ 0,005** | 0,649 | 0,611 | 0,67 / 0,49 / 0,81 / 0,57 |

- p ≤ 0,005: 200 permütasyonla ulaşılabilecek en küçük değer (1/201): hiçbir permütasyon gerçek değere ulaşmadı.
- **Kural:** A ve B'nin ikisinde de ayrışma var. Bu, gerçek bir spektral fark ihtimali anlamına geliyor. Kural gereği burada durdum: 05, 06 ve 04-B'nin GD eki çalıştırılmadı.
- İç döngüde seçilen değerler: A'da çoğunlukla k = 500, C = 10. B'de dağınık; k = 10 ile 500 arasında değişiyor.

## Betimsel: hangi öznitelikler ayrıştırıyor (tek değişkenli F, model değil)
- **(A) mutlak güç:** En güçlü 50 özniteliğin 50'sinde cg > sg. Bantlara göre dağılım: beta 24, alfa 16, teta 8, delta 2. Suçlularda genlik genel olarak daha düşük. 01'deki kanal SD farkıyla aynı yönde.
- **(B) göreli güç:** En güçlü 50 özniteliğin bant dağılımı:
  - Delta: 31 öznitelik, **hepsinde sg > cg**. 13'ü frontal (C bloğu).
  - Alfa: 18 öznitelik, **hepsinde sg < cg**.
  - Teta: 1.
  - Yani suçlularda göreli olarak daha fazla delta ve daha az alfa var.

## Yorum ve sınırlar (kural "gerçek spektral fark ihtimali" diyor, ama)
1. **Göreli güç yalnızca çarpımsal kazanç farkını ortadan kaldırır.** Toplamsal etkiler göreli spektrumu yine değiştirebilir. Bunlar: elektrot empedansına bağlı gürültü, ortam gürültüsü, oküler ve kas artefaktları. Yani B'nin anlamlı çıkması batch ya da kayıt koşulu açıklamasını dışlamaz, yalnızca zayıflatır.
2. **C bloğunda (ön-frontal ve orta-frontal) delta fazlası tipik bir oküler artefakt imzası.** Kalan göz hareketi ve kırpma artığı özellikle göz açık epoklarda (O1, O2) görülür. Uyuklama da aynı imzayı verir. Madde etkisi de bir olasılık. Bu veriyle hangisinin geçerli olduğu ayırt edilemez.
   - **[v4 notu, F4]** v3'teki "oküler artık açıklaması zayıfladı" (E5) yorumu fazla güçlüydü. 07e haritasında (Şekil S1) en büyük 10 etkinin 10'u ve en büyük 20 etkinin 18'i C bloğunda, frontopolar ve ön-frontal elektrotlarda: sg'de göreli delta ↑, teta ↓, beta ↓; uzun blokta alfa farkı yok (A bloğu medyan g = 0,015). Göz kapalıyken de göz hareketleri, ICA sonrası artık, alın derisi ve ter potansiyelleri ve elektrot teması frontopolar bölgede düşük frekansta iz bırakabilir. EOG kanalları yayımlanmadığı için bunlar ne doğrulanabilir ne dışlanabilir. Uzun blok sonucu yalnızca göz açıkken oluşan kırpma ve sakkad artefaktını tek açıklama olmaktan çıkarıyor.
3. **03 ile çelişki var.** 03'te göreli öznitelikler sg vs cg için yalnızca 0,53 AUC vermişti. Ama iki analiz dört açıdan farklı:
   - Veri: 03'te 8 dakikalık göz kapalı blok kullanıldı; 07'de ilk 4 dakikanın kapalı ve açık epokları.
   - Öznitelik düzeyi: 03'te 14 ROI özniteliği; 07'de 512 kanal düzeyinde öznitelik.
   - Model: 03'te L2 lojistik regresyon; 07'de seçimli SVM.
   - Örneklem: 03'te 111 denek; 07'de 100.

   Bu farklardan hangisinin belirleyici olduğu test edilmedi.
4. **Örneklem ve seçim.** Excel ile veri setinin kesişimi olan 100 denek kullanıldı. Bu bir seçim, ama denek seçimi etiketten bağımsız.
5. **Bu sonuç keşifsel.** Önceden belirlenmiş tek birincil test 05'tir. Bu sonuç birincil bulgu olarak sunulamaz.

## Karar için seçenekler (hiçbiri çalıştırılmadı)
- **(i)** 05 ve 06'yı planlandığı gibi çalıştırmak, 07'yi keşifsel bir bulgu olarak raporlamak.
- **(ii)** Önce 07'nin kaynağını ayrıştırmak; bu yeni bir keşifsel analiz olur ve CLAUDE.md'ye önceden tanımlanması gerekir. Önerilen ayrıştırmalar:
  - (a) B'yi yalnız göz kapalı ve yalnız göz açık epoklarla ayrı ayrı çalıştırmak (oküler artefakt testi).
  - (b) Frontal (C bloğu) kanalları çıkarmak.
  - (c) EMG ve frontal delta'yı kalıntılayarak çıkarmak.
  - (d) 03'teki uzun blok ROI özniteliklerini kanal düzeyinde, aynı SVM pipeline'ıyla çalıştırmak; böylece 03 ile 07 uzlaştırılır.
  - (e) B ile sg2 ve cg'yi karşılaştırmak, yani batch negatif kontrolünü 07'ye uygulamak.
- **(iii)** Makale çerçevesini yeniden değerlendirmek. "Titiz null sonuç" çerçevesi, B'nin sonucu nedeniyle zayıflıyor.

## Hazır ama çalıştırılmayan
- `05_alpha_reactivity_v1_2026-10-02.py`: plana uygun yazıldı, çalıştırılmadı.
- `04b_leakage_gd_v1_2026-10-02.py`: 04-B'ye GD sütunu ekleyecek. Aynı seed'lerle yeniden çalıştırıp AUC'leri kayıtlı sonuçlarla karşılaştıracak. Çalıştırılmadı.
