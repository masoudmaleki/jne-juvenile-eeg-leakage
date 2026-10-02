# Figure caption drafts v3 (2026-10-02)
Figures 1, 3, 4 and 5: `figures/Fig*_v2.*` (`08_figures_v2_2026-10-02.py`). Figure 2: `figures/Fig2_exploratory_cascade_v3.*` (`08_figures_v3_2026-10-02.py`).
Supplementary 07e map: `figures/FigS_07e_feature_map_v1.*` (`07e_feature_map_v1_2026-10-02.py`).
v3 corrections follow DENETIM_RAPORU_2: E2 (Fig. 4), E4 and E6 (Fig. 2); 07f added. Exploratory p values are unadjusted (D9).

**Figure 1. Data leakage inflates the classification of offenders versus controls.**
(a) Subject-level ROC-AUC on the published, derived Excel features. The naive pipeline (N1) was built in this study to represent a common error; the data providers published no classifier. Shading marks epoch-level leakage (row-level CV, N1–N2) and feature-selection leakage (selection on all data, N1 and N3). (b) Under subject-level label shuffling, N1 still reaches an AUC of 0.79–0.85, whereas the nested subject-level pipeline (P) falls to chance. (c) Golden Distance (lower is better) summarises accuracy, sensitivity, specificity and F1 in one number and ranks the pipelines in the same order as AUC.

**Figure 2. Offenders in subgroup sg separate from controls across recording segments, but no model shows significant transfer to the second offender subgroup (sg2).**
(a) Nested-SVM subject-level ROC-AUC for sg vs controls (100 ID-verified participants), with grey bars for the shuffled-label null (95%). Filled markers indicate p < 0.05; p ≤ 0.005 is the smallest value attainable with 200 permutations. The shaded band at the eyes-closed column marks the 0.60–0.65 range for which the decision rule defined no outcome. "C block out" removes the 32 Biosemi C-block electrodes: prefrontal (Fp, AF), midline frontal (Fz, FCz, F1/F2, FC1) and right frontal (F4/F6/F8, AF8, FC2); left frontal electrodes remain. "Long eyes-closed block" is the 465-s eyes-closed block split into four 116-s segments. (b) Models trained on sg and controls were tested on held-out controls vs sg2 (n = 24) within each fold. None showed significant transfer (AUC 0.55–0.59; p = 0.10–0.29); the detection limit was about 0.60–0.65, so the result is "no evidence of transfer" rather than evidence of no transfer. (c) Eyes-closed relative delta (C block) and relative alpha (A block), median [IQR].

**Figure 3. The single pre-specified hypothesis test, alpha reactivity, shows no group difference.**
(a) Posterior alpha reactivity index, (C − O)/(C + O), by subgroup. Offenders (n = 70) did not differ from controls (n = 66; Mann–Whitney p = 0.395). (b–c) Rank-biserial correlation, Hodges–Lehmann shift and the age- and EMG-adjusted estimate, each with its 95% CI; all intervals include zero.

**Figure 4. Pre-specified ROI-level features do not separate offenders from controls.**
ROC-AUC of an L2 logistic regression on 14 pre-specified ROI-level features from the long eyes-closed block. For offenders (sg + sg2) vs controls, AUC is 0.54 (95% CI 0.44–0.63; repetition mean 0.51), so AUC > 0.63 is approximately excluded. With the same groups (sg vs controls), ROI-level logistic regression gives 0.53, whereas channel-level SVM features from the same block give 0.746 (Fig. 2a). The null result therefore holds only for the ROI-level features and the chosen model.

**Figure 5. Cohort composition, provenance of the derived features, and the recording-period confound.**
(a) Analysis samples branch in parallel from the 140 published participants; they are not successive filtering steps. (b) The derived Excel features cover 112 participants: 12 of them match no published recording, and none of the sg2 participants are included. (c) Recording dates show no temporal overlap between sg and controls; sg2 is closer in time to the controls and overlaps with them only in May–June 2022.

**Figure S1. Channel-level effect sizes behind the long-block separation (descriptive).**
Hedges g (sg − controls) for relative delta, theta, alpha and beta power in the long eyes-closed block, averaged over the four 116-s segments; C-block electrodes are circled. Single-feature effects are small (|g| ≤ 0.58): sg shows slightly higher relative delta (mainly C and D blocks) and lower relative theta (most clearly in the C block), with little difference in relative alpha. No test was performed.
