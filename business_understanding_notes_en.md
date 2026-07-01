# Business Understanding — ABC Multistate Bank Churn (notebook notes)

**Question breakdown** (3 layers, sequence: Descriptive/Diagnostic → Classification → Segmentation → Prescriptive out of scope)

| Layer | Type | Why |
|---|---|---|
| Who is likely to churn | Classification | `churn` is a binary label — supervised, not time-series forecasting |
| Which segment they belong to | Descriptive/Diagnostic | Pivot tables + optional clustering |
| Target retention effectively | Prescriptive (out of scope) | Needs A/B test on offers, next phase |

**Techniques by layer**

Approach: Classification (Supervised Learning)
Question: "Which customers are likely to churn?"
Techniques:
* Logistic regression: baseline, interpretable coefficients, outputs churn probability
* Decision trees: split customers by simple rules (e.g. products_number, active_member)
* Random Forest / Gradient Boosting (XGBoost): ensemble, higher accuracy, gives feature importance for driver analysis
* Support vector machines: boundary-based classifier, optional, less interpretable for business stakeholders
Examples:
* Predicting churn label for each customer_id
* Credit default classification
* Fraud transaction flagging

Approach: Descriptive & Diagnostic Analytics (+ Unsupervised Learning for segmentation)
Question: "What patterns exist, and which segment does each customer belong to?"
Techniques:
* Data aggregation (groupby): churn rate by country, gender, age band, products_number
* Pivot tables: cross-tab of age_band × products_number × country
* Correlation analysis: point-biserial (numeric vs churn), Cramér's V (categorical vs churn)
* Clustering (K-means / hierarchical): data-driven segment discovery on scaled features, without using the churn label
Examples:
* Churn-rate heatmap by segment
* Customer segments by balance level / activity status
* Root-cause pattern of churn concentrated in a specific country × product combination

Approach: Prescriptive Analytics (out of scope for this EDA project — next phase)
Question: "What retention action should we take for each segment?"
Techniques:
* Optimization models: allocate a limited retention budget across segments for max expected retained value
* Simulation: estimate expected impact of different offers before rollout
* A/B testing / decision analysis: validate the causal effect of a retention action per segment before scaling
Examples:
* Personalized retention offer targeting
* Fee-waiver / pricing decision for the high-risk segment
* Prioritizing the outreach list within a fixed budget constraint

**Assumptions**
- No timestamp/snapshot date in data → treat as cross-sectional churn, not a true "next quarter" rolling window.
- "Segment" = customer groups sharing traits linked to churn (not CLV-based).
- 12 columns are the full input set; no transaction/behavior/complaint data available.
- Verified on actual file (`data/raw/bank_customer_churn.csv`, 10,000 rows): churn rate = **20.37%** (2,037/10,000) → confirmed imbalance, handle with class_weight/SMOTE.

**KPIs**
- Churn/retention rate by segment
- Retention campaign ROI (cost vs. value retained)
- Recall@K and Precision@K for targeting efficiency (not just accuracy)

**Feature engineering to-do**
- One-hot encode `country`, `gender`
- Scale `credit_score`, `balance`, `estimated_salary`
- Add `zero_balance` flag (balance = 0)
- Add `balance_to_salary_ratio`
- Handle class imbalance (`class_weight` or SMOTE) if churn < 25%

**EDA to-do**
- Churn rate by `country`, `gender`, age band, `products_number`, `active_member`, `credit_card`
- Pivot: rows = age_band × products_number, cols = country, values = churn_rate
- Correlation: point-biserial (numeric vs churn), Cramér's V (categorical vs churn)

**Segmentation approach**
- Rule-based from pivot table (fast, interpretable)
- K-means/hierarchical clustering on scaled features, no churn label (data-driven), cross-check churn rate per cluster

**Evidence tier**
- Descriptive/diagnostic patterns = observation + hypothesis, not causal
- Feature importance = hypothesis about drivers, not proof
- Causal claims (e.g. "fee waiver reduces churn X%") require A/B/holdout test

**Definition of Done**
- [ ] Question layers + sequence confirmed
- [ ] Assumptions on churn window / segment definition confirmed
- [ ] Feature engineering plan ready for EDA
- [ ] Success KPIs locked (Recall@K/Precision@K, retention ROI)
