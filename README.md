# Customer Churn Prediction & Segmentation for a Digital Bank

End-to-end Business Analytics group project: from raw data to a monitored, deployed model.
Business question: *"Which customers are likely to churn next quarter, and which segment do
they belong to, so retention can be targeted effectively?"*

## Repository = 3 independent parts

This repo is intentionally split into **three decoupled parts**. Each has its own
`requirements.txt`, its own README, and runs without importing code from the others. They
communicate **only through versioned artifacts** (the contract below), so a team member can
work on one part without the others being finished.

| Part | Modules | Owner (suggested) | Runs independently because… |
|---|---|---|---|
| `research/` | M1–M5 (data gen, EDA, cleaning, features, models) | Data Eng + Data Analyst + 2× ML Eng | Produces model + data artifacts; needs nothing downstream |
| `development/` | M6–M7 (API, app, monitoring) | MLOps Lead | Loads a model artifact from a folder; ships a stub model so it boots with zero research code |
| `report/` | M8 (report + slides) | Whole team | Reads metric/figure files; falls back to placeholders if absent |

```
churn-banking-prediction/
├── data/                     # shared inputs (raw Kaggle + synthetic) — read-only to all parts
│   ├── raw/                  # Kaggle base dataset
│   ├── synthetic/            # generated transactional/behavioral data (M1)
│   ├── processed/            # cleaned + feature tables (M3/M4 output)
│   └── data_dictionary.md    # DELIVERABLE — every synthetic field documented
├── research/                 # PART 1 — Modules 1–5
├── development/              # PART 2 — Modules 6–7
├── report/                   # PART 3 — Module 8
├── docs/research_plan.md     # research questions, hypotheses, timeline, DoD
└── .github/workflows/ci.yml  # lint + test gate
```

## The artifact contract (the only coupling between parts)

Independence is enforced by a small, stable hand-off interface. Change the *content* of
these files freely; do not change their *names/paths* without updating both sides.

| Producer | Artifact | Consumer | Schema |
|---|---|---|---|
| `research/` M5 | `research/outputs/models/churn_model.pkl` | `development/` API | sklearn-compatible `.predict_proba` |
| `research/` M5 | `research/outputs/models/segmentation_model.pkl` | `development/` API | `.predict` → cluster id |
| `research/` M5 | `research/outputs/models/model_card.json` | dev + report | feature list, threshold, metrics |
| `research/` M5 | `research/outputs/metrics/metrics.json` | `report/` | AUC, PR, F1, silhouette, per-segment churn |
| `research/` M2/M5 | `research/outputs/figures/*.png` | `report/` | figures referenced in the report |
| `research/` M4 | `data/processed/features.parquet` | dev monitoring reference | training feature distribution |

To wire research → development, run `development/scripts/sync_model.sh` (copies the 3 model
files into `development/models/`). Until then, development uses a bundled **stub model** so it
boots standalone.

## Quick start (each part is separate)

```bash
# PART 1 — research
cd research && pip install -r requirements.txt && python run_pipeline.py   # M1→M5

# PART 2 — development (works with stub model even if research not run)
cd development && pip install -r requirements.txt && docker compose up

# PART 3 — report
cd report && python build_report.py   # assembles report from metrics/figures
```

## Deliverables map (Section 4 of the announcement)

| Deliverable | Format | Location |
|---|---|---|
| Source code | GitHub repo | this repository |
| Data dictionary | Markdown/Excel | `data/data_dictionary.md` |
| Deployed API + dashboard demo | live link | `development/` (FastAPI + Streamlit) |
| Monitoring dashboard/report | Evidently | `development/monitoring/` |
| Final report + slides | PDF + PPTX | `report/` |

> All code is scaffold/dummy authored by the team. Replace stubs with real implementations.
> No no-code/AutoML platforms — per the coding requirement.

## Grading alignment (Section 6) & milestones (Section 7)

The project is built to be graded on **rigor and clarity per stage, not accuracy alone**.

- **Self-assessment rubric** — every grading criterion mapped to artifact + evidence + DoD +
  self-score: [`docs/evaluation_rubric.md`](docs/evaluation_rubric.md)
- **Submission plan** — milestone dates + per-checkpoint acceptance criteria:
  [`docs/submission_plan.md`](docs/submission_plan.md)
- **Code originality** — authorship + module ownership: [`AUTHORS.md`](AUTHORS.md)

| Checkpoint | Modules | Date (assumed) | Rubric rows |
|---|---|---|---|
| Team formation & topic | — | Fri 03 Jul 2026 | — |
| CP1 data + EDA + cleaning | M1–M3 | Fri 24 Jul 2026 | #1, #2, #3 |
| CP2 features + models | M4–M5 | Fri 07 Aug 2026 | #3, #4 |
| CP3 deployment + monitoring | M6–M7 | Fri 21 Aug 2026 | #5, #6 |
| Final submission & presentation | M8 | Fri 28 Aug 2026 | #1–#7 |

Dates are assumptions (8-week timeline from 30 Jun 2026); replace with the instructor's dates in
`docs/submission_plan.md`. Each grading criterion already has a concrete home in the repo — see
the rubric for the location/evidence/DoD of all seven.
