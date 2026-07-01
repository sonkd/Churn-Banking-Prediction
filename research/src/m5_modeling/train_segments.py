"""Module 5 Branch B — Behavioral segmentation. K-Means on RFM/behavioral features;
assign interpretable persona names; analyze churn rate by segment (RQ2/RQ3)."""
import json, numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from src.common.io import load_config, rpath, save_model, save_json

PERSONAS = {0: "Loyal High-Value", 1: "Dormant At-Risk", 2: "New Explorer", 3: "Price-Sensitive"}

def train():
    cfg = load_config()
    df = pd.read_parquet(rpath("../data/processed/features.parquet"))
    feats = cfg["segmentation"]["features"]
    X = df[feats].fillna(0)
    k = cfg["segmentation"]["k"]
    model = Pipeline([("scale", StandardScaler()),
                      ("km", KMeans(n_clusters=k, n_init=10, random_state=cfg["seed"]))])
    labels = model.fit_predict(X)
    sil = float(silhouette_score(model.named_steps["scale"].transform(X), labels))
    df["segment"] = labels
    by_seg = df.groupby("segment")[cfg["target"]].mean().round(3).to_dict()
    save_model(model, cfg["paths"]["models"] + "/segmentation_model.pkl")
    save_json({"k": k, "silhouette": sil, "personas": PERSONAS,
               "churn_rate_by_segment": by_seg, "features": feats},
              cfg["paths"]["metrics"] + "/segments.json")
    print(f"[M5-B] k={k} silhouette={sil:.3f} churn_by_segment={by_seg}")
    return sil, by_seg

if __name__ == "__main__":
    train()
