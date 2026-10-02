# Table S3. Feature extraction and quality-control parameters (A) and group-wise QC summary (B)

| Panel | Item | Setting | sg | sg2 | cg | Source |
|---|---|---|---|---|---|---|
| A. Parameters (prespecified) | Segment | Fixed 465 s from the 3rd eyes-closed marker + 5 s; two halves H1, H2 (232.5 s each) |  |  |  | CLAUDE.md, line 46 |
| A. Parameters (prespecified) | PSD | Welch, 4 s Hann window, 50% overlap (0.25 Hz resolution) |  |  |  | CLAUDE.md, line 47 |
| A. Parameters (prespecified) | Bands (relative power) | delta 1–4, theta 4–8, alpha 8–13, beta 13–30 Hz; denominator = 1–30 Hz total; gamma not a feature (EMG control only) |  |  |  | CLAUDE.md, line 48 |
| A. Parameters (prespecified) | Aperiodic fit (FOOOF) | fooof 1.1; primary: aperiodic mode 'fixed', 3–30 Hz |  |  |  | CLAUDE.md, line 49 |
| A. Parameters (prespecified) | Aperiodic fit, sensitivity | 'knee' mode, 2–30 Hz; sensitivity analysis only, no post hoc choice |  |  |  | CLAUDE.md, line 50 |
| A. Parameters (prespecified) | IAF | Primary: strongest FOOOF peak in 7–13 Hz; secondary: centre of gravity in 7–13 Hz of the aperiodic-removed spectrum; no PSD argmax |  |  |  | CLAUDE.md, line 51 |
| A. Parameters (prespecified) | EMG index | Slope of log10 PSD vs log10 f, 30–40 Hz (flatter/positive = more muscle); covariate in group analyses |  |  |  | CLAUDE.md, line 53 |
| A. Parameters (prespecified) | Channel exclusion | Primary FOOOF R² < 0.9 OR EMG index robust z > 3 (median + 3·1.4826·MAD, one-sided); determined on the full segment, same set for halves |  |  |  | CLAUDE.md, line 54 |
| A. Parameters (prespecified) | ROI features | Computed from the mean spectrum of the retained channels |  |  |  | CLAUDE.md, line 55 |
| A. Parameters (prespecified) | Atypical-spectrum rule | > 25% of channels (> 32/128) excluded → subject flagged; only the EMG rule applied, ROI from all remaining channels; included in primary, excluded in sensitivity analyses |  |  |  | CLAUDE.md, line 59 |
| A. Parameters (prespecified) | Vigilance | Theta/alpha ratio in 30 s windows; slope (log10 ratio per min) as vigilance index; features also for H1 and H2 |  |  |  | CLAUDE.md, line 56 |
| A. Parameters (prespecified) | EMG index caveat | Includes the roll-off of the preprocessing low-pass FIR filter; valid as a relative index only |  |  |  | 02_features_v2_rapor_2026-10-01.md, line 51 |
| B. QC summary, median [Q1–Q3] | Subjects processed (n) |  | 45 | 24 | 66 | 02_features_v2_2026-10-01_subject_qc.csv |
| B. QC summary, median [Q1–Q3] | EMG index (channel median, all channels) |  | −1.88 [−2.37, −1.38] | −2.56 [−3.04, −1.71] | −2.04 [−2.52, −1.41] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | Excluded channels, total |  | 3 [1–7] | 3.5 [1–8] | 3 [1–6] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | … due to R² < 0.9 |  | 0 [0–3] | 0 [0–4.25] | 0 [0–1] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | … due to EMG z > 3 |  | 2 [0–3] | 1 [0–4] | 1 [0–4] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | FOOOF R², channel median |  | 0.989 [0.987–0.990] | 0.985 [0.983–0.990] | 0.990 [0.986–0.992] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | FOOOF R², posterior ROI |  | 0.991 [0.988–0.994] | 0.983 [0.976–0.992] | 0.990 [0.984–0.994] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | Theta/alpha slope, global (log10 ratio/min) |  | 0.014 [−0.006, 0.037] | 0.020 [0.008–0.029] | 0.026 [0.005–0.059] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | Theta/alpha slope, posterior |  | 0.009 [−0.007, 0.024] | 0.017 [0.010–0.032] | 0.029 [0.007–0.070] | 02_descriptive_by_group_v2_2026-10-01.csv |
| B. QC summary, median [Q1–Q3] | Atypical-spectrum subjects (> 32 channels excluded) |  | 0 | 2 | 0 | 02_features_v2_2026-10-01_subject_qc.csv |

**Notes.** Panel A: parameters fixed before any group comparison (CLAUDE.md, 'prespecified primary analysis'); line numbers refer to the files at commit time. Panel B: full 465 s segment, primary FOOOF fit; descriptive only, no group test. Subjects without a long eyes-closed block or with a missing data file are not included (Table S-n).
