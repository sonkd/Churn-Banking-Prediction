# CLAUDE.md

Guidance for Claude Code (and any contributor) working in this repository.

## What this repo is

`churn-banking-prediction` — predict which digital-bank customers will churn next quarter and
which behavioral segment they belong to, so retention can be targeted. See root `README.md` for
the business framing and `docs/mlops_fti_task_plan.md` for the MLOps restructuring plan (FTI:
Feature / Training / Inference) this codebase is being evolved towards.

## The 3-part independence rule

This repo is split into **three decoupled parts**. This is a hard rule, not a suggestion:

| Part | Contains | Must NOT do |
|---|---|---|
| `research/` | M1–M5: data generation, EDA, cleaning, feature engineering, modeling | Import anything from `development/` or `report/` |
| `development/` | M6–M7: FastAPI, Streamlit, batch prediction, monitoring | Import anything from `research/` (load models via files, never via `import research...`) |
| `report/` | M8: final report + slides | Import anything from `research/` or `development/` (reads metric/figure files only) |

Each part has its **own `requirements.txt`** and runs standalone. `development/` boots with a
bundled stub model (`api/model_loader.StubModel`) even if `research/` has never been run — never
break that fallback.

## The artifact contract (the only coupling between parts)

Parts communicate **only** through files at fixed paths. Never rename/move these without updating
every consumer; freely change their *content*.

| Producer | Artifact | Consumer | Schema |
|---|---|---|---|
| `research/` M5 | `research/outputs/models/churn_model.pkl` | `development/` API | sklearn-compatible `.predict_proba` |
| `research/` M5 | `research/outputs/models/segmentation_model.pkl` | `development/` API | `.predict` → cluster id |
| `research/` M5 | `research/outputs/models/model_card.json` | `development/` + `report/` | feature list, threshold, metrics |
| `research/` M5 | `research/outputs/metrics/metrics.json` | `report/` | AUC, PR, F1, silhouette, per-segment churn |
| `research/` M2/M5 | `research/outputs/figures/*.png` | `report/` | figures referenced in the report |
| `research/` M4 | `data/processed/features.parquet` | `development/` monitoring reference | training feature distribution |
| `research/` M1/M4 | `data/processed/feature_metadata.json` | `development/` batch + monitoring | schema, feature list, version, created_at, row hash (added by P1) |

Wire research → development with `development/scripts/sync_model.sh` (copies the 3 model files
into `development/models/`).

## Style

- Lint with `ruff` (listed in `research/requirements.txt`; add to `development/requirements.txt`
  if missing). Run `ruff check .` inside the part you're editing.
- Tests are `pytest`, one `tests/` dir per part. A change to `research/` must keep
  `research/tests/test_pipeline.py` passing (it runs the full pipeline and checks the artifact
  contract + an anti-leakage guard: churn AUC must stay `< 0.99`). A change to `development/`
  must keep `development/tests/test_api.py` passing (boots the API with the stub model).
- Config lives in `research/config/config.yaml` (paths, seed, decision threshold, segmentation
  features) — read via `src/common/io.load_config()`. Don't hardcode paths that already have a
  config key.
- Secrets (e.g. `WANDB_API_KEY`) go through environment variables / `.env`, never hardcoded.
  `development/.env.default` documents the expected keys with safe local defaults.
