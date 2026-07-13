"""Module 6 — Streamlit dashboard: 2 pages (Predictions, Monitoring). Talks ONLY to the
FastAPI backend via API_URL - never reads the bucket or model files directly - so the UI
stays decoupled from how/where predictions and metrics are actually stored."""
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Churn Dashboard", page_icon="🏦", layout="wide")

# RFM segment labels (K-Means cluster id -> business name). Cluster ids are arbitrary:
# re-verify this mapping against the churn-rate-by-cluster profile whenever the
# segmentation model is retrained ("At Risk" must stay the highest-churn cluster).
SEGMENT_LABELS = {0: "Champion", 1: "Loyalist", 2: "Promising", 3: "At Risk"}


def segment_name(seg_id: int) -> str:
    return SEGMENT_LABELS.get(int(seg_id), f"Segment {seg_id}")


def api_get(path: str, **params):
    """Returns (data, error_message). Never raises - callers just check `error_message`."""
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=10)
        if r.status_code == 404:
            return None, r.json().get("detail", "not found")
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"API not reachable at {API}: {e}"


def predictions_page():
    st.header("📉 Predictions — retention risk")
    segments, err = api_get("/segments")
    if err:
        st.error(err)
        return

    col_a, col_b = st.columns([1, 2])
    seg_options = {segment_name(s): s for s in segments}          # label -> id
    segment_choice = col_a.selectbox("Segment", ["All"] + list(seg_options))
    top_k = col_b.slider("Top-k at-risk customers", min_value=5, max_value=500, value=50, step=5)

    params = {"top_k": top_k}
    if segment_choice != "All":
        params["segment"] = seg_options[segment_choice]
    rows, err = api_get("/predictions", **params)
    if err:
        st.error(err)
        return

    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No predictions in the bucket yet — run `make batch-predict`.")
        return
    df.insert(df.columns.get_loc("segment") + 1, "segment_label", df["segment"].map(segment_name))

    c1, c2, c3 = st.columns(3)
    c1.metric("Customers shown", len(df))
    c2.metric("Avg churn probability", f"{df['churn_proba'].mean():.1%}")
    c3.metric("Model version", df["model_version"].iloc[0])

    st.subheader("Churn probability distribution")
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.hist(df["churn_proba"], bins=20, color="#C44E52")
    ax.set_xlabel("churn probability"); ax.set_ylabel("customers")
    st.pyplot(fig)

    st.subheader(f"Top {len(df)} at-risk customers")
    st.dataframe(df, width="stretch")
    st.download_button("⬇️ Export CSV for retention team", df.to_csv(index=False),
                        file_name="retention_list.csv", mime="text/csv")


def monitoring_page():
    st.header("📈 Monitoring — data drift")
    metrics, err = api_get("/monitoring/metrics")
    if err:
        st.warning(err)
        return

    psi = metrics.get("psi", {})
    trigger = bool(metrics.get("retrain_trigger", False))
    drifted = metrics.get("drifted_features", [])

    if trigger:
        st.error(f"⚠️ Retrain trigger ACTIVE — drifted features: {', '.join(drifted) or '—'}")
    else:
        st.success("✅ No retrain trigger — all features within the PSI threshold")

    if psi:
        st.subheader("PSI per feature (threshold = 0.2)")
        fig, ax = plt.subplots(figsize=(8, 3.5))
        colors = ["#C44E52" if v > 0.2 else "#4C72B0" for v in psi.values()]
        ax.bar(list(psi.keys()), list(psi.values()), color=colors)
        ax.axhline(0.2, color="black", linestyle="--", linewidth=1, label="drift threshold (0.2)")
        ax.set_ylabel("PSI"); ax.legend()
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.info("No per-feature PSI in the latest monitoring run.")

    scored_at = metrics.get("checked_at") or metrics.get("scored_at")
    if scored_at:
        st.caption(f"Last batch checked: {scored_at}")

    # ---- Prediction drift: model quality per batch run over time ----
    st.subheader("Prediction drift — accuracy over time")
    history, err = api_get("/monitoring/history")
    if err:
        st.info(err)
        return
    hist = pd.DataFrame(history)
    if len(hist) < 2:
        st.info("Need at least 2 batch runs to draw a trend — run `make batch-predict` again later.")
        st.dataframe(hist, width="stretch")
        return

    hist["scored_at"] = pd.to_datetime(hist["scored_at"])
    hist = hist.sort_values("scored_at")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.5))
    for col, color, label in [("accuracy", "#4C72B0", "accuracy"),
                              ("auc_roc", "#55A868", "AUC-ROC"),
                              ("recall", "#DD8452", "recall")]:
        if col in hist.columns:
            ax1.plot(hist["scored_at"], hist[col], marker="o", color=color, label=label)
    ax1.set_title("Model quality per batch run")
    ax1.set_ylim(0, 1.05); ax1.legend(); ax1.grid(True, linestyle=":", alpha=0.5)

    ax2.plot(hist["scored_at"], hist["mean_proba"], marker="o", color="#C44E52", label="mean churn proba")
    if "share_flagged" in hist.columns:
        ax2.plot(hist["scored_at"], hist["share_flagged"], marker="s", linestyle="--",
                 color="#8172B2", label="share flagged")
    ax2.set_title("Score distribution per batch run")
    ax2.legend(); ax2.grid(True, linestyle=":", alpha=0.5)
    for ax in (ax1, ax2):
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    st.pyplot(fig)

    latest = hist.iloc[-1]
    if "accuracy" in hist.columns and len(hist) >= 2:
        prev = hist.iloc[-2]
        st.caption(f"Latest run: accuracy {latest['accuracy']:.3f} "
                   f"({latest['accuracy'] - prev['accuracy']:+.3f} vs previous), "
                   f"model {latest['model_version']}")


st.sidebar.title("🏦 Churn Dashboard")
page = st.sidebar.radio("Page", ["Predictions", "Monitoring"])
st.sidebar.caption(f"API: {API}")

if page == "Predictions":
    predictions_page()
else:
    monitoring_page()
