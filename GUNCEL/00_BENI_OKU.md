# GUNCEL (2026-10-02): makale için geçerli dosyaların kopyaları

**ANALİZ DONDURULDU (2026-10-02).** Yeni analiz, öznitelik, model ya da analiz betiği çalıştırılmaz. Yalnız kayıtlı sonuçları okuyan şekil ve tablo betikleri çalıştırılabilir; sayılar değişmez. İstisna: hakem isteği. Bu durumda önce CLAUDE.md'ye tanım yazılır, ayrı commit atılır, sonra çalıştırılır.

Bu klasördeki dosyalar **kopyadır**. Asılları `analysis/` ve `analysis/figures/` altında; eski sürümler orada korunuyor. Bir dosya değişirse önce aslı yeni sürüm numarasıyla güncellenir, sonra buraya kopyalanır.

## Dosyalar
| Dosya | Ne? | Asıl yol |
|---|---|---|
| `MAKALE_ISKELETI_v6.md` | Makale iskeleti: başlık, iddialar, bölümler, Tablo S2 (karar günlüğü) | `analysis/MAKALE_ISKELETI_v6.md` |
| `FIGURE_CAPTIONS_v5.md` | Şekil 1–5 ve S1'in İngilizce başlık taslakları | `analysis/figures/FIGURE_CAPTIONS_v5.md` |
| `Fig1_leakage_v2.{png,pdf}` | Şekil 1: sızıntı | `analysis/figures/`; betik `analysis/08_figures_v2_2026-10-02.py` |
| `Fig2_exploratory_cascade_v4.{png,pdf}` | Şekil 2: keşifsel kanal düzeyi ayrışma, sg2'ye transfer, betimsel | `analysis/figures/`; betik `analysis/08_figures_v4_2026-10-02.py` |
| `Fig3_primary_alpha_reactivity_v2.{png,pdf}` | Şekil 3: birincil test (alfa reaktivitesi) | `analysis/figures/`; betik 08 v2 |
| `Fig4_prespecified_null_v2.{png,pdf}` | Şekil 4: ROI düzeyinde null | `analysis/figures/`; betik 08 v2 |
| `Fig5_cohort_v2.{png,pdf}` | Şekil 5: kohort, Excel kaynağı, kayıt dönemi | `analysis/figures/`; betik 08 v2 |
| `FigS_07e_feature_map_v1.{png,pdf}` | Şekil S1: 07e kanal × bant Hedges g (betimsel) | `analysis/figures/`; betik `analysis/07e_feature_map_v1_2026-10-02.py` |
| `09_tables_v1_2026-10-02_Table1.{md,csv}` | Tablo 1: katılımcı özellikleri ve confound'lar (140) | `analysis/`; betik `analysis/09_tables_v1_2026-10-02.py` |
| `09_tables_v2_2026-10-02_TableSn.{md,csv}` | Tablo S-n: her analizin örneklemi | `analysis/`; betik `analysis/09_tables_v2_2026-10-02.py` |
| `09_tables_v2_2026-10-02_TableS4.{md,csv}` | Tablo S4: keşifsel analizler 07–07f, 07g %95 GA, GD | `analysis/`; betik 09 v2 |
| `git_log.txt` | Commit geçmişi (tarih ve saatli) | `analysis/git_log.txt` |
| `git_show_07f.txt`, `git_show_07g.txt` | 07f ve 07g'nin tanım ve sonuç commit içerikleri (zaman kaydı kanıtı) | `analysis/` |

