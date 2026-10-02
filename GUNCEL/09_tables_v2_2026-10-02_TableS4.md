# Table S4. Exploratory analyses 07–07f: subject-level AUC, 95% CI (07g), permutation p and Golden Distance

All exploratory; p values unadjusted (D9); 200 permutations (smallest attainable p = 1/201 ≈ 0.005). Pipeline: StandardScaler → SelectKBest(f_classif) → RBF SVM, nested StratifiedGroupKFold (outer 5 × 20 repeats).
Source models (sg vs cg): AUC = mean over 20 repeats (as reported); 95% CI = class-stratified subject bootstrap (2000) of the AUC computed from subject scores averaged over the 20 repeats (AUC_meanscore; the same method as 06). Averaging scores raises the AUC, so the CI is centred on AUC_meanscore, not on the repeat mean.
Transfer models (held-out cg vs sg2, within fold): AUC = mean of 100 fold AUCs; 95% CI = weighted subject bootstrap (multinomial weights for cg 55 and sg2 24; 2000). CIs cover subject sampling only, not model-training variability. Excl. atypical = descriptive transfer AUC without sub-1105sg2 and sub-1114sg2 (no retraining). sg2 offender rate depends on the threshold and cannot be interpreted alone (E1).

| Analysis | Data | Comparison | AUC (repeat mean) | Repeat 2.5–97.5 | AUC (mean score) | 95% CI | Null mean | p | BA | GD ↓ | Sen | Spe | F1 | sg2 "offender" rate | AUC excl. atypical sg2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 07 A | log10 absolute band power, all epochs | sg vs cg (n = 45 / 55) | 0.754 | 0.708–0.801 | 0.771 | 0.672–0.860 | 0.479 | ≤ 0.005 | 0.667 | 0.573 | 0.572 | 0.762 | 0.614 | – | – |
| 07 B | relative band power, all epochs | sg vs cg (n = 45 / 55) | 0.734 | 0.674–0.794 | 0.800 | 0.706–0.886 | 0.479 | ≤ 0.005 | 0.649 | 0.611 | 0.490 | 0.808 | 0.567 | – | – |
| 07a closed | B, eyes-closed epochs (2 × 50 s) | sg vs cg (n = 45 / 55) | 0.645 | 0.578–0.735 | 0.709 | 0.604–0.809 | 0.477 | 0.0149 | 0.601 | 0.664 | 0.472 | 0.729 | 0.522 | – | – |
| 07a open | B, eyes-open epochs (2 × 50 s) | sg vs cg (n = 45 / 55) | 0.709 | 0.635–0.763 | 0.767 | 0.669–0.859 | 0.485 | ≤ 0.005 | 0.650 | 0.592 | 0.581 | 0.719 | 0.603 | – | – |
| 07b | B, eyes closed, C block removed | sg vs cg (n = 45 / 55) | 0.582 | 0.508–0.666 | 0.609 | 0.495–0.725 | 0.479 | 0.0498 | 0.559 | 0.718 | 0.408 | 0.711 | 0.461 | – | – |
| 07e | B, long eyes-closed block (4 × 116.25 s) | sg vs cg (n = 45 / 55) | 0.746 | 0.647–0.801 | 0.781 | 0.685–0.867 | 0.478 | ≤ 0.005 | 0.658 | 0.596 | 0.508 | 0.808 | 0.583 | – | – |
| 07c | B, eyes-closed epochs | held-out cg vs sg2 (n = 55 / 24), within fold | 0.569 | 0.526–0.622 | – | 0.439–0.688 | 0.508 | 0.264 | – | – | – | – | – | 0.437 | 0.543 |
| 07d A all | A, all epochs | held-out cg vs sg2 (n = 55 / 24), within fold | 0.549 | 0.520–0.594 | – | 0.439–0.662 | 0.503 | 0.224 | – | – | – | – | – | 0.193 | 0.566 |
| 07d B all | B, all epochs | held-out cg vs sg2 (n = 55 / 24), within fold | 0.589 | 0.551–0.637 | – | 0.475–0.702 | 0.510 | 0.194 | – | – | – | – | – | 0.330 | 0.565 |
| 07d B open | B, eyes-open epochs | held-out cg vs sg2 (n = 55 / 24), within fold | 0.553 | 0.491–0.592 | – | 0.446–0.660 | 0.508 | 0.289 | – | – | – | – | – | 0.351 | 0.534 |
| 07f | B, long eyes-closed block | held-out cg vs sg2 (n = 55 / 24), within fold | 0.582 | 0.526–0.631 | – | 0.463–0.704 | 0.504 | 0.104 | – | – | – | – | – | 0.297 | 0.561 |
