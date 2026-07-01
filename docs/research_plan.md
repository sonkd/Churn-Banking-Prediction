# Research Plan (1-pager)

**Project:** Customer Churn Prediction & Segmentation — Digital Bank
**Decision it informs:** Where to spend retention budget — which customers to target and with
what offer per segment.

## Research questions & hypotheses

| # | Question | Hypothesis | Validation |
|---|---|---|---|
| RQ1 | Which behavioral signals predict churn best? | Declining txn trend + login drop beat demographics | SHAP; ΔAUC with/without behavioral block |
| RQ2 | How many natural behavioral segments exist? | 4–5 RFM clusters differ in churn rate | Silhouette; chi-square churn×cluster |
| RQ3 | Does segment improve the churn model? | Adding segment feature raises F1 | Held-out A/B: with vs without segment |
| RQ4 | Is the model stable under drift? | PSI>0.2 on a key feature degrades recall | Simulated drift batch + Evidently |

**Discipline:** label every finding *observation → hypothesis → causal claim*. EDA yields
associations only; no "X drives churn" in the report without an experiment.

## Metrics
- **Model:** Recall (churn class) + AUC-PR primary; AUC-ROC, F1 secondary. Accuracy is not used
  (class imbalance). Segmentation: silhouette + business interpretability.
- **Business KPI:** churn rate, CLV, retention cost; capture rate of top-20% risk decile (lift).
- **Cost framing:** missing a churner ≫ a false alarm → optimize threshold for recall.

## Timeline (8 weeks → 4 checkpoints)

| Phase | Weeks | Modules | Definition of Done |
|---|---|---|---|
| Foundation | 1–3 | M1–M3 | Data dictionary complete; ≥5 EDA insights; before/after cleaning log |
| Modeling | 4–5 | M4–M5 | Model comparison table; SHAP; ≥4 named personas; RQ1–RQ3 answered |
| Productionize | 6–7 | M6–M7 | Live link works; Evidently report; retrain triggers defined |
| Synthesis | 8 | M8 | Per-segment retention strategy; PDF+PPTX; recorded demo |

## Top risks → mitigation
1. **Synthetic data leakage** → inject noise; keep generation rule out of features; flag any "too-perfect" feature.
2. **Free-tier deploy fails/sleeps** → deploy a hello-world in week 6; keep model <100MB.
3. **No drift data for M7** → plan a "next-month" batch generator from M1.
4. **SMOTE leakage** → resample inside CV / train fold only.

## Definition of Done (project)
Two working models, a live deployment with a lookup UI, a functioning drift monitor with
triggers, and a report translating segment-level findings into targeted retention actions.
