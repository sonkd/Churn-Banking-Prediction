"""Run the full research pipeline M1->M5. Independent of development/ and report/.
Produces the artifact contract under research/outputs/ and data/processed/."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # make `src` importable
from src.m1_data_generation.generate import generate
from src.m2_eda.eda import run as eda_run
from src.m3_cleaning.clean import clean
from src.m4_feature_engineering.features import build
from src.m5_modeling.train_churn import train as train_churn
from src.m5_modeling.train_segments import train as train_segments
from src.common.io import save_json

def main():
    print("=== Research pipeline M1->M5 ===")
    generate()                       # M1
    eda_run()                        # M2
    clean()                          # M3
    build()                          # M4
    churn_metrics = train_churn()    # M5-A
    sil, by_seg = train_segments()   # M5-B
    # consolidated metrics.json -> consumed by report/
    save_json({"churn": churn_metrics, "segmentation": {"silhouette": sil,
               "churn_rate_by_segment": by_seg}}, "outputs/metrics/metrics.json")
    print("=== DONE. Artifacts in research/outputs/ + data/processed/ ===")

if __name__ == "__main__":
    main()
