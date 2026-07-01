# Final Report — Customer Churn Prediction & Segmentation for a Digital Bank

> Template. Replace bracketed/placeholder text. `build_report.py` injects `{{AUC}}`, `{{RECALL}}`,
> `{{F1}}` from `research/outputs/metrics/metrics.json` and copies figures. Export to PDF for submission.

## 1. Executive summary
One paragraph: the business question, the two models built, headline result, and the single most
important retention recommendation. (1 slide / ~150 words.)

## 2. Business problem & KPIs
- Question: which customers churn next quarter, and in which segment?
- KPIs: churn rate, CLV, retention cost. Cost framing: a missed churner ≫ a false alarm.

## 3. Data
- Base: Kaggle bank customer churn. Synthetic: 6-month transactional/behavioral (see
  `data/data_dictionary.md`). Realism + anti-leakage notes summarized here.

## 4. Methods & results
- EDA highlights (observations only — no causal claims). Figures: `figures/`.
- Cleaning & feature engineering decisions (before/after).
- **Classification:** AUC-ROC = {{AUC}}, Recall (churn) = {{RECALL}}, F1 = {{F1}}.
  Model choice + threshold justified by cost framing.
- **Segmentation:** k clusters, silhouette, named personas, churn rate by segment.

## 5. Retention strategy by segment
For each persona: risk level, recommended action (offer / outreach channel), and estimated impact
(qualitative or quantitative). Tie each to CLV / retention cost.

| Segment / persona | Churn rate | Recommended action | Expected impact |
|---|---|---|---|
| Loyal High-Value | … | proactive perks | protect CLV |
| Dormant At-Risk | … | win-back campaign | reduce churn |
| New Explorer | … | onboarding nudges | raise activation |
| Price-Sensitive | … | fee review / bundle | retain margin |

## 6. Monitoring plan
Drift tracked via PSI / Evidently; retrain trigger: any feature PSI > 0.2 OR recall drop > 10%.

## 7. Limitations & future work
Synthetic-data realism, threshold tuning, true label delay, online A/B validation of retention
actions (the only way to make a causal churn-reduction claim).

## 8. Links
- Live demo (API + Streamlit): [insert link]
- Repository: [insert link]
- Monitoring report: `development/monitoring/reports/`
