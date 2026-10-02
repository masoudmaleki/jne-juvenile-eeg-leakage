# MAKALE İSKELETİ v1 (2026-10-02). Yalnızca iskelet, metin yazılmadı.

**Çerçeve (CLAUDE.md):** titiz null sonuç + sızıntı/confound denetimi. "Suçluluk biyobelirteci" iddiası yok.
**Tek birincil hipotez testi:** 05. Bunun dışındaki her şey ya önceden belirlenmiş kontrol (03, 04, 06) ya da keşifsel (07, 07a–c).

## Başlık önerileri (İngilizce)
1. *From 0.91 to chance: data leakage, recording confounds and a pre-specified null result in resting-state EEG classification of juvenile offenders*
2. *Resting-state EEG does not separate adolescent offenders from controls under leakage-free, confound-aware analysis: an audit of an open dataset*
3. *High accuracy without signal: a leakage and confound audit of resting-state EEG in juvenile offenders (OpenNeuro ds006923)*

## Özet (en son yazılacak; yapılandırılmış)
Background / Methods / Results (her birincil sayı GA ile) / Conclusions.

---

## 1. Giriş (yalnızca konu başlıkları)
- Suçluluk ve antisosyal davranışta EEG biyobelirteci arayışı; yüksek doğruluk raporlayan çalışmalar.
- EEG makine öğrenmesinde bilinen sızıntı türleri: epok ya da denek düzeyinde bölme, CV dışında öznitelik seçimi.
- Bu kohort için önceki çalışmalar: nöropsikoloji (Data 2023), MRI (Data 2024). EEG yayını yok.
- Veri seti özgüllüğü: grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey iç içe.
- Amaçlar:
  - (i) veri bütünlüğü denetimi,
  - (ii) sızıntı gösterimi,
  - (iii) tek önceden belirlenmiş hipotez,
  - (iv) null sonucun nicelenmesi,
  - (v) keşifsel kaynak ayrıştırması.

## 2. Yöntem
| Alt bölüm | Kaynak analiz | Tablo / Şekil |
|---|---|---|
| 2.1 Veri seti ve katılımcılar | `participants.tsv`; 03 Adım 0 | **Tablo 1:** sg / sg2 / cg demografi ve confound'lar (yaş, eğitim, madde, tabaka, şiddet suçu, okul terki) |
| 2.2 Kayıt ve önişleme (veri sağlayıcısı) | README, yan dosyalar; 01 | metin |
| 2.3 Veri denetimi ve dışlamalar | 01 (`01_data_audit_v2`) | **Şekil 5a** akış diyagramı; Tablo S1 dışlananlar |
| 2.4 Analiz ön-belirtimi ve karar günlüğü | CLAUDE.md tarihçesi | **Tablo S2:** karar günlüğü (tarih, karar, sonuç görülmeden mi?), QC değişikliği notu dahil |
| 2.5 Öznitelikler (önceden belirlenmiş) | 02 v2 / v3 (Welch, göreli güç, FOOOF fixed 3–30, IAF, EMG/R² kanal kuralı, atipik spektrum kuralı) | Tablo S3 parametreler; Şekil S2 FOOOF QC örnekleri |
| 2.6 Batch negatif kontrolü | 03 | metin |
| 2.7 Sızıntı gösterimi | 04-A (Excel denetimi), 04-B (2×2 + karıştırılmış etiket) | metin |
| 2.8 Birincil hipotez: alfa reaktivitesi | 05 | metin |
| 2.9 Null sonucun nicelenmesi | 06 (bootstrap, DeLong, dışlanabilen etki, Cohen d) | metin |
| 2.10 Keşifsel analizler | 07, 07a–c (karar kurallarıyla) | metin |
| 2.11 İstatistik ve metrikler | İç içe CV, permütasyon, bootstrap; AUC birincil; dengeli doğruluk ve GD ek | metin |

## 3. Sonuçlar
| Alt bölüm | Kaynak analiz | Anahtar sayılar | Tablo / Şekil |
|---|---|---|---|
| 3.1 Veri bütünlüğü | 01, 04-A | 140 → 135/136; 5 dışlama; kayıt dönemi ayrışması; Excel: 12 bilinmeyen ID, sg2 yok, Kurtosis = 3 değer, 0 baytlık dosya | **Şekil 5** (akış + Venn + zaman çizelgesi); Kutu 1: n = 3 ispatı |
| 3.2 Sızıntı gösterimi | 04-B (+ GD) | Naif denek AUC 0,89–0,91; karıştırılmış etiketle 0,79–0,85; doğru pipeline 0,66–0,73; epok sızıntısı +0,21 | **Şekil 1**, **Tablo 2** (AUC, dengeli doğruluk, GD) |
| 3.3 Birincil test: alfa reaktivitesi | 05 | p = 0,395; r = −0,085 [−0,28; 0,11]; HL −0,030 [−0,10; 0,04]; kovaryatlı p = 0,89 | **Şekil 3**, **Tablo 3** |
| 3.4 Önceden belirlenmiş spektral öznitelikler: null ve nicelenmesi | 06, 03 | Suçlu vs cg AUC 0,51 (GA 0,44–0,63; AUC > 0,63 dışlanır, d ≈ 0,48); sg vs cg 0,53; sg vs sg2 0,63 (p = 0,053, α = 0,025) | **Şekil 4** (orman grafiği), **Tablo 4** |
| 3.5 Keşifsel: genlik ve kaynak ayrıştırması | 07, 07a–c | A 0,754 / B 0,734; açık 0,709 > kapalı 0,645 > frontalsız 0,582; transfer 0,569 (p = 0,26); kural sonucu "belirsiz" (kural boşluğu) | **Şekil 2**, Tablo S4 (+ GD) |

