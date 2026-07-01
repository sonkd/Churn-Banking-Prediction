# Data Dictionary

Per the announcement (§2), **every synthetically generated field** must document: column,
type, unit, valid range, and the generation logic / business assumption. Base (Kaggle) fields
are documented for completeness.

## 1. Base dataset — `data/raw/bank_customer_churn.csv` (source: Kaggle)

| Column | Type | Unit | Valid range | Notes |
|---|---|---|---|---|
| customer_id | int | id | ≥100000 | Primary key, surrogate |
| credit_score | int | score | 350–850 | — |
| country | category | — | France/Germany/Spain | — |
| gender | category | — | Male/Female | — |
| age | int | years | 18–92 | — |
| tenure | int | years | 0–10 | Years as customer |
| balance | float | currency | ≥0 | 0 allowed (no-balance accounts) |
| products_number | int | count | 1–4 | # of bank products held |
| credit_card | int | bool | 0/1 | Has credit card |
| active_member | int | bool | 0/1 | Activity flag |
| estimated_salary | float | currency | 10000–200000 | — |
| churn | int | bool | 0/1 | **Target.** 1 = churned |

## 2. Synthetic dataset — `data/synthetic/transactions_monthly.csv` (generated, Module 1)

Grain: **one row per customer per month** (6 monthly snapshots).

| Column | Type | Unit | Valid range | Generation logic / business assumption |
|---|---|---|---|---|
| customer_id | int | id | matches base | FK to base; ensures join integrity |
| month | int | month idx | 1–6 | Relative month (1 = oldest snapshot) |
| txn_count | int | count | ≥0 | Poisson(λ); λ higher for active members. **Churners trend down ~8%/month** (noisy ground-truth) |
| txn_amount | float | currency | ≥0 | txn_count × U(20,150); proxy for monetary value (RFM-M) |
| app_logins | int | count | ≥0 | Poisson(12 × decline); engagement proxy |
| complaints | int | count | ≥0 | Poisson(0.4 + 0.5·churn); churners complain slightly more |
| channel_atm | int | bool | 0/1 | Bernoulli(0.4); channel-usage flag |
| channel_mobile | int | bool | 0/1 | Bernoulli(0.7); digital adoption proxy |
| channel_branch | int | bool | 0/1 | Bernoulli(0.2); offline reliance proxy |

### Realism & anti-leakage notes (graded — §6)
- The churn signal is injected **with noise** (random decline factor, Poisson jitter) so the
  relationship is *learnable but not deterministic*. Avoids the classic "AUC≈0.99" leakage trap.
- The generation rule (`decline = 1 - 0.08·month` for churners) is **documented but NOT used as
  a feature** — only its downstream effects (txn trend, login drop) are available to the model.
- **Definition of Done (M1):** join key 100% valid; no field perfectly separates churn; ranges
  match this table; reviewer can reproduce with the fixed seed in `m1_data_generation`.
