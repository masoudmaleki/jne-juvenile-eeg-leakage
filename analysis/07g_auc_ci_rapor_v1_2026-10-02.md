# 07g (YALNIZ NİCELENDİRME): keşifsel AUC'lerin %95 güven aralıkları, sonuç raporu (2026-10-02)

**Tanım:** CLAUDE.md "07g"; kaynak DENETIM_RAPORU_3 bölüm 3. Karar kuralı yok. Hiçbir iddia bu sonuca göre güçlendirilmez.
**Zaman kaydı (git):**
- Tanım: `e81e61b` (12:08:23). Analizden önce atıldı, yalnız CLAUDE.md'ye 19 satır ekliyor.
- Analiz: 12:09:29'da başladı (ilerleme kaydı).
- Sonuç: `e5dfeb6` (12:12:25). Yalnız 07g betiği ve çıktılarını, ayrıca `git_show_07f.txt`'yi içeriyor.
- Metin düzeltmeleri (F1–F7): `8a0931a`.

**Betik:** `07g_auc_ci_v1_2026-10-02.py`. `M7.nested` ve `M7C.transfer`'in birebir kopyaları kullanıldı; tek fark, denek ve kat skorlarını da döndürmeleri. Seed'ler aynı (20261001 + r). Yeniden eğitim yaklaşık 1,5 dakika, bootstrap yaklaşık 40 saniye sürdü.
**Okunanlar:** 07, 07abc, 07de ve 07f'nin öznitelik npz'leri, `ckpt_real.jsonl` ve `transfer_folds.csv` dosyaları; `01_data_audit_v2`. Ham veriye yazılmadı.
**Çıktılar:** `07g_auc_ci_v1_2026-10-02_{results.csv, verify.csv, scores.pkl, progress.log}`

**Çalıştırma notu:** İlk çalıştırma, doğrulama tamamlandıktan sonra durdu. Neden: Windows konsolu "≤" karakterini yazamadı (`UnicodeEncodeError`, cp1254). Hesaplamayla ilgili bir hata değildi. Betik, kaydedilmiş skorlarla `PYTHONIOENCODING=utf-8` kullanılarak yeniden çalıştırıldı ve doğrulama yeniden yapıldı. Bu yüzden ilerleme kaydında iki başlangıç satırı var. Betikte sonradan yalnız docstring'deki çıktı adı düzeltildi (`scores.npz` → `scores.pkl`).

## 1. Doğrulama: yeniden üretilen AUC'ler kayıtlı değerlerle birebir aynı mı?
**Evet.** 1120 değer karşılaştırıldı:
- 6 kaynak model × 20 tekrar = 120 denek AUC'si;
- 5 transfer modeli × 100 kat × 2 (sg2 = 24 ve 25) = 1000 kat AUC'si.

| | Maks \|fark\| |
|---|---|
| Kaynak modeller (07 A, 07 B, 07a kapalı, 07a açık, 07b, 07e) | 0 |
| Transfer modelleri (07c, 07d × 3, 07f) | 5,55e-17 |

Eşik 1e-12'ydi; tüm değerler eşiğin altında. Ayrıntı: `07g_..._verify.csv`.

## 2. Kaynak modeller (sg vs cg; n = 45 / 55)
GA, sınıf içi tabakalı denek bootstrap'ıyla hesaplandı (06 ile aynı yöntem; 2000 yineleme). Bootstrap edilen AUC, 20 tekrarın ortalama denek skorundan hesaplanan AUC.

| Model | Tekrar ortalaması (kayıtlı) | Ortalama skordan AUC | %95 GA |
|---|---|---|---|
| 07 A, log10 mutlak, tüm epoklar | 0,754 | 0,771 | 0,672–0,860 |
| 07 B, göreli, tüm epoklar | 0,734 | 0,800 | 0,706–0,886 |
| 07a göz kapalı | 0,645 | 0,709 | 0,604–0,809 |
| 07a göz açık | 0,709 | 0,767 | 0,669–0,859 |
| 07b kapalı, C bloğu çıkarılmış | 0,582 | 0,609 | 0,495–0,725 |
| 07e uzun blok | 0,746 | 0,781 | 0,685–0,867 |

**Okuma uyarısı:**
- Tekrarların skorları ortalanınca AUC yükseliyor (topluluk etkisi), bazı modellerde belirgin biçimde: 07 B'de 0,734'ten 0,800'e, 07a kapalıda 0,645'ten 0,709'a.
- GA bu yükselmiş AUC'nin çevresinde kurulu. Kayıtlı tekrar ortalaması GA'nın alt yarısında kalıyor; 07 B'de alt sınıra yakın.
- Bu yüzden kaynak GA'ları "ayrışma ne kadar güçlü" sorusu için iyimser okunmamalı. Raporlarken nokta tahmini ile GA aynı yöntemden verilmeli: "0,781 (0,685–0,867; tekrar ortalaması 0,746)". 06'da da bu biçim kullanılmıştı.
- Bu bir sorunu da açık bırakıyor: 07a kapalının GA'sı (0,604–0,809), kural boşluğundaki tekrar ortalamasını (0,645) içeriyor. Kural sonucu ("belirsiz") değişmez, çünkü 07g'de karar kuralı yok.

