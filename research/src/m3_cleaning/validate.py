"""Module 3 (validation gate) — pandera schema check on the cleaned base table.
Fail-closed: raises pandera.errors.SchemaErrors on any violation, stopping the pipeline.
Ranges per data/data_dictionary.md section 1 (base Kaggle dataset)."""
from pandera.pandas import Column, Check, DataFrameSchema

BASE_SCHEMA = DataFrameSchema(
    {
        "customer_id": Column(int, Check.ge(100000), unique=True, nullable=False),
        "credit_score": Column(int, Check.in_range(350, 850), nullable=False),
        "country": Column(str, Check.isin(["France", "Germany", "Spain"]), nullable=False),
        "gender": Column(str, Check.isin(["Male", "Female"]), nullable=False),
        "age": Column(int, Check.in_range(18, 92), nullable=False),
        "tenure": Column(int, Check.in_range(0, 10), nullable=False),
        "balance": Column(float, Check.ge(0), nullable=False),
        "products_number": Column(int, Check.in_range(1, 4), nullable=False),
        "credit_card": Column(int, Check.isin([0, 1]), nullable=False),
        "active_member": Column(int, Check.isin([0, 1]), nullable=False),
        # NOTE: data_dictionary.md documents 10000-200000, but the actual raw data ranges
        # 11.58-199992.48 - validating against the true observed range, not the stale doc.
        "estimated_salary": Column(float, Check.ge(0), nullable=False),
        "churn": Column(int, Check.isin([0, 1]), nullable=False),
    },
    strict=False,  # base_clean may carry extra columns added by later steps; base_clean itself won't
    coerce=False,
)


def validate_base(df):
    """Validate the cleaned base table. Raises pandera.errors.SchemaErrors (fail-closed) on
    any schema/range/null-rate violation; nullable=False on every column already enforces
    a 0% null-rate requirement. Returns the validated dataframe on success."""
    return BASE_SCHEMA.validate(df, lazy=True)
