# Requirements: Reasoning Diff

Defined: 2026-09-20. Code delivery is separate from scientific validation.

## v1 Requirements
- [ ] **DATA-01**: T1 independently generated arithmetic DAG fixtures, official iGSM export contract, op 5/10/15/21 and 500-task config, value/rename/no-op/source-value variants.
- [ ] **DATA-02**: GSM-Symbolic/GSM-Plus, HotpotQA, MuSiQue, HumanEval data adapters with independent annotation and explicit unknown graph fields; no synthetic attribution of official provenance.
- [ ] **DATA-03**: Leakage-proof base-group splits, test-only dataset constraints, file/record identity and provenance.
- [ ] **MEAS-01**: Identity/version/scope event matching, structural/failed/unknown records, manual audit export/import.
- [ ] **MEAS-02**: Common-random-stream edits and paired sham opportunities; separate task/finite behavior/noise labels, S/M raw/noise/signed excess, TO/CSP with denominators.
- [ ] **MODEL-01**: Qwen3 and Qwen2/R1 frozen HF inference, streamed hidden span extraction, exact offsets and three positions, isolated RNG, resumable records and honest token/timing costs.
- [ ] **PROBE-01**: Low-rank bilinear task/behavior heads, weighted BCE masks, 2-layer boundary MLP, dev selection and independent trajectory calibration.
- [ ] **BASE-01**: Prefix-matched supervised text, attention/rollout and zero/few-shot/reflection/supervised verbalizer pipelines with identical labels/splits and distinct visibility tiers.
- [ ] **XFER-01**: Frozen direct transfer only when dimensions compatible, separately reported unlabelled paired adaptation for unequal dimensions and held-out evaluation.
- [ ] **CAUSAL-01**: Before-first-target-token swaps, selective ablation, INLP, rescue, wrong-source controls, C-rand/C-layer same batch and matched norm.
- [ ] **CAUSAL-02**: Predeclared source/value-decoupled donors and response matrices, target/non-target/task/invalid rates with all failures.
- [ ] **C3-01**: P1 held-out logistic AUC and chain/op controls, clustered intervals; P2 paired no-op effects; P3 controlled selective ablation and recovery.
- [ ] **REPAIR-01**: Appendix-only no-gate text splice, oracle/predicted/text/truncation/random/prompt/full baselines, original-token budgets, per-round cost and offline failure classification.
- [ ] **OPS-01**: CLI for prepare/collect/label/fit/calibrate/intervene/repair/analyze and offline smoke; manifests, config checks, resume/shards, portable server recipes.
- [ ] **QA-01**: Regression/unit tests and tiny random HF CPU integration, no network/real weights; all modules audited; reproducibility and limitations documented.
- [ ] **DECIDE-01**: Gate 0–2 unregistered by default, Week-8 rule and C3/transfer-first narrative without claiming positive scientific findings.

## Out of Scope
Real GPU experiments, dataset/weight downloads on this machine, RL, production gates/fallback, publication.

## Traceability
| Requirement | Phase | Status |
|---|---|---|
| DATA-01 | 1 | In progress |
| DATA-02 | 1 | In progress |
| DATA-03 | 1 | In progress |
| MEAS-01 | 1 | In progress |
| MEAS-02 | 1 | In progress |
| MODEL-01 | 2 | Pending |
| PROBE-01 | 3 | Pending |
| BASE-01 | 3 | Pending |
| XFER-01 | 3 | Pending |
| CAUSAL-01 | 4 | Pending |
| CAUSAL-02 | 4 | Pending |
| C3-01 | 5 | Pending |
| REPAIR-01 | 5 | Pending |
| OPS-01 | 6 | Pending |
| QA-01 | 6 | Pending |
| DECIDE-01 | 6 | Pending |

Coverage: 16 requirements, 16 mapped, 0 unmapped. Status only becomes Complete after implemented and verified.