## Makaledeki sayıların kaynağı
| Sayı grubu (iskelet v6 bölümü) | Rapor | Sayısal kaynak (CSV / log) |
|---|---|---|
| Kohort, örneklemler, kısa kayıtlar, kayıt dönemi (3.1) | `analysis/01_data_audit_v2_2026-10-01.py` çıktıları; CLAUDE.md "Audit sonuçları" | `analysis/01_data_audit_v2_2026-10-01.csv`, `analysis/09_tables_v1_2026-10-02_Table1.csv`, `analysis/09_tables_v2_2026-10-02_TableSn.csv` |
| Excel öznitelikleri, 12 bilinmeyen ID, 3 değerden istatistik (3.1) | `analysis/04a_excel_audit_v1_2026-10-01_rapor.md` | `analysis/04a_excel_audit_v1_2026-10-01_{ids,id_match,n_points,structure}.csv` |
| Sızıntı: naif 0,89–0,91, dengeli doğruluk 0,76–0,80; karıştırılmış etiket; P (3.2) | `analysis/04b_leakage_rapor_v2_2026-10-02.md` | `analysis/04b_leakage_v1_2026-10-01_results.csv`, `analysis/04b_leakage_gd_v1_2026-10-02_results.csv`, `analysis/04b_leakage_v1_2026-10-01_null.npz` |
| Birincil test: p = 0,395, r = −0,085 [−0,28; 0,11], HL, kovaryatlı (3.3) | `analysis/05_alpha_reactivity_v1_2026-10-02_rapor.md` | `analysis/05_alpha_reactivity_v1_2026-10-02_{results,descriptive,subjects}.csv` |
| ROI düzeyi: 0,54 [0,44–0,63], tekrar ortalaması 0,51 (3.4) | `analysis/06_null_quantification_rapor_v4_2026-10-02.md` | `analysis/06_null_quantification_v1_2026-10-02_{results,oof}.csv` |
| sg vs cg 0,53; sg vs sg2 0,629 (p = 0,053, eşik 0,651) (3.4, Güç) | `analysis/03_batch_negcontrol_v1_2026-10-01_rapor.md` | `analysis/03_batch_negcontrol_v1_2026-10-01_results.csv` |
| Kanal düzeyi ayrışma 07 A/B (3.5) | `analysis/07_amplitude_decomp_rapor_v4_2026-10-02.md` | `analysis/07_amplitude_decomp_v1_2026-10-02_results.csv` |
| 07a kapalı/açık, 07b, 07c (3.5, 3.6) | `analysis/07abc_source_decomp_rapor_v4_2026-10-02.md` | `analysis/07abc_source_decomp_v1_2026-10-02_{results,transfer_folds,descriptive}.csv` |
| 07d transfer, 07e uzun blok (3.5, 3.6) | `analysis/07de_transfer_longblock_rapor_v3_2026-10-02.md` | `analysis/07de_transfer_longblock_v1_2026-10-02_{results,transfer_folds}.csv` |
| 07f uzun blok transferi (3.6) | `analysis/07f_longblock_transfer_rapor_v2_2026-10-02.md` | `analysis/07f_longblock_transfer_v1_2026-10-02_{results,transfer_folds}.csv` |
| %95 GA'lar (kaynak ve transfer), atipik sg2 hariç, anlamlılık eşikleri (3.5, 3.6, Güç) | `analysis/07g_auc_ci_rapor_v2_2026-10-02.md` | `analysis/07g_auc_ci_v1_2026-10-02_results.csv`; eşikler: `07abc/07de/07f_..._ckpt_tr_null.jsonl` |
| 07e haritası: \|g\| ≤ 0,58, frontopolar yoğunlaşma, A bloğu alfa g = 0,015 (3.5, Tartışma) | CLAUDE.md 07e harita satırı ve F4 notu | `analysis/07e_feature_map_v1_2026-10-02.csv` |
| Uyanıklık (teta/alfa eğimi), EMG, ROI öznitelikleri (Tartışma, 2.5) | `analysis/02_features_v2_rapor_2026-10-01.md` | `analysis/02_features_v2_2026-10-01_{roi,ta_timeseries,subject_qc}.csv`, `analysis/02_features_v3_2026-10-01_roi.csv`, `analysis/02_descriptive_by_group_v2_2026-10-01.csv` |
| Yaş, kayıt saati, şiddet suçu oranı (Tartışma) | – | `analysis/09_tables_v1_2026-10-02_Table1.csv`, `analysis/03_step0_demografi_v1_2026-10-01.csv` |

Metinde GA'lar iki ondalıkla verilir; Tablo S4'te üç ondalık kalabilir (GA sınırlarında Monte Carlo hatası yaklaşık ±0,01).

## Henüz dosyası olmayan tablolar
| Tablo | İçerik | Kaynak |
|---|---|---|
| Tablo 2 | Sızıntı: N1–N4 ve P, SVM/RF, AUC, dengeli doğruluk, GD | `analysis/04b_leakage_rapor_v2_2026-10-02.md`; `analysis/04b_leakage_gd_v1_2026-10-02_results.csv` |
| Tablo 3 | Birincil test (alfa reaktivitesi) | `analysis/05_alpha_reactivity_v1_2026-10-02_rapor.md`; `_results.csv`, `_descriptive.csv` |
| Tablo 4 | ROI düzeyinde null ve 03 karşılaştırmaları | `analysis/06_null_quantification_rapor_v4_2026-10-02.md`; `06_..._results.csv`, `03_..._results.csv` |
| Tablo S3 | Öznitelik tanımları ve QC (kanal dışlama, atipik spektrum) | `analysis/02_features_v2_rapor_2026-10-01.md`; `02_features_v2_2026-10-01_subject_qc.csv`, `_channels.csv` |

Bu tablolar üretilirken yalnız kayıtlı CSV'ler okunur; yeni hesap yapılmaz.
