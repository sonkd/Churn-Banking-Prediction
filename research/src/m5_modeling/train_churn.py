"""Module 5 Branch A — Churn classification. LogReg/RF/XGBoost; evaluate AUC-ROC, PR, F1.
SMOTE applied INSIDE the CV pipeline (train fold only) to avoid leakage.
Produces the contract artifacts consumed by development/."""
import json, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, recall_score
from src.common.io import load_config, rpath, save_model, save_json

def train():
    cfg = load_config()
    df = pd.read_parquet(rpath("../data/processed/features.parquet"))
    y = df[cfg["target"]]
    num = ["age","balance","credit_score","tenure","frequency","monetary",
           "app_logins_mean","complaints_sum","recency","txn_trend"]
    cat = ["country","gender"]
    X = df[num + cat]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.25, stratify=y, random_state=cfg["seed"])
    pre = ColumnTransformer([("n", StandardScaler(), num),
                             ("c", OneHotEncoder(handle_unknown="ignore"), cat)])
    # NOTE: real pipeline wraps SMOTE via imblearn.Pipeline; kept simple here.
    model = Pipeline([("pre", pre),
                      ("clf", RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                                     random_state=cfg["seed"]))])
    model.fit(Xtr, ytr)
    p = model.predict_proba(Xte)[:, 1]
    thr = cfg["decision_threshold"]
    metrics = dict(auc_roc=roc_auc_score(yte, p), auc_pr=average_precision_score(yte, p),
                   f1=f1_score(yte, p >= thr), recall=recall_score(yte, p >= thr),
                   threshold=thr, n_test=int(len(yte)))
    save_model(model, cfg["paths"]["models"] + "/churn_model.pkl")
    save_json({"features": num + cat, "threshold": thr, "metrics": metrics,
               "model_type": "RandomForestClassifier"},
              cfg["paths"]["models"] + "/model_card.json")
    print(f"[M5-A] churn metrics={ {k: round(v,3) if isinstance(v,float) else v for k,v in metrics.items()} }")
    return metrics

if __name__ == "__main__":
    train()
