#!/usr/bin/env bash
# Wire research -> development (the artifact contract). Run after research/run_pipeline.py.
set -e
SRC="../research/outputs/models"
DST="$(dirname "$0")/../models"
mkdir -p "$DST"
cp "$SRC/churn_model.pkl" "$DST/" 2>/dev/null && echo "synced churn_model.pkl" || echo "WARN: churn_model.pkl not found (run research first)"
cp "$SRC/segmentation_model.pkl" "$DST/" 2>/dev/null && echo "synced segmentation_model.pkl" || true
cp "$SRC/model_card.json" "$DST/" 2>/dev/null && echo "synced model_card.json" || true
