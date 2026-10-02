# 05 Alfa reaktivitesi: TEK birincil hipotez testi, sonuç raporu (2026-10-02)

**Plan:** `04_05_PLAN_v2_2026-10-01.md` ve CLAUDE.md. Plana birebir uyuldu, sapma yok.
**Betik:** `05_alpha_reactivity_v1_2026-10-02.py`. Seed 20261001.
**Okunanlar:** 140 adet `acq-epochs .set`, `participants.tsv`, 02 v2 kanal bayrakları, 02 v3 atipik bayrağı. Ham veriye yazılmadı.
**Çıktılar:** `05_alpha_reactivity_v1_2026-10-02_{subjects,results,descriptive}.csv`

## Yöntem (özet)
- **ARI = (C − O) / (C + O).** C = (C1 + C2)/2 ve O = (O1 + O2)/2; ikisi de posterior ROI'nin mutlak alfa (8–13 Hz) gücü.
- **Veri:** Her epok, işaretten 5 s sonra başlayan 50 s. Welch: 4 s Hann penceresi, %50 örtüşme.
- **Örneklem:** n = 136; bütün deneklerde epok sırası COCO.
- **Kanallar:** 133 denekte 02 v3 kanal seti, 2 atipik denekte yalnız EMG kuralı uygulanmış set, sub-1084sg2'de 9 kanalın hepsi. Posterior ROI'de kullanılan kanal sayısı medyan 9, en az 6.
- **Test:** suçlu (sg + sg2, n = 70) vs cg (n = 66), Mann-Whitney U, iki yönlü, α = 0,05.

## Birincil sonuç: anlamlı değil
| | Suçlu (n = 70) | cg (n = 66) |
|---|---|---|
| ARI medyanı | 0,636 | 0,678 |

| Test | Değer |
|---|---|
| Mann-Whitney U | 2114, **p = 0,395** |
| Rank-biserial r (suçlu > cg pozitif) | **−0,085** [bootstrap %95 GA −0,282; 0,111] |
| Hodges–Lehmann kayması (suçlu − cg, ARI birimi) | **−0,030** [−0,099; 0,039] |

**Önceden belirlenen yorum kuralına göre sonuç negatif; GA sınırları dışlanabilen en küçük etki olarak raporlanır:**
- %95 güvenle şu etkiler dışlanır:
  - Suçlular lehine rank-biserial r > 0,11.
  - cg lehine r < −0,28.
  - Medyan ARI farkı +0,04'ün üstünde ya da −0,10'un altında.
- Bağlam: ARI'nin grup içi IQR'si yaklaşık 0,30.

## Kovaryat duyarlılığı (yaş, EMG; HC3 robust standart hata, n = 136)
| Model | Suçlu katsayısı [%95 GA] | p | Yaş katsayısı (p) | EMG katsayısı (p) |
|---|---|---|---|---|
| OLS ARI ~ suçlu + yaş + EMG | +0,005 [−0,068; 0,079] | 0,886 | −0,031 (0,032) | −0,029 (0,050) |
| OLS rank(ARI) ~ suçlu + yaş + EMG | −0,10 rank [−13,8; 13,6] | 0,988 | −6,1 (0,033) | −4,0 (0,17) |

- Yaş ve EMG modele eklenince grup etkisi tamamen sıfıra iniyor.
- Yaş, ARI ile negatif ilişkili (betimsel bir gözlem; birincil test değil).

## Duyarlılık: n = 140 (kısa kayıtlı 4 sg yalnız C1/O1 ile)
- Mann-Whitney p = 0,279. Rank-biserial −0,107 [−0,293; 0,090]. HL −0,037 [−0,105; 0,032].
- Sonuç değişmiyor.

## Betimsel: alt gruplar (test yok)
| Grup | n | ARI medyanı [Q1–Q3] |
|---|---|---|
| sg | 45 | 0,640 [0,516–0,774] |
| sg2 | 25 | 0,624 [0,461–0,797] |
| cg | 66 | 0,678 [0,493–0,804] |

## Yorum
- **Tek birincil hipotez testinin sonucu negatif:** alfa reaktivitesi suçlular ile kontroller arasında farklı değil.
- Kazanç farkından bağımsız olan bu ölçütte grup farkı yok. Bu, 03'teki null sonuçla (14 öznitelik, AUC 0,53) tutarlı.
- 07'deki keşifsel ayrışmayla birlikte okununca:
  - 07'deki ayrışma ağırlıklı olarak göz açık ve frontal öznitelikler ile sg'ye özgü delta artışından geliyor.
  - Bu ayrışma, kapalı ile açık arasındaki alfa reaktivitesine yansımıyor.
