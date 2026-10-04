# Data leakage and recording confounds in resting-state EEG classification of juvenile offenders

Analysis code, analysis log and result files for:

> Melek M, Melek N. *High accuracy without demonstrated generalisation: data leakage and recording confounds in resting-state EEG classification of juvenile offenders.* Manuscript under review.

## Data

The dataset is not included. All analyses use the open dataset *Dataset of Electroencephalograms of Juvenile Offenders* (OpenNeuro ds006923, version 1.0.0, CC0; doi:10.18112/openneuro.ds006923.v1.0.0). Our copy was obtained from its NEMAR mirror (doi:10.82901/nemar.on006923). All EEG files are identical in size and SHA-256 checksum to the OpenNeuro release (`analysis/11_integrity_v1_*`).

To rerun the analyses, place the dataset in a folder named `v1.0.0/` at the repository root.

## Contents

- `analysis/`: analysis scripts, their outputs (CSV files and Markdown reports), and the scripts that produce the figures and tables. File names carry a version and a date (for example `_v2_2026-10-01`). Older versions are kept unchanged as part of the record.
- `CLAUDE.md`: the project log, in Turkish. It records plans, decision rules, results and corrections in time order.
- `DENETIM_RAPORU_2026-10-02.md` and `analysis/DENETIM_RAPORU_*.md`: audit reports, in Turkish.
- The LaTeX source of the manuscript.
- The git history. The commit identifiers cited in supplementary table S1 of the paper refer to this history.

An English summary of the log is supplementary table S1 of the paper. It is also included here as `analysis/TableS1_decision_log_en_v3_filled.csv`.

## Analyses

Identifiers are those used in the paper.

| ID | Script prefix | Content |
|---|---|---|
| 01 | `01_` | Data audit: durations, block markers, recording dates |
| 02 | `02_` | Spectral features and quality control |
| 03 | `03_` | Batch negative control (region-of-interest features) |
| 04-A | `04a_` | Audit of the precomputed spreadsheet features |
| 04-B | `04b_` | Leakage demonstration: naive pipelines N1–N4 and nested pipeline P |
| 05 | `05_` | Primary test: alpha reactivity |
| 06 | `06_` | Quantification of the region-of-interest null result |
| 07–07f | `07_`, `07abc_`, `07de_`, `07f_` | Exploratory channel-level analyses and transfer to sg2 |
| 07g | `07g_` | Confidence intervals of the exploratory AUCs |
| – | `07e_feature_map_` | Descriptive channel-level effect-size map |
| – | `08_`, `09_`, `10_` | Figures, tables and the analysis-log table |
| K1 | `11_integrity_` | File integrity check (SHA-256) |
| K2 | `12_matched_perm_p_` | Check of the permutation statistics |
| K3 | `13_matched_null_` | Permutation tests with matched null statistics |

`metrics_gd.py` computes the Golden Distance.

## Reproducing the analyses

1. Use Python 3.13 and install the packages in `requirements.txt`. The main versions are NumPy 2.3.2, SciPy 1.16.1, pandas 2.3.1, scikit-learn 1.7.1, FOOOF 1.1.1 and statsmodels 0.14.6. MNE-Python 1.10.0 and Matplotlib 3.10.8 are used for figures only.
2. Place the dataset in `v1.0.0/`.
3. Run the scripts from the repository root in the order of their identifiers, for example `python analysis/03_batch_negcontrol_v1_2026-10-01.py`. Later scripts read the outputs of earlier ones from `analysis/`.

Random seeds are fixed (20261001). Most scripts run in minutes. The permutation analyses take longer; for example, `13_matched_null` took about 6 hours with 15 parallel workers.

## Use of AI tools

The analysis code was written and executed by an AI coding agent (Claude Code, Anthropic; model Claude Opus 5.5) under the authors' direction. The authors approved every analysis plan, decision rule and interpretation.

Audits of code, numbers and text were carried out in separate sessions of the same model, so they are not independent. A draft of the manuscript was also reviewed by the AI system Astra.

The authors take full responsibility for the analyses and the text.

## License

The code is released under the MIT License (see `LICENSE`). The dataset is not part of this repository; its creators distribute it under CC0.

## Contact

Negin Melek, negin.melek@gumushane.edu.tr
