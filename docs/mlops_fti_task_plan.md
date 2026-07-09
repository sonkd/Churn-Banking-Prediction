# Task Plan — FTI Pipeline với FastAPI + Streamlit

> Chuyển repo `churn-banking-prediction` sang kiến trúc **FTI (Feature / Training / Inference)**
> theo diagram của Paul Iusztin (Full Stack 7-Steps MLOps Framework, Lesson 6).
> Mỗi phase là 1 phiên làm việc với Claude Code, có prompt sẵn và Definition of Done.

**Tóm tắt:** Repo đã có ~70% nguyên liệu (research M1–M5 với model v2, development có
FastAPI `/predict` online + Streamlit + drift report). Việc chính là **tái cấu trúc theo 3
pipeline độc lập + bucket**, để FastAPI chỉ *đọc* prediction đã tính sẵn (batch-serving),
đúng tinh thần bài viết — không phá artifact contract hiện có.

---

## 1. Giả định (điều chỉnh nếu sai)

- **A1.** Giữ nguyên split 3 phần `research / development / report` và artifact contract trong README — chỉ *mở rộng*, không đổi tên path đã có.
- **A2.** Không dùng Hopsworks/GCS/Airflow như bài gốc — project 8 tuần, free tier. Feature store = parquet có version; bucket = thư mục local qua `fsspec` (swap sang GCS/S3 sau chỉ bằng đổi env var).
- **A3.** ML Platform = **W&B free tier** (khớp diagram); nếu không muốn tài khoản ngoài → MLflow local (đổi 1 dòng trong P2).
- **A4.** Deploy target = Hugging Face Spaces (Docker), theo development/README.
- **A5.** Deadline bám milestone README: CP2 features+models 07/08, CP3 deployment+monitoring 21/08/2026.
- **A6.** Dữ liệu synthetic → không có PII thật; vẫn không log identifier thô trong API logs.

## 2. Mapping diagram → repo

| Diagram (Iusztin) | Repo hiện tại | Việc cần làm |
|---|---|---|
| #1 FE Pipeline (API → FE → Validation) | `research/src/m1–m4` | Thêm data validation (pandera) sau M3 |
| Feature Store (Hopsworks) | `data/processed/features.parquet` | Thêm `feature_metadata.json` (schema, version, hash) |
| #2 Training Pipeline + W&B | `research/src/m5` | Tích hợp W&B tracking + model registry semver |
| #3 Batch Prediction Pipeline | **chưa có** | Mới: `development/batch/predict.py` |
| Bucket (GCS) | **chưa có** | Mới: `development/bucket/` qua fsspec |
| Model Monitoring | `development/monitoring/` | Chạy trên output bucket, ghi metrics ngược về bucket |
| API – Web App (FastAPI) | `development/api/` (chỉ `/predict` online) | Thêm GET endpoints đọc bucket (read-only) |
| UI – Web App (Streamlit) | `development/app/` (1 trang) | 2 dashboard: Predictions + Monitoring |

## 3. Quyết định kiến trúc

| Quyết định | Chọn | Thay vì | Lý do / trade-off |
|---|---|---|---|
| Feature store | Parquet + metadata file | Hopsworks | 1 model, 8 tuần → YAGNI; giữ đúng contract sẵn có. Mất: point-in-time join (không cần) |
| Experiment tracking | W&B free | MLflow self-host | Khớp diagram, 0 hạ tầng; secret `WANDB_API_KEY` qua env |
| Bucket | Local dir + fsspec | GCS | 0 chi phí, code không đổi khi swap (`BUCKET_URI` env) |
| Serving | **Batch-serving** (API đọc bucket) + giữ `/predict` online cho demo | Chỉ online | Đọc bucket ≈ instant → UX "real-time" với chi phí batch; `/predict` giữ cho live demo chấm điểm |
| Orchestration | `run_pipeline.py` + Makefile + GH Actions cron | Airflow | Airflow là over-engineering ở quy mô này |
| Monitoring UI | Page thứ 2 trong Streamlit | Service riêng (như bài gốc) | Tiết kiệm 1 container trên free tier |