## 4. Tartışma (yalnızca konu başlıkları)
- Ana bulgu: önceden belirlenmiş tek test ve nicelenmiş null sonuç. Dışlanabilen etki büyüklükleri.
- Naif pipeline'ların bu veride ürettiği şişkin performans ve bunun literatüre etkisi.
- Keşifsel ayrışmanın doğası:
  - göz açık ve frontal katkı,
  - sg'ye özgü delta artışı,
  - transfer başarısızlığı,
  - kayıt dönemi, kayıt yeri, suç profili ve madde kullanımının ayrıştırılamaması.
- Kural boşluğu (07a) ve şeffaflık.
- Yayımlanan türetilmiş özniteliklerin (Excel) yeniden üretilemezliği; açık veri için öneriler.
- Klinik ve adli çıkarım yapılmaması gerektiği.

## 5. Sınırlılıklar (madde listesi)
- Grup ile kayıt yeri, kayıt dönemi, madde kullanımı ve sosyoekonomik düzey ayrıştırılamıyor. sg ile cg arasında zamansal örtüşme yok.
- Aynı kurum varsayımı doğrulanmadı (yalnızca dosya yolu).
- Örneklem büyüklüğü ve güç: (a) testinde AUC ≈ 0,70'in altındaki etkiler tespit edilemiyor.
- EOG ve ECG kanalları yayımlanmamış: oküler artık doğrudan kontrol edilemiyor (07a–c ile ilgili).
- Önişleme veri sağlayıcısında yapılmış (ASR, ICA, ICLabel); değiştirilemedi.
- 8 dakikalık blokta uyanıklık düşüşü; teta/alfa eğimi kovaryat olarak kullanıldı.
- 06'nın GA'sı model eğitimindeki oynaklığı içermiyor.
- Atipik spektrumlu denekler sg2'de toplanmış (QC kuralı sonradan, grup bakılmadan eklendi).
- 07a karar kuralındaki 0,60–0,65 boşluğu; eşik sonradan değiştirilmedi.
- Excel kohortu yayımlanan veriyle eşleşmiyor; 04-B sonuçları yayımlanan EEG'ye genellenemez.

## Önerilen şekiller (4–5)
| No | İçerik | Kaynak dosyalar | Durum |
|---|---|---|---|
| **Şekil 1** | Sızıntı: (a) 2×2 hücre × model AUC (N1–N4, P); (b) N1 ve P için karıştırılmış etiket dağılımı ile gerçek değer; (c) GD ek paneli | `04b_leakage_v1_..._results.csv`, `_null.npz`, `04b_leakage_gd_..._results.csv` | üretilecek |
| **Şekil 2** | Keşifsel kademe: B tüm epoklar 0,734 → açık 0,709 → kapalı 0,645 → kapalı-frontalsız 0,582 → transfer sg2 0,569; her biri sıfır dağılımı bandıyla; 0,60/0,65 eşikleri ve kural boşluğu işaretli | `07_..._results.csv`, `07abc_..._results.csv`, ckpt null'ları | üretilecek |
| **Şekil 3** | Birincil test: ARI dağılımı (sg, sg2, cg ayrı; suçlu birleşik) + HL kayması ve GA | `05_..._subjects.csv`, `_results.csv` | üretilecek |
| **Şekil 4** | Null sonuç orman grafiği: 06 (suçlu vs cg), 03 (sg vs cg, sg vs sg2, transfer), 05 (r) — GA ve "dışlanabilen etki" bölgesi | `06_..._results.csv`, `03_..._results.csv`, `05_..._results.csv` | üretilecek |
| **Şekil 5** | Veri ve kohort: (a) 140 → dışlamalar akışı; (b) Excel 112 ile yayımlanan 140 Venn'i (100 ortak, 12 yalnız Excel'de, 40 yalnız veri setinde); (c) gruplara göre kayıt tarihi zaman çizelgesi | `01_data_audit_v2`, `04a_..._ids.csv` | üretilecek |
| Şekil S1–S3 | FOOOF pilot QC (mevcut: `02_features_pilot_qc_v1_...png`); 07 betimsel F topografileri; teta/alfa zaman serileri | 02, 07 | kısmen mevcut |

## Tablolar
- **Tablo 1:** demografi ve confound'lar (sg / sg2 / cg).
- **Tablo 2:** sızıntı (04-B + GD).
- **Tablo 3:** birincil test (05).
- **Tablo 4:** null nicelenmesi (06 + 03).
- **Ek tablolar:** S1 dışlamalar, S2 karar günlüğü, S3 öznitelik parametreleri, S4 keşifsel (07, 07a–c + GD), S5 Excel denetimi (04-A).

## Veri ve kod erişimi (madde)
- Veri: OpenNeuro ds006923 / NEMAR on006923 (v1.0.0).
- Kod: `analysis/` betikleri (01–07c, `metrics_gd.py`); seed 20261001; yazılım sürümleri (MNE 1.10, scikit-learn 1.7.1, fooof 1.1).
