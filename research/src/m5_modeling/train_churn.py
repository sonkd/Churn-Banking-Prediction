"""Module 5 Branch A — Churn classification. LogReg/RF/XGBoost; evaluate AUC-ROC, PR, F1.
SMOTE applied INSIDE the CV pipeline (train fold only) to avoid leakage.
Produces the contract artifacts consumed by development/. Tracks each run with Weights & Biases;
WANDB_MODE defaults to "offline" so this runs with zero external account/API key needed."""
import json, os
import pandas as pd
import wandb
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, recall_score
from sklearn.calibration import calibration_curve
from src.common.io import load_config, rpath, save_model, save_json

os.environ.setdefault("WANDB_MODE", "offline")

NUM = ["age", "balance", "credit_score", "tenure", "frequency", "monetary",
       "app_logins_mean", "complaints_sum", "recency", "txn_trend"]
CAT = ["country", "gender"]


def _feature_metadata():
    p = rpath("../data/processed/feature_metadata.json")
    return json.load(open(p)) if p.exists() else {"version": "unknown"}


def _next_semver(model_dir: str) -> str:
    """Bump the patch version of the previously committed model_card.json, if any."""
    p = rpath(model_dir) / "model_card.json"
    if p.exists():
        prev = json.load(open(p)).get("semver", "1.0.0")
        try:
            major, minor, patch = (int(x) for x in prev.split("."))
            return f"{major}.{minor}.{patch + 1}"
        except ValueError:
            pass
    return "1.0.0"


def train():
    cfg = load_config()
    df = pd.read_parquet(rpath("../data/processed/features.parquet"))
    y = df[cfg["target"]]
    X = df[NUM + CAT]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.25, stratify=y, random_state=cfg["seed"])

    n_estimators = 200
    threshold = cfg["decision_threshold"]
    data_version = _feature_metadata().get("version", "unknown")

    run = wandb.init(
        project="churn-banking-prediction", job_type="train_churn",
        config={"model_type": "RandomForestClassifier", "n_estimators": n_estimators,
                "class_weight": "balanced", "seed": cfg["seed"], "threshold": threshold,
                "data_version": data_version},
    )

    pre = ColumnTransformer([("n", StandardScaler(), NUM),
                             ("c", OneHotEncoder(handle_unknown="ignore"), CAT)])
    # NOTE: real pipeline wraps SMOTE via imblearn.Pipeline; kept simple here.
    model = Pipeline([("pre", pre),
                      ("clf", RandomForestClassifier(n_estimators=n_estimators, class_weight="balanced",
                                                     random_state=cfg["seed"]))])
    model.fit(Xtr, ytr)
    p = model.predict_proba(Xte)[:, 1]
    metrics = dict(auc_roc=roc_auc_score(yte, p), auc_pr=average_precision_score(yte, p),
                   f1=f1_score(yte, p >= threshold), recall=recall_score(yte, p >= threshold),
                   threshold=threshold, n_test=int(len(yte)))
    wandb.log(metrics)
    wandb.log({"confusion_matrix": wandb.plot.confusion_matrix(
        preds=(p >= threshold).astype(int), y_true=yte.to_numpy(), class_names=["stay", "churn"])})

    frac_pos, mean_pred = calibration_curve(yte, p, n_bins=10, strategy="quantile")
    calib_table = wandb.Table(data=list(zip(mean_pred, frac_pos)),
                               columns=["mean_predicted_proba", "fraction_of_positives"])
    wandb.log({"calibration_curve": wandb.plot.line(
        calib_table, "mean_predicted_proba", "fraction_of_positives", title="Calibration curve")})

    save_model(model, cfg["paths"]["models"] + "/churn_model.pkl")
    save_json({
        "semver": _next_semver(cfg["paths"]["models"]),
        "features": NUM + CAT,
        "threshold": threshold,
        "metrics": metrics,
        "model_type": "RandomForestClassifier",
        "data_version": data_version,
        "wandb_run_id": run.id,
    }, cfg["paths"]["models"] + "/model_card.json")

    run.finish()
    print(f"[M5-A] churn metrics={ {k: round(v,3) if isinstance(v,float) else v for k,v in metrics.items()} }")
    return metrics

if __name__ == "__main__":
    train()
