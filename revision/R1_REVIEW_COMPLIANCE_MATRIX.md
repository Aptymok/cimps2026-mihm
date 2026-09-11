# CIMPS2026 724450 - Major Revision Compliance Matrix

| Reviewer requirement | R1 action | Evidence / output | Status |
|---|---|---|---|
| Distinguish proof of concept from experimental validation | Title, abstract, contribution and conclusions reframed as reproducible proof of concept | Revised manuscript Sections I, VII | PASS |
| Formalize Fs, Di, Cs, Dcog, Er, Vi | Six variables receive explicit observable proxies, formulas/scales and extraction procedure | Section III; variable contract; experiment script | PASS |
| Define and justify Phi | Legacy estimator analyzed; new Phi_S is method-scoped baseline proximity with explicit robust normalization | Section III-C/D; baseline_contract.json | PASS |
| Explain identical Phi=0.5000 | Historical code recovered: old estimator was 0.5 minus a small mean RMS first-difference term, mechanically yielding near-0.5 on long signals | Section III-D; legacy artifacts | PASS |
| Additional signals / conditions | Original pair retained; five additional KXTXR objects added as secondary robustness set; 3 perturbation families x 3 severities | Section IV; RUN_MANIFEST.json | PASS (bounded audio only) |
| Ground truth | Clean vs known deterministic/seeded signal transformations explicitly defined | Protocol; Section IV-B | PASS |
| Baselines | Isolation Forest and One-Class SVM trained only on clean baseline windows | Section IV-D; metrics.csv | PASS |
| Statistics / uncertainty | Cluster-bootstrap AUC CI, paired Wilcoxon-Holm, bootstrap median-effect CI, severity correlations | Section V; auc_uncertainty.csv; paired_stats.csv | PASS |
| Sensitivity analysis | +/-20% normalized weights and k=2.5/3/3.5, 900 configurations, no best-case selection | Section V-C; sensitivity.csv | PASS |
| Reproducibility | Source hashes, exact script, versions, seeds, results and manifest persisted | Section VI; RUN_MANIFEST.json | PASS |
| Paper/repository discrepancies | R0 outputs and legacy code preserved; R1 implementation versioned separately; generated tables tied to result CSVs | Section III-D; revision package | PASS |
| Figures cited and ordered | Three figures retained, each cited in body before presentation | Sections III-V | PASS |
| Reduce conceptual redundancy | Ishikawa and redundant conceptual diagrams removed | Revised manuscript | PASS |
| E=g(S,N,V,C) not operational equation | Removed from operational formalization rather than presented as a complete equation | Revised manuscript | PASS |
| Modernize state of art | OpenTelemetry 2026, TimeSeriesBench 2024, MTAD 2024, plus canonical anomaly baselines | Section II | PASS |
| Clarify DevOps/DevSecOps/AIOps role | Recast as engineering antecedents, not mathematical foundations of MIHM | Section II | PASS |
| Limit sociotechnical/multimodal claims | Explicitly moved to future work; present evidence is bounded acoustic | Abstract, Sections I, VII, VIII | PASS |
| Cognitive terminology must be measurable | Dcog explicitly demoted to a historical symbol for temporal onset dispersion proxy; no cognitive inference | Section III-B, VII | PASS |
