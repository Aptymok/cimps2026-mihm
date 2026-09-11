# CIMPS2026 Submission 724450 - R1 Experimental Protocol

## Status
Revision protocol corresponding to the major-changes response. This document freezes the operational choices used for the reproducible R1 rerun. It is not represented as a preregistration.

## Scientific claim
The R1 study tests whether a bounded, acoustic operationalization of MIHM can (a) transform observed audio windows into explicit normalized variables, (b) derive a method-scoped state index Phi_S from a declared clean baseline, (c) respond monotonically or directionally to known controlled perturbations, and (d) preserve provenance and reproducibility. It does not claim universal validation of MIHM, direct measurement of human cognition, multimodal generalization, or superiority to anomaly-detection methods.

## Primary and secondary objects
Primary confirmatory objects reproduce the two sources named in the submitted manuscript: REM618 and easter_egg. A secondary within-corpus robustness set adds AELUDE, BLVCK, ED, YNLPC, and ODIO_DECIRTELO. All are treated as bounded audio objects, not as evidence for all sociotechnical systems.

## Sampling
Audio is loaded mono at 22,050 Hz and partitioned into non-overlapping 4-second windows. For each source, the first half of complete windows defines the clean reference distribution. The second half is held out for evaluation and controlled perturbation generation. No perturbed window is used to fit the clean baseline.

## Operational variables
Fs: mean bounded spectral flux between adjacent L1-normalized spectra.
Di: mean spectral flatness, used only as an acoustic interference/noise-density proxy.
Cs: one minus normalized spectral entropy, used as spectral concentration/coherence proxy.
Dcog: historical symbol retained for traceability, operationally restricted in this study to onset-interval dispersion CV/(1+CV); it is not a direct cognitive measurement.
Er: RMS energy-floor retention P10/P90.
Vi: RMS-envelope variability CV/(1+CV).

## Phi_S
For feature j, center b_j is the median of clean baseline windows and robust scale s_j=max(1.4826 MAD, IQR/1.349, 0.01). With k=3 and equal weights, d_j=min(|x_j-b_j|/(k s_j),1). Phi_S=1-sum_j w_j d_j. Therefore Phi_S is bounded to [0,1] and has a single meaning in this experiment: proximity to the source-specific clean reference state. It is not an absolute health score.

## Controlled ground truth
Noise: SNR 30/20/10 dB.
Clipping: peak threshold ratios 0.90/0.60/0.30.
Dropout: zeroed sample fractions 0.01/0.05/0.10 using five seeded blocks.
Clean held-out windows are label 0; controlled perturbations are label 1. This ground truth denotes known transformations, not semantic or clinical anomalies.

## Baselines
Isolation Forest: 300 trees, random_state 724450, contamination=auto.
One-Class SVM: RBF, gamma=scale, nu=0.05; StandardScaler fitted only on clean baseline windows.

## Metrics and uncertainty
Primary discrimination metric: ROC AUC. AUC confidence intervals use cluster bootstrap resampling at the source-window level. Directional paired tests compare MIHM anomaly score (1-Phi_S) for each perturbation condition against the corresponding clean held-out window using one-sided Wilcoxon signed-rank tests with Holm correction. Median effect sizes receive bootstrap 95% confidence intervals. Severity response is also summarized by Spearman correlation.

## Sensitivity
All six feature weights are perturbed independently +/-20% and renormalized, for 300 draws at k in {2.5,3.0,3.5} (900 configurations). The distribution of pooled AUC is reported rather than selecting the best configuration.

## Reproducibility boundary
All inputs are identified by SHA-256. The exact script, outputs, software versions and run manifest are preserved. If an original raw asset cannot be hosted in GitHub, its cryptographic hash remains the identity anchor and the authors retain the source for audit.
