# Evaluation Rubric & Self-Assessment (§6)

Grading emphasizes **rigor and clarity of each stage, not accuracy alone**. This sheet maps
every grading criterion to where it is satisfied in the repo, the evidence to produce, its
Definition of Done, and a self-score the team fills before each checkpoint.

**Self-score scale:** 0 = absent · 1 = stub · 2 = working, thin · 3 = rigorous + documented.
Target ≥ 2 by the checkpoint that owns the module; ≥ 3 by final submission.

| # | Criterion | Where (artifact) | Required evidence | Definition of Done | Owner | Status | Score /3 |
|---|---|---|---|---|---|---|---|
| 1 | **Synthetic data quality & realism + complete data dictionary** | `data/synthetic/`, `research/src/m1_*`, `data/data_dictionary.md` | Every synthetic field documented (col, type, unit, range, generation logic); realism justification; reproducible seed; **anti-leakage proof** | Dictionary 100% complete; FK integrity = 100%; no single field perfectly separates churn; `pytest` tripwire `auc<0.99` passes; distribution-plausibility note written | Data Engineer | scaffolded | ☐ |
| 2 | **Depth of EDA + clarity of visualization** | `research/src/m2_eda/`, `research/notebooks/`, `research/outputs/figures/` | ≥5 insights, each labelled **observation / hypothesis / causal-claim**; distributions, outliers, correlations; churn rate by segment; RFM-style viz | Charts honest (sorted categories, masked heatmap triangle, overplotting handled); every insight labelled; short narrative per figure | Data Analyst | stub charts | ☐ |
| 3 | **Soundness of cleaning & feature engineering + documentation** | `research/src/m3_cleaning/`, `research/src/m4_feature_engineering/` | Missing/dupes/inconsistent-category handling; outlier rules (invalid age, negative balance); **before/after counts**; feature rationale; SMOTE; feature selection | Every cleaning decision logged with counts; SMOTE/scaling **fit on train fold only** (no leakage); each engineered feature justified as a testable hypothesis | ML Eng (Classification) | scaffolded | ☐ |
| 4 | **Model choice & metric appropriateness for the business** | `research/src/m5_modeling/`, `research/outputs/metrics/`, `model_card.json` | Baseline→advanced comparison (LogReg/RF/XGBoost); **Recall + AUC-PR primary** (justify vs accuracy under imbalance); threshold by cost; SHAP; segmentation silhouette + named personas | Comparison table; metric choice tied to cost framing (missed churner ≫ false alarm); threshold rationale; ≥4 interpretable personas; churn-by-segment analysis | ML Eng (both) | scaffolded | ☐ |
| 5 | **Working, accessible deployment (live link REQUIRED)** | `development/api/`, `development/app/`, `Dockerfile`, `docker-compose.yml` | Public live link; FastAPI `/health`+`/predict`; Streamlit bank-staff lookup; cloud free tier | Live URL responds on `/health`; `/predict` returns valid response; deployed early (week 6 hello-world); image small, model <100MB | MLOps Lead | code ready · **live link = action** | ☐ |
| 6 | **Functioning monitoring with defined drift/performance triggers** | `development/monitoring/` | PSI per feature + Evidently report; "incoming" drift batch; **explicit retrain trigger rule** | Report renders; trigger rule documented (`PSI>0.2 OR recall drop>10%`); **verified to fire** on a drifted batch | MLOps Lead | ✓ verified | ☐ |
| 7 | **Originality of code (authored by team, no AutoML)** | whole repo, `AUTHORS.md`, `.github/workflows/ci.yml` | Code authored by members; no no-code/AutoML platforms; meaningful git history | `AUTHORS.md` maps modules→members; commit history shows authorship; CI lint/test gate green | Whole team | scaffolded | ☐ |

## How to use this sheet
1. Before each checkpoint, fill the **Score** column honestly and attach the evidence link.
2. Any criterion `< 2` at its owning checkpoint is a **blocker** — fix before submitting the checkpoint.
3. At final submission, every row must be **3** with a concrete artifact link.

## Scoring reminder (what graders reward)
- **Documentation beats accuracy.** A model at AUC 0.78 with a clear cost-based threshold and
  honest limitations outscores a black-box AUC 0.95 with no rationale.
- **Label your claims.** "Older customers churn more" is an *observation*, not a cause — say so.
- **Show your work.** Before/after tables, decision logs, and the data dictionary are graded directly.
