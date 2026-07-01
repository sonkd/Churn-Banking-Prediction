# Submission Plan & Milestones (§7)

**Assumptions (adjust to the instructor's real dates):** 8-week timeline starting the week of
**30 Jun 2026**; checkpoints fall on Fridays. If the instructor inserts different dates, update
only the table below — nothing else depends on these values.

## Milestones

| # | Milestone | Modules | Date (assumed) | Week |
|---|---|---|---|---|
| 1 | Team formation & topic confirmation | — | **Fri 03 Jul 2026** | 0 |
| 2 | Checkpoint 1 — data + EDA + cleaning | M1–M3 | **Fri 24 Jul 2026** | 3 |
| 3 | Checkpoint 2 — features + models | M4–M5 | **Fri 07 Aug 2026** | 5 |
| 4 | Checkpoint 3 — deployment + monitoring | M6–M7 | **Fri 21 Aug 2026** | 7 |
| 5 | Final submission & presentation | M8 | **Fri 28 Aug 2026** | 8 |

## Per-checkpoint acceptance (what must be true to pass the checkpoint)

### Checkpoint 1 — M1–M3 (data + EDA + cleaning) · rubric #1, #2, #3
**Required artifacts**
- `data/synthetic/` generated; `data/data_dictionary.md` complete (every field documented).
- `research/src/m2_eda/` + `research/outputs/figures/` with ≥5 labelled insights.
- `research/src/m3_cleaning/` with a before/after decision log; `data/processed/base_clean.parquet`.

**Acceptance criteria**
- FK integrity 100%; anti-leakage tripwire `auc<0.99` passes.
- Each EDA insight labelled observation / hypothesis / causal-claim.
- Every cleaning decision logged with row counts.
- Rubric rows #1–#3 each self-scored ≥ 2.

### Checkpoint 2 — M4–M5 (features + models) · rubric #3, #4
**Required artifacts**
- `data/processed/features.parquet` (RFM + behavioral trend).
- Model comparison table (LogReg/RF/XGBoost); `churn_model.pkl`, `model_card.json`, `metrics.json`.
- `segmentation_model.pkl`, `segments.json` with ≥4 named personas + churn-by-segment.

**Acceptance criteria**
- SMOTE/scaling fit on train fold only (no leakage).
- Primary metrics = Recall + AUC-PR, with cost-based threshold justified.
- SHAP / feature importance produced.
- Rubric rows #3–#4 self-scored ≥ 2.

### Checkpoint 3 — M6–M7 (deployment + monitoring) · rubric #5, #6
**Required artifacts**
- **Public live link** (Hugging Face Spaces / Render / Streamlit Cloud) — API + Streamlit lookup.
- `development/monitoring/` drift report (Evidently/PSI) + documented retrain trigger.

**Acceptance criteria**
- Live URL responds on `/health`; `/predict` returns a valid response.
- Drift monitor verified to **fire** on a drifted batch; trigger rule written.
- Rubric rows #5–#6 self-scored ≥ 2 (deployment must be live, not local).

### Final — M8 · rubric #1–#7
**Required artifacts**
- `report/final_report.md` → **PDF**; `report/slides.pptx` (**PPTX**).
- Per-segment retention strategy; limitations + causal-validation note.
- `AUTHORS.md`; green CI.

**Acceptance criteria**
- Every rubric row self-scored **3** with an evidence link.
- Live demo (or recorded) presented to class.

## Suggested ownership (RACI-lite)

| Milestone | Accountable | Support |
|---|---|---|
| CP1 data + EDA + cleaning | Data Engineer | Data Analyst |
| CP2 features + models | ML Eng (Classification) | ML Eng (Segmentation) |
| CP3 deployment + monitoring | MLOps Lead | ML Engs |
| Final report + presentation | Whole team | — |

> Definition of Done (project): all four checkpoints accepted, a live deployment, a firing drift
> monitor, and a report translating segment findings into targeted retention actions.
