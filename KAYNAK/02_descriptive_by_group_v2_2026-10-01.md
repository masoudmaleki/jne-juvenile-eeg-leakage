# Grup bazında betimsel QC tablosu (grup farkı testi YOK)

Kaynak: `02_features_v2_2026-10-01_subject_qc.csv`. Tam kesit (465 s), birincil FOOOF (fixed, 3-30 Hz).
İşlenen denek: 135 (sg 45, sg2 24, cg 66); atlanan: 5.

| Metrik | Grup | n | Ortalama (SD) | Medyan [Q1–Q3] | Min–Maks |
|---|---|---|---|---|---|
| EMG indeksi: kanal medyanı, 30-40 Hz log-log eğim (tüm 128 kanal) | sg | 45 | -1.946 (0.928) | -1.884 [-2.366–-1.379] | -5.272–0.218 |
| EMG indeksi: kanal medyanı, 30-40 Hz log-log eğim (tüm 128 kanal) | sg2 | 24 | -2.434 (1.081) | -2.558 [-3.043–-1.709] | -5.193–-0.659 |
| EMG indeksi: kanal medyanı, 30-40 Hz log-log eğim (tüm 128 kanal) | cg | 66 | -2.076 (0.943) | -2.043 [-2.522–-1.405] | -6.022–-0.250 |
| EMG oranı: kanal medyanı, güç 30-40 / 1-40 Hz (tüm kanallar) | sg | 45 | 0.022 (0.012) | 0.020 [0.013–0.027] | 0.005–0.050 |
| EMG oranı: kanal medyanı, güç 30-40 / 1-40 Hz (tüm kanallar) | sg2 | 24 | 0.022 (0.011) | 0.020 [0.013–0.031] | 0.008–0.048 |
| EMG oranı: kanal medyanı, güç 30-40 / 1-40 Hz (tüm kanallar) | cg | 66 | 0.019 (0.011) | 0.016 [0.012–0.023] | 0.003–0.064 |
| Dışlanan kanal sayısı (toplam) | sg | 45 | 4.578 (4.454) | 3.000 [1.000–7.000] | 0.000–16.000 |
| Dışlanan kanal sayısı (toplam) | sg2 | 24 | 10.417 (20.340) | 3.500 [1.000–8.000] | 0.000–88.000 |
| Dışlanan kanal sayısı (toplam) | cg | 66 | 4.333 (4.453) | 3.000 [1.000–6.000] | 0.000–21.000 |
| FOOOF R² < 0,9 nedeniyle | sg | 45 | 2.311 (3.976) | 0.000 [0.000–3.000] | 0.000–14.000 |
| FOOOF R² < 0,9 nedeniyle | sg2 | 24 | 7.708 (20.729) | 0.000 [0.000–4.250] | 0.000–88.000 |
| FOOOF R² < 0,9 nedeniyle | cg | 66 | 1.848 (3.978) | 0.000 [0.000–1.000] | 0.000–19.000 |
| EMG robust z > 3 nedeniyle | sg | 45 | 2.489 (2.801) | 2.000 [0.000–3.000] | 0.000–13.000 |
| EMG robust z > 3 nedeniyle | sg2 | 24 | 2.917 (4.242) | 1.000 [0.000–4.000] | 0.000–16.000 |
| EMG robust z > 3 nedeniyle | cg | 66 | 2.591 (3.143) | 1.000 [0.000–4.000] | 0.000–13.000 |
| FOOOF R² (birincil): kanal medyanı | sg | 45 | 0.987 (0.005) | 0.989 [0.987–0.990] | 0.971–0.993 |
| FOOOF R² (birincil): kanal medyanı | sg2 | 24 | 0.976 (0.029) | 0.985 [0.983–0.990] | 0.873–0.995 |
| FOOOF R² (birincil): kanal medyanı | cg | 66 | 0.988 (0.007) | 0.990 [0.986–0.992] | 0.954–0.996 |
| FOOOF R² (birincil): posterior ROI | sg | 45 | 0.989 (0.007) | 0.991 [0.988–0.994] | 0.963–0.996 |
| FOOOF R² (birincil): posterior ROI | sg2 | 24 | 0.982 (0.011) | 0.983 [0.976–0.992] | 0.956–0.996 |
| FOOOF R² (birincil): posterior ROI | cg | 66 | 0.987 (0.010) | 0.990 [0.984–0.994] | 0.949–0.997 |
| FOOOF R² (birincil): global ROI | sg | 45 | 0.989 (0.010) | 0.992 [0.989–0.995] | 0.951–0.998 |
| FOOOF R² (birincil): global ROI | sg2 | 24 | 0.979 (0.020) | 0.987 [0.969–0.992] | 0.906–0.996 |
| FOOOF R² (birincil): global ROI | cg | 66 | 0.988 (0.012) | 0.992 [0.988–0.995] | 0.938–0.998 |
| Teta/alfa eğimi (log10 oran / dk), global | sg | 45 | 0.018 (0.032) | 0.014 [-0.006–0.037] | -0.047–0.113 |
| Teta/alfa eğimi (log10 oran / dk), global | sg2 | 24 | 0.026 (0.041) | 0.020 [0.008–0.029] | -0.054–0.159 |
| Teta/alfa eğimi (log10 oran / dk), global | cg | 66 | 0.037 (0.044) | 0.026 [0.005–0.059] | -0.020–0.198 |
| Teta/alfa eğimi (log10 oran / dk), posterior | sg | 45 | 0.018 (0.036) | 0.009 [-0.007–0.024] | -0.036–0.125 |
| Teta/alfa eğimi (log10 oran / dk), posterior | sg2 | 24 | 0.028 (0.050) | 0.017 [0.010–0.032] | -0.080–0.188 |
| Teta/alfa eğimi (log10 oran / dk), posterior | cg | 66 | 0.043 (0.051) | 0.029 [0.007–0.070] | -0.021–0.231 |
