# 07a–c Kaynak ayrıştırması (KEŞİFSEL): sonuç raporu (2026-10-02)

**Tanım:** CLAUDE.md "07a–c". Sonuç görülmeden önce, karar kurallarıyla birlikte yazıldı. Plandan sapma yok.
**Betik:** `07abc_source_decomp_v1_2026-10-02.py`. Checkpoint ve ilerleme kaydı içeriyor. Toplam süre yaklaşık 17 dakika.
**Veri:** B seti (göreli bant gücü), 07 ile aynı 100 denek (sg 45, cg 55). 07c için ek olarak sg2'nin göz kapalı epokları kullanıldı (24 denek; 25'li versiyon ek satırda). Ham veriye yazılmadı.

## Sonuçlar
| Analiz | Denek AUC (20 tekrar; 2,5–97,5) | Sıfır dağılımı ortalaması [%97,5] | p (200 perm.) | "Yüksek"? (AUC ≥ 0,65 ve p < 0,05) | GD ↓ | Sen / Spe |
|---|---|---|---|---|---|---|
| 07a yalnız göz kapalı (C1 + C2) | **0,645** (0,578–0,735) | 0,477 [0,605] | **0,015** | Hayır (AUC eşiğin hemen altında) | 0,664 | 0,47 / 0,73 |
| 07a yalnız göz açık (O1 + O2) | **0,709** (0,635–0,763) | 0,485 [0,597] | **0,005** | **Evet** | 0,592 | 0,58 / 0,72 |
| 07b kapalı, frontal C bloğu çıkarılmış | **0,582** (0,508–0,666) | 0,479 [0,616] | **0,050** | Hayır | 0,718 | 0,41 / 0,71 |
| 07c transfer: held-out cg vs sg2 (24), kat içi | **0,569** (0,526–0,622) | 0,508 [0,649] | **0,264** | – | – | sg2'nin suçlu sınıflanma oranı 0,44 |
| 07c, sg2 = 25 (1084sg2 dahil) | 0,576 | – | – | – | – | – |

**Önceden tanımlanan kurala göre sonuç: BELİRSİZ (kural boşluğu).**
- Karar kuralında 0,60 ile 0,65 arasındaki göz kapalı AUC değerleri için tanımlı bir sonuç yoktu. Kural yalnızca "≤ 0,60" ve "≥ 0,65" durumlarını kapsıyordu.
- Gözlenen 0,645 tam bu boşluğa düştü. Sonuç bu nedenle belirsizdir.
- Eşik sonradan değiştirilmedi ve değiştirilmeyecek (kullanıcı kararı, 2026-10-02).
- Keşifsel ayrıştırma burada sona erdi; yeni öznitelik ya da analiz eklenmeyecek.

Ayrıntı:
- **Oküler artefakt kuralı tutmuyor:** bu kural göz kapalı AUC ≤ 0,60 istiyor; gözlenen 0,645.
- **Gerçek spektral fark kuralı tutmuyor:** bu kural göz kapalı AUC ≥ 0,65 ve 07b'nin de korunmasını istiyor. Gözlenen 0,645 (p = 0,015) ve 07b 0,582 (p = 0,050, eşiğin tam sınırında).

**Not:** İki karar noktası eşiğin çok yakınında: 0,645'e karşı 0,65 ve 0,0498'e karşı 0,05. Sonuç, eşiklerin küçük oynamalarına karşı kırılgan.

## Betimsel: göz kapalı göreli güç, grup medyanları (deneklerin epok ve kanal ortalaması)
| Ölçü | sg | sg2 (24) | cg |
|---|---|---|---|
| Göreli delta, tüm kanallar | **0,314** | 0,265 | 0,263 |
| Göreli delta, frontal C | **0,375** | 0,327 | 0,314 |
| Göreli alfa, tüm kanallar | 0,422 | **0,369** | 0,455 |
| Göreli alfa, A bloğu (posterior/orta hat) | 0,504 | **0,397** | 0,542 |

- **Delta artışı sg2'de görülmüyor.** sg2'nin göreli deltası cg'ye çok yakın; delta artışı sg'ye özgü.
- **Alfa düşüşü sg2'de de var, hatta daha güçlü.** Ancak 07c transfer modeli sg2'yi cg'den ayıramadı (AUC 0,57, p = 0,26).

## Yorum (keşifsel; kuralın "belirsiz" sonucunu değiştirmez)
1. **Kademeli bir tablo var.** Ayrışma göz açık epoklarda en güçlü (0,71). Göz kapalı epoklarda daha zayıf (0,645). Frontal kanallar çıkarılınca daha da zayıflıyor (0,58).
   - Bu tablo, ayrışmanın bir kısmının frontal ve göz açıkken ortaya çıkan bir kaynaktan geldiğiyle uyumlu (oküler artık ya da göz açıkken frontal aktivite).
   - Ama göz kapalı durumda frontal olmayan kanallarda da zayıf bir ayrışma kalıyor. Yani kaynak tek bir faktöre indirgenemiyor.
2. **Transfer başarısız:** 07c'de AUC 0,57, p = 0,26. sg ile cg üzerinde öğrenilen göz kapalı imza sg2'ye taşınmıyor.
   - Bu sonuç ayrışmanın sg grubuna ya da kayıt dönemine özgü olmasıyla tutarlı.
   - Ancak sg2, suç profili (şiddet), alkol kullanımı ve yaş bakımından da sg'den farklı (03 Adım 0). Dolayısıyla "batch" yorumu tek açıklama değil.
   - Ayrıca kural 07c'ye yalnızca "gerçek fark" dalında başvuruyordu; bu dala girilmediği için 07c sonucu betimsel kalıyor.
3. **İmza sg'ye özgü:** delta artışı sg'de var, sg2'de yok. Bu, 07'deki ayrışmanın "suçlu olma" ile değil, sg alt grubunun özellikleriyle ilişkili olduğunu düşündürüyor. Bu özellikler kayıt dönemi (2021 yazı), şiddet profili ve başka farklar olabilir.

## Çıktılar
`07abc_source_decomp_v1_2026-10-02_{results,transfer_folds,descriptive}.csv`, `_ckpt_*.jsonl`, `_progress.log`, `_sg2_features.npz`
