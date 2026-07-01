"""Module 8 — Assemble the final report + slides from research artifacts.
Independent: reads metrics/figures if present, else uses placeholders so it always runs."""
import json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
METRICS = ROOT / "research/outputs/metrics/metrics.json"
SEGMENTS = ROOT / "research/outputs/metrics/segments.json"
FIGS = ROOT / "research/outputs/figures"

def load(p, default):
    try: return json.load(open(p))
    except Exception: return default

def main():
    m = load(METRICS, {"churn": {"auc_roc": "TBD", "recall": "TBD", "f1": "TBD"}})
    s = load(SEGMENTS, {"personas": {}, "churn_rate_by_segment": {}})
    (HERE / "figures").mkdir(exist_ok=True)
    for png in FIGS.glob("*.png") if FIGS.exists() else []:
        shutil.copy(png, HERE / "figures" / png.name)
    # inject metrics into final_report.md placeholders
    rep = (HERE / "final_report.md").read_text()
    rep = rep.replace("{{AUC}}", str(m["churn"].get("auc_roc")))
    rep = rep.replace("{{RECALL}}", str(m["churn"].get("recall")))
    rep = rep.replace("{{F1}}", str(m["churn"].get("f1")))
    (HERE / "final_report.built.md").write_text(rep)
    print("[M8] built final_report.built.md (metrics injected, figures copied)")
    try:
        from build_slides import build as build_slides
        build_slides(m, s)
    except Exception as e:
        print(f"[M8] slides skipped ({type(e).__name__}: {e}) — run with python-pptx installed")

if __name__ == "__main__":
    main()
