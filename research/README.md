# Part 1 — Research (Modules 1–5)

Independent package. Turns raw + synthetic data into two models and a metrics file.
Imports nothing from `development/` or `report/`.

## Run

```bash
pip install -r requirements.txt
python run_pipeline.py     # M1 -> M2 -> M3 -> M4 -> M5(A+B)
pytest tests -q            # smoke + anti-leakage guard
```

## Modules

| Module | File | Output |
|---|---|---|
| M1 Data generation | `src/m1_data_generation/generate.py` | validates `data/synthetic/`, FK integrity |
| M2 EDA | `src/m2_eda/eda.py` | figures in `outputs/figures/` |
| M3 Cleaning | `src/m3_cleaning/clean.py` | `data/processed/base_clean.parquet` + decision log |
| M4 Feature engineering | `src/m4_feature_engineering/features.py` | `data/processed/features.parquet` (RFM + trend) |
| M5-A Classification | `src/m5_modeling/train_churn.py` | `churn_model.pkl`, `model_card.json` |
| M5-B Segmentation | `src/m5_modeling/train_segments.py` | `segmentation_model.pkl`, `segments.json` |

## Artifacts produced (the hand-off contract — see root README)

```
research/outputs/models/churn_model.pkl          -> development API
research/outputs/models/segmentation_model.pkl   -> development API
research/outputs/models/model_card.json          -> dev + report
research/outputs/metrics/metrics.json            -> report
research/outputs/figures/*.png                   -> report
data/processed/features.parquet                  -> monitoring reference
```

## Notes (eda-python discipline)
- Every EDA finding is labelled **observation / hypothesis / causal claim** — no causal language off a correlation.
- SMOTE / scaling are fit on the **train fold only** (no leakage).
- The test asserts `auc_roc < 0.99` as an anti-leakage tripwire on synthetic data.
- **DoD:** pipeline runs clean, all 4 contract artifacts present, metrics sane, ≥4 named personas.
