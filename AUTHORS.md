# Authors & Code Originality (§6 — Originality of code)

All code in this repository is authored by the team members below. **No no-code / AutoML
platforms** were used; models are implemented with open-source libraries (scikit-learn, XGBoost,
imbalanced-learn) and team-written code.

## Team & module ownership

| Member | Role | Primary modules / files |
|---|---|---|
| [Name 1] | Data Engineer | M1 data generation, data dictionary, M3 cleaning |
| [Name 2] | Data Analyst | M2 EDA + visualization |
| [Name 3] | ML Engineer — Classification | M4 feature engineering, M5-A churn model |
| [Name 4] | ML Engineer — Segmentation | M5-B clustering, persona definition |
| [Name 5] | MLOps Lead | M6 deployment, M7 monitoring (may combine for 4-person teams) |

## Originality evidence
- Git commit history shows incremental, attributable authorship per member.
- CI (`.github/workflows/ci.yml`) runs lint + tests on every push/PR.
- Third-party libraries are declared in each part's `requirements.txt`; only library *usage*,
  not generated/AutoML code, is external.
- Any external snippet adapted is cited inline in the source file.

> Fill in real names before submission. Keep commits attributed to the actual author.
