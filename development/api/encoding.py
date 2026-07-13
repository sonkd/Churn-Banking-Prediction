"""Replicates the research v3 feature encoding (notebook §5 cell: engineered cols +
pd.get_dummies with drop_first) for the ONLINE path only. The batch path never needs this -
data/processed/features.parquet is already encoded by research. Keep this in sync with
model_card.json["features"]: the reindex(fill_value=0) guarantees column order and silently
zero-fills any one-hot level not present in the single-row input, which is exactly the
drop_first behaviour at inference time."""
import pandas as pd

AGE_BINS = [17, 29, 39, 49, 59, 100]
AGE_LABELS = ["18-29", "30-39", "40-49", "50-59", "60+"]
CS_BINS = [0, 580, 670, 740, 800, 850]
CS_LABELS = ["poor", "fair", "good", "very_good", "excellent"]


def encode_for_model(raw: dict, feature_list: list[str]) -> pd.DataFrame:
    """raw customer dict (API schema fields) -> 1-row DataFrame with exactly feature_list."""
    df = pd.DataFrame([raw])

    df["zero_balance"] = (df["balance"] == 0).astype(int)
    salary = df["estimated_salary"].replace(0, pd.NA)
    df["balance_to_salary_ratio"] = (df["balance"] / salary).fillna(0).astype(float)
    df["active_and_card"] = (df["active_member"] * df["credit_card"]).astype(int)
    products = df["products_number"].replace(0, pd.NA)
    df["tenure_per_product"] = (df["tenure"] / products).fillna(0).astype(float)
    df["age_band"] = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LABELS)
    df["credit_score_tier"] = pd.cut(df["credit_score"], bins=CS_BINS, labels=CS_LABELS)

    df = pd.get_dummies(df, columns=["country", "gender", "age_band", "credit_score_tier"], dtype=int)
    return df.reindex(columns=feature_list, fill_value=0)


def needs_encoding(card: dict, raw_fields: set[str]) -> bool:
    """True when the model card's feature list is NOT a subset of the raw API fields -
    i.e. the model was trained on encoded/engineered columns (v3+)."""
    features = card.get("features")
    return bool(features) and not set(features) <= raw_fields
