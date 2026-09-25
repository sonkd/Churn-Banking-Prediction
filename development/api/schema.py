from pydantic import BaseModel, Field

class Customer(BaseModel):
    age: int = Field(40, ge=18, le=100)
    balance: float = 50000
    credit_score: int = Field(650, ge=300, le=850)
    tenure: int = 3
    products_number: int = Field(1, ge=0, le=4)
    credit_card: int = Field(1, ge=0, le=1)
    active_member: int = Field(1, ge=0, le=1)
    estimated_salary: float = 100000
    frequency: float = 60
    monetary: float = 4000
    app_logins_mean: float = 10
    complaints_sum: float = 1
    recency: float = 1
    txn_trend: float = 0.0
    country: str = "France"
    gender: str = "Male"

class Prediction(BaseModel):
    churn_probability: float
    churn_label: int
    segment: int | None = None
    threshold: float
    model_source: str

class BatchPrediction(BaseModel):
    """One row of a batch-scored bucket/predictions/latest.parquet (written by
    development/batch/predict.py, Pipeline #3)."""
    customer_id: int
    churn_proba: float
    churn_label: int
    segment: int
    model_version: str
    scored_at: str