**Impact:** batch-serving giảm latency đọc prediction xuống mức đọc file (~ms), cho phép
UI hiển thị top-k khách hàng rủi ro theo segment → gắn trực tiếp KPI retention của bài toán.

---

## 4. Phases — mỗi phase 1 phiên Claude Code

### P0 — Scaffold cho Claude Code (0.5 ngày, 08–09/07)
- [ ] Tạo `CLAUDE.md` ở root: artifact contract, quy tắc "3 phần độc lập", lệnh chạy/test từng phần, style (ruff, pytest).
- [ ] `Makefile`: `make features / train / batch-predict / serve / monitor / test`.
- [ ] `development/.env.default`: `BUCKET_URI=./bucket`, `API_URL`, `MODEL_DIR`.

**Prompt:** `Read README.md and docs/mlops_fti_task_plan.md. Create CLAUDE.md at repo root codifying the artifact contract and the 3-part independence rule, a root Makefile with targets features/train/batch-predict/serve/monitor/test, and development/.env.default. Do not modify existing artifact paths.`

**DoD:** `make test` chạy pass ở cả research lẫn development trên máy sạch.

### P1 — Pipeline #1: Feature Engineering (2 ngày, trước CP1 24/07)
- [ ] Thêm bước validation bằng **pandera** sau M3: schema, range, null-rate; fail-closed.
- [ ] Chuẩn hóa feature store: `data/processed/features.parquet` + `feature_metadata.json` (schema, feature list, version, created_at, row hash).
- [ ] `run_pipeline.py` in validation summary; CI chạy validation trên sample.

**Prompt:** `In research/, add a pandera validation step after M3 cleaning (fail the pipeline on schema violation), and write data/processed/feature_metadata.json alongside features.parquet with schema, version, created_at. Update run_pipeline.py and add unit tests.`

**DoD:** pipeline fail khi inject 1 lỗi schema cố ý; metadata file được cả monitoring đọc được.

### P2 — Pipeline #2: Training + W&B (2 ngày, trước CP2 07/08)
- [ ] Wrap `train_churn.py` / `train_segments.py` với W&B: log params, AUC/PR/F1, confusion, calibration.
- [ ] Model registry: giữ `research/outputs/models/`, thêm semver vào `model_card.json` (feature list, threshold, metrics, data version từ P1).
- [ ] `sync_model.sh` copy đúng version được "promote".

**Prompt:** `Integrate Weights & Biases tracking into research/src/m5_modeling (params, metrics, artifacts), guard behind WANDB_MODE=offline default. Extend model_card.json with semver, feature_list, threshold, training data version read from feature_metadata.json.`

**DoD:** 2 run liên tiếp so sánh được trên W&B; model_card đủ để API load không cần hỏi research.

### P3 — Pipeline #3: Batch Prediction → Bucket (2 ngày)
- [ ] Mới `development/batch/predict.py`: load model từ `development/models/` (hoặc stub), đọc `features.parquet`, ghi `bucket/predictions/latest.parquet` (+ bản snapshot theo timestamp) và `bucket/metadata.json`.
- [ ] Truy cập bucket qua `fsspec` + `BUCKET_URI` (local dir mặc định, GCS/S3 sau).
- [ ] Output: `customer_id, churn_proba, churn_label, segment, model_version, scored_at`.

**Prompt:** `Create development/batch/predict.py: load model via existing api/model_loader (stub fallback), read data/processed/features.parquet, write predictions parquet + metadata.json into a bucket accessed via fsspec with BUCKET_URI env (default ./bucket). Add tests using the stub model.`

**DoD:** 1 lệnh `make batch-predict` sinh predictions cho toàn bộ khách hàng, chạy được cả khi chưa sync model thật (stub).

### P4 — FastAPI backend: đọc bucket (2 ngày)
Giữ `POST /predict` (online demo). Thêm, theo đúng pattern Lesson 6 (API read-only với bucket):
- [ ] `GET /predictions/{customer_id}` — proba + segment + model_version.
- [ ] `GET /predictions?segment=&top_k=` — danh sách rủi ro cao nhất (retention list).
- [ ] `GET /monitoring/metrics` — PSI tổng hợp, drift trigger status.
- [ ] `GET /segments` — segment values cho dropdown UI.
- [ ] Settings class (pydantic-settings) đọc `.env`; `/ready` báo model + bucket state.

