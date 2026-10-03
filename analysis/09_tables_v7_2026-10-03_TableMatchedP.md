# Table MatchedP. Permutation tests with null statistics matched to the observed statistic (K3, sensitivity analysis)

| Analysis | Comparison | Observed AUC | Original null (5 repeats): mean | Original null: threshold | Original null: p | Matched null (20 repeats): mean | Matched null: threshold | Matched null: p | α | Decision changed |
|---|---|---|---|---|---|---|---|---|---|---|
| 03(a) | sg vs sg2 (ROI features) | 0.629 | 0.498 | 0.651 | 0.053 | 0.499 | 0.646 | 0.042 | 0.025 | no |
| 07 A | sg vs cg | 0.754 | 0.479 | 0.575 | ≤ 0.005 | 0.481 | 0.567 | ≤ 0.005 | 0.050 | no |
| 07 B | sg vs cg | 0.734 | 0.479 | 0.578 | ≤ 0.005 | 0.479 | 0.586 | ≤ 0.005 | 0.050 | no |
| 07a closed | sg vs cg | 0.645 | 0.477 | 0.572 | 0.015 | 0.480 | 0.568 | ≤ 0.005 | 0.050 | no |
| 07a open | sg vs cg | 0.709 | 0.485 | 0.580 | ≤ 0.005 | 0.485 | 0.579 | ≤ 0.005 | 0.050 | no |
| 07b | sg vs cg | 0.582 | 0.479 | 0.578 | 0.0498 | 0.480 | 0.581 | 0.055 | 0.050 | yes |
| 07e | sg vs cg | 0.746 | 0.478 | 0.572 | ≤ 0.005 | 0.479 | 0.569 | ≤ 0.005 | 0.050 | no |
| 07c | held-out cg vs sg2 (transfer) | 0.569 | 0.508 | 0.638 | 0.264 | 0.508 | 0.637 | 0.249 | 0.050 | no |
| 07d A all | held-out cg vs sg2 (transfer) | 0.549 | 0.503 | 0.586 | 0.224 | 0.504 | 0.584 | 0.209 | 0.050 | no |
| 07d B all | held-out cg vs sg2 (transfer) | 0.589 | 0.510 | 0.633 | 0.194 | 0.511 | 0.632 | 0.199 | 0.050 | no |
| 07d B open | held-out cg vs sg2 (transfer) | 0.553 | 0.508 | 0.621 | 0.289 | 0.509 | 0.615 | 0.294 | 0.050 | no |
| 07f | held-out cg vs sg2 (transfer) | 0.582 | 0.504 | 0.601 | 0.104 | 0.504 | 0.599 | 0.114 | 0.050 | no |

**Notes.** Observed: mean over 20 cross-validation repeats (source models: subject-level AUC; transfer models: within-fold AUC of held-out controls vs sg2). Original null: 5 repeats per permutation. Matched null: the same permutations extended to 20 repeats; their first 5 repeats reproduce the original null (maximum difference 0). Threshold: one-sided 95th percentile of the null (03(a): 97.5th). p = (k+1)/(N+1); N = 200 (03(a): 1000). 03(b) is not included because its observed value lies below the null mean; 04-B is not included (section 2.11).
