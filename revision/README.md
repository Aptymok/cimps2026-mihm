# CIMPS2026 #724450 · Round 1 Major Revision

This directory is the additive, versioned response to the CIMPS2026 **Accepted with Major Changes** decision for submission 724450.

## Scientific boundary

The revised work is framed as an **operational formalization and reproducible proof-of-concept**, not as universal experimental validation of MIHM. The experiment is restricted to bounded acoustic objects and controlled perturbations. It does not claim direct human-cognitive measurement, multimodal validity, general sociotechnical validity, or superiority over anomaly-detection baselines.

## What changed

- Reconciles the submitted manuscript with the historical implementation and preserves R0 artifacts rather than rewriting them.
- Replaces the ambiguous legacy `Phi` estimator with method-scoped `Phi_S`, defined as robust proximity to a source-specific clean baseline.
- Gives executable definitions for `Fs`, `Di`, `Cs`, `Dcog`, `Er`, and `Vi`; `Dcog` is explicitly only a temporal onset-dispersion proxy in this experiment.
- Retains the original REM618 + `easter_egg` pair as the primary cohort and adds five KXTXR audio objects as a secondary within-corpus robustness cohort.
- Uses nine controlled perturbation conditions across noise, clipping, and dropout, with clean/perturbed ground truth.
- Adds Isolation Forest and One-Class SVM baselines.
- Adds cluster-bootstrap AUC intervals, paired Wilcoxon-Holm tests, bootstrap median-effect intervals, and 900 sensitivity configurations.
- Persists hashes, versions, seeds, scripts, generated results, and the reviewer-compliance matrix.

## Main files

- `CIMPS2026_R1_REVISED_MANUSCRIPT.md` — manuscript source used for the camera-ready package.
- `R1_REVIEW_COMPLIANCE_MATRIX.md` — reviewer requirement → change → evidence → status.
- `MIHM_CIMPS_R1_PROTOCOL.md` — frozen R1 experimental protocol (not represented as preregistration).
- `MIHM_CIMPS_R1_VARIABLE_CONTRACT.json` — operational variable and `Phi_S` contract.
- `experiments/run_r1_extended_experiment.py` — deterministic experimental runner.
- `experiments/analyze_r1_uncertainty.py` — uncertainty/effect analysis.
- `results/` — generated empirical outputs and run manifest.
- `legacy/` — recovered R0 code/results used to explain the original near-0.5000 Phi values.

## Reproduction boundary

The exact source files are identified by SHA-256 in `results/RUN_MANIFEST.json`. Some author-controlled audio assets are not redistributed through GitHub. Missing raw assets must not be silently replaced; the manifest hashes are the identity anchors. Controlled perturbations are generated deterministically by the experimental script.

## Interpretation of results

The pooled MIHM-R1 discrimination AUC is modest and is reported with uncertainty. One-Class SVM performs better in the present task. The revised claim is therefore not detector superiority; it is that the bounded MIHM operationalization is explicit, executable, provenance-preserving, and measurably responsive to several known perturbations while exposing a documented weakness for mild dropout.
