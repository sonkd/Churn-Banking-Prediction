# Part 2 — Development (Modules 6–7)

Independent service package: serves the churn model as an API + Streamlit demo (M6) and
monitors drift (M7). **Boots standalone** with a bundled stub model — no research code needed.

## Run

```bash
pip install -r requirements.txt

# 1) (optional) wire the real model from research:
bash scripts/sync_model.sh         # copies churn/segment .pkl + model_card.json into models/

# 2) serve API + app
docker compose up                  # API :8000, Streamlit :8501
# or locally:
uvicorn api.main:app --reload      # then: streamlit run app/streamlit_app.py

# 3) monitoring (M7)
python monitoring/generate_drift_batch.py   # make an 'incoming' batch with drift
python monitoring/drift_report.py           # PSI + Evidently report + retrain trigger

pytest tests -q                    # API smoke test (uses stub model)
```

## Endpoints (M6)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness |
| GET | `/ready` | readiness — is a model loaded? reports `stub` vs `research` |
| POST | `/predict` | churn probability + label + segment |

## Monitoring (M7)
- `generate_drift_batch.py` synthesizes a "next quarter" batch with **intentional drift** (lower
  engagement, more complaints, cohort age shift) — because real incoming data doesn't exist yet.
- `drift_report.py` computes **PSI per feature**, writes an Evidently HTML report when available,
  and emits a **retrain trigger**: `retrain if any feature PSI > 0.2 OR recall drops > 10%`.

## How it stays independent
The API loads `models/churn_model.pkl` if present; otherwise `api/model_loader.StubModel` returns
deterministic predictions. So this part runs, tests pass, and the demo works **before research is
finished**. The only coupling is the file contract in the root README.

## Deploy (free tier — live link required)
- Hugging Face Spaces (Docker) or Render free web service. Keep the image small; model <100MB.
- Deploy a hello-world early (week 6) to surface free-tier limits before the deadline.
- **DoD:** public live link responds on `/health`; `/predict` returns a valid response; drift
  report renders with a defined trigger.