**Prompt:** `Extend development/api: add pydantic-settings Settings loading .env, and read-only endpoints GET /predictions/{customer_id}, GET /predictions?segment=&top_k=, GET /segments, GET /monitoring/metrics that read parquet/json from BUCKET_URI via fsspec. Keep POST /predict unchanged. Add httpx tests incl. bucket-empty 404 case.`

**DoD:** Swagger docs đầy đủ; tests pass với bucket rỗng (404 rõ ràng) và bucket có data; API không import gì từ research.

### P5 — Streamlit: 2 dashboards (2 ngày)
- [ ] **Predictions page:** dropdown segment (từ `/segments`), phân phối churn proba, bảng top-k khách hàng rủi ro + nút export CSV cho retention team.
- [ ] **Monitoring page:** PSI per feature (bar, ngưỡng 0.2), trạng thái retrain trigger, timestamp batch gần nhất.
- [ ] UI chỉ gọi API qua `API_URL` — không đọc file trực tiếp; graceful khi API down.

**Prompt:** `Rewrite development/app/streamlit_app.py as a 2-page app (Predictions, Monitoring) that only consumes the FastAPI endpoints via API_URL env. Predictions: segment filter, churn probability histogram, top-k risk table with CSV download. Monitoring: per-feature PSI bar chart with 0.2 threshold line and retrain-trigger status. Handle API-down with a clear error state.`

**DoD:** cả 2 page render từ API thật; rút mạng API → UI báo lỗi thân thiện, không crash.

### P6 — Monitoring loop + Docker + Deploy + CI (3 ngày, trước CP3 21/08)
- [ ] `drift_report.py` đọc batch mới nhất từ bucket, so với `features.parquet` reference (đúng feedback loop Bucket → Monitoring trong diagram), ghi `bucket/monitoring/metrics.json` + Evidently HTML.
- [ ] Docker compose: 2 services (api, app) + `make monitor` chạy định kỳ (GH Actions cron).
- [ ] CI: ruff + pytest + build image; regression gate đơn giản (AUC không giảm >2% so với model_card đã commit).
- [ ] Deploy HF Spaces; smoke test `/health`, `/predictions?top_k=5`.

**Prompt:** `Refactor development/monitoring/drift_report.py to read the latest batch from BUCKET_URI, compare against data/processed/features.parquet reference, and write monitoring/metrics.json back to the bucket (retrain trigger: any PSI > 0.2). Update docker-compose healthchecks, add GitHub Actions workflow: ruff, pytest, docker build, and a metric regression gate against the committed model_card.`

**DoD (tổng, khớp development/README):** live link public trả `/health` OK; `/predictions` trả data thật từ bucket; monitoring page render PSI với trigger rule định nghĩa rõ; CI xanh trên PR.

---

## 5. Rủi ro & failure modes

| Rủi ro | Phát hiện | Xử lý |
|---|---|---|
| Schema features thay đổi làm gãy batch predict | pandera fail ở P1 (fail-closed) | Version bump metadata; batch từ chối chạy nếu feature_list ≠ model_card |
| Evidently API đổi giữa các version | pin `evidently` trong requirements | PSI tự viết là fallback (đã có) |
| HF Spaces free tier sleep / build limit | deploy hello-world sớm (tuần này) | Render free làm phương án 2 |
| W&B key lộ trong CI | không bao giờ hardcode | GH secret + `WANDB_MODE=offline` mặc định local |
| Stub model vs model thật lệch output schema | test contract chung ở P3 | 1 test chạy cả 2 model qua cùng schema assert |

## 6. Next steps (tuần này, 08–11/07)

1. Chạy **P0** với Claude Code (30–60 phút) — mở khóa mọi phase sau.
2. Deploy hello-world FastAPI lên HF Spaces để lộ giới hạn free tier sớm.
3. Chốt A3 (W&B vs MLflow) với team trước khi vào P2.
