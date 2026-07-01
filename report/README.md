# Part 3 — Report (Module 8)

Independent. Assembles the final report (PDF) and slides (PPTX) from research artifacts, with
placeholder fallback so it runs even before research/development are finished.

## Run

```bash
pip install -r requirements.txt
python build_report.py     # injects metrics, copies figures, builds slides.pptx
# export final_report.built.md -> PDF (e.g. pandoc, or the docx/pdf skill)
```

## Files
| File | Role |
|---|---|
| `final_report.md` | report template with `{{AUC}}/{{RECALL}}/{{F1}}` placeholders |
| `build_report.py` | injects metrics from `research/outputs/metrics/`, copies figures |
| `build_slides.py` | generates `slides.pptx` (deliverable) |
| `figures/` | figures copied from research outputs |

## Independence
Reads only `research/outputs/metrics/*.json` and `figures/*.png`. If absent, uses placeholders —
so the report part never blocks on the others. **DoD:** PDF + PPTX produced; every segment has a
retention action; limitations + causal-validation note included.
