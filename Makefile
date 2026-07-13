PYTHON ?= python3

.PHONY: features train promote batch-predict serve monitor test

## research: promote v3 notebook artifacts -> canonical contract paths, then sync to development
promote:
	cd research && $(PYTHON) promote_v3.py
	bash development/scripts/sync_model.sh

## research: M1 generate -> M3 clean -> validate (fail-closed) -> M4 build features
features:
	cd research && $(PYTHON) -c "from src.m1_data_generation.generate import generate; from src.m3_cleaning.clean import clean; from src.m3_cleaning.validate import validate_base; from src.m4_feature_engineering.features import build; generate(); base, _ = clean(); validate_base(base); build()"

## research: M5 train_churn + train_segments
train:
	cd research && $(PYTHON) -c "from src.m5_modeling.train_churn import train as train_churn; from src.m5_modeling.train_segments import train as train_segments; train_churn(); train_segments()"

## development: score data/processed/features.parquet -> bucket/predictions/
batch-predict:
	cd development && $(PYTHON) -m batch.predict

## development: API :8000 + Streamlit :8501 via docker compose
serve:
	cd development && docker compose down && docker compose up --build

## development: drift report against the bucket's latest batch
monitor:
	cd development && $(PYTHON) monitoring/drift_report.py

## pytest in both independent parts - both must pass
test:
	cd research && $(PYTHON) -m pytest tests -q
	cd development && $(PYTHON) -m pytest tests -q