## 3. Transfer modelleri (held-out cg vs sg2 = 24; kat içi)
GA, ağırlıklı denek bootstrap'ıyla hesaplandı:
- cg (55) ve sg2 (24) için çok terimli çarpanlar; aynı çarpanlar o yinelemedeki 100 katın hepsinde kullanıldı.
- Kat AUC'si ağırlıklı Mann–Whitney ile hesaplandı; 2000 yineleme.
- Held-out cg ağırlığı 0 olan kat hiç çıkmadı (atlanan kat değerlendirmesi 0).

| Model | Transfer AUC (GA) | Yaklaşık olarak dışlanan | Anlamlılık eşiği (sıfırın tek yönlü %95'i) | p | Atipik 2 sg2 hariç (betimsel, 22 sg2) |
|---|---|---|---|---|---|
| 07c, B göz kapalı | 0,569 (0,439–0,688) | AUC > 0,69 | 0,638 | 0,264 | 0,543 |
| 07d, A tüm epoklar | 0,549 (0,439–0,662) | AUC > 0,66 | 0,586 | 0,224 | 0,566 |
| 07d, B tüm epoklar | 0,589 (0,475–0,702) | AUC > 0,70 | 0,633 | 0,194 | 0,565 |
| 07d, B göz açık | 0,553 (0,446–0,660) | AUC > 0,66 | 0,621 | 0,289 | 0,534 |
| 07f, B uzun blok | 0,582 (0,463–0,704) | AUC > 0,70 | 0,601 | 0,104 | 0,561 |

**F2'deki yaklaşık GA'larla karşılaştırma:** Kesin GA'lar daha dar: üst sınırlar 0,660–0,704, yaklaşık değerlerde 0,69–0,73. Gözlenen bootstrap SD'si 0,056–0,064, yaklaşık hesaptaki SD ise 0,07. Olası neden: transfer AUC'si 100 katın ortalaması olduğu için 55 cg deneğinin hepsi katkı veriyor. Bu açıklama ayrıca test edilmedi.

## 4. Yorum
- **"No evidence of transfer" iddiası aynen geçerli.** 07g bunu ne güçlendiriyor ne zayıflatıyor.
- **Veri "transfer yok" ile "orta düzeyde transfer" arasındaki her şeyle uyumlu.**
  - Dışlanabilen: AUC > yaklaşık 0,66–0,70.
  - Dışlanamayan: 0,60–0,66 civarındaki transfer.
  - Bu yüzden "sg'ye özgü" ya da "transfer etmiyor" denemez (F2, F3).
- **Atipik spektrumlu iki sg2 deneği (1105, 1114) çıkarılınca** transfer AUC'leri 0,534–0,566 oluyor. 07c ve 07d B açıkta biraz düşüyor, diğerlerinde biraz yükseliyor. Sonucu değiştiren tek bir denek yok. Bu betimsel bir analiz; GA ve yeniden eğitim yok.
- **Kaynak ve transfer AUC'leri doğrudan karşılaştırılamaz.** Farklı denek kümeleri ve farklı yöntemlerle hesaplandılar (iç içe CV ile ortalama skor; kat içi transfer). Aralarındaki fark test edilmedi.

## 5. Sınırlılıklar
- **GA'lar yalnız denek örneklemesini içeriyor.** Model eğitimindeki oynaklık (seed, katlama) dahil değil. Bu oynaklık, tekrarlar arası aralıklarla ayrıca görülebilir (Tablo S4). Kaynak modellerde bu aralık 0,09–0,16 genişliğinde.
- **Kaynak modellerde bootstrap edilen AUC, tekrar ortalamasından yüksek** (bkz. 2). Nokta tahmini ve GA aynı yöntemden verilmeli.
- **Transfer bootstrap'ı aynı cg deneklerini 20 tekrarda farklı katlara dağıtıyor;** çarpanlar denek düzeyinde ortak tutularak bu bağımlılık korundu. Percentile GA'nın küçük örneklemdeki kapsama oranı test edilmedi.
- **Çoklu karşılaştırma düzeltmesi yok.** Düzeltme GA'ları genişletir; bu da "transfer kanıtı yok" iddiası açısından tutucu.

## 6. Metne yansıması (commit `8a0931a`)
- 07f v2, 07de v3, şekil başlıkları v4 (Şekil 2b), iskelet v5 (Kural sonucu, Özet, 3.5, 3.6, Sınırlılıklar → Güç): "tespit sınırı" ifadesi kaldırıldı; anlamlılık eşiği ve 07g GA'ları eklendi.
- Tablo S4 (`09_tables_v2_2026-10-02_TableS4.*`): 07–07f için 07g GA'ları eklendi.
- CLAUDE.md: 07g SONUÇ satırı ile 07d ve 07f için tarihli notlar eklendi.
