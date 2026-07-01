# Business Understanding Brief — ABC Multistate Bank Churn Prediction

## Business question (restated)

Trong quý tới, khách hàng nào của ABC Bank có khả năng churn, họ thuộc phân khúc nào, để đội Retention target đúng người và đúng cách tiếp cận.

Đây là câu hỏi ghép **3 lớp** — tách riêng để tránh làm lẫn lộn khi triển khai:

| Lớp câu hỏi | Loại (Analytics type) | Vì sao |
|---|---|---|
| 1. "Khách hàng nào có khả năng churn?" | **Classification** | Target `churn` là nhãn nhị phân (0/1) có sẵn — đây là bài toán supervised classification, không phải forecasting theo thời gian |
| 2. "Họ thuộc phân khúc nào?" | **Descriptive/Diagnostic** (pivot + segmentation) | Nhóm khách hàng theo đặc điểm chung ảnh hưởng churn — dùng pivot table + có thể bổ sung clustering không giám sát |
| 3. "Để retention target hiệu quả" | **Prescriptive** (ngoài phạm vi dự án EDA này) | Đòi hỏi thử nghiệm (A/B test ưu đãi/retention offer theo segment) — là bước tiếp theo sau khi có model + segment, không nằm trong scope EDA |

Thứ tự triển khai đề xuất: **Descriptive/Diagnostic (EDA + pivot) → Classification (model churn) → Segmentation → Prescriptive (ngoài scope, giai đoạn sau)**.

## Assumptions (giả định — điều chỉnh nếu sai)

- `churn` là nhãn lịch sử ("đã rời trong một giai đoạn nào đó"), dataset **không có timestamp/snapshot date**. Giả định đây là snapshot cắt ngang (cross-sectional), không phải rolling window theo quý thực sự. Muốn dự đoán đúng nghĩa "quý tới" cần có mốc thời gian rõ ràng (ngày snapshot, ngày gắn nhãn churn) — nếu không có, model sẽ dự đoán "khả năng churn nói chung", không phải "churn trong Q tới" cụ thể.
- "Segment" hiểu là nhóm khách hàng có đặc điểm chung liên quan churn, chưa phải segment theo giá trị/CLV — làm rõ với stakeholder nếu cần khác.
- 12 cột đã cho là toàn bộ input; không có dữ liệu hành vi/giao dịch/khiếu nại (transaction log, complaint, NPS) — nếu có thêm, sức mạnh dự đoán và phần diagnostic sẽ tăng đáng kể.
- ~~Tỷ lệ churn ước lượng ~20%~~ → **Đã verify trên file thật** (`data/raw/bank_customer_churn.csv`, 10,000 dòng): churn = 1 chiếm **20.37%** (2,037/10,000) — cần imbalance handling (class_weight/SMOTE) khi model.

## KPI liên quan

- Churn rate / retention rate theo segment (nhóm quốc gia, độ tuổi, số sản phẩm...)
- ROI chiến dịch retention: chi phí target vs. giá trị khách hàng giữ được (TOI)
- **Recall@K** (bắt được bao nhiêu khách hàng thực sự sẽ churn trong top K được target) và **Precision@K** (tránh lãng phí ngân sách vào khách hàng vốn không định rời) — đây là trade-off chính khi chọn ngưỡng model, không chỉ nhìn accuracy.

## Kỹ thuật theo từng lớp

**1. Classification (churn model)**
- Baseline: Logistic Regression (diễn giải hệ số dễ) → so sánh Random Forest / XGBoost (accuracy cao hơn, có feature importance).
- Feature engineering cần làm trước khi model:
  - One-hot encode `country`, `gender`
  - Scale `credit_score`, `balance`, `estimated_salary`
  - Cờ `zero_balance` (balance = 0 — pattern phổ biến ở dữ liệu ngân hàng, thường liên quan churn)
  - `balance_to_salary_ratio`
  - Kiểm tra & xử lý class imbalance (`class_weight` hoặc SMOTE nếu churn rate < 25%)

**2. Descriptive/Diagnostic (pattern & pivot table)**
- Churn rate theo `country`, `gender`, age band, `products_number`, `active_member`, `credit_card` (groupby + crosstab).
- Pivot table: rows = age_band × products_number, columns = country, values = churn_rate.
- Correlation: point-biserial cho biến số vs churn; Cramér's V cho biến hạng mục vs churn.

**3. Segmentation**
- Cách 1 (nhanh, dễ diễn giải): rule-based segment rút ra từ pivot table (vd: "≥3 sản phẩm + không active" = segment rủi ro cao).
- Cách 2 (data-driven): K-means/hierarchical clustering trên feature đã scale, không dùng nhãn churn — mô tả segment bằng centroid, sau đó đối chiếu churn rate từng cluster.
- Khuyến nghị chạy cả hai, đối chiếu chéo để tăng độ tin cậy trước khi trình bày cho stakeholder.

## Evidence tier

- Pattern từ descriptive/diagnostic = **Observation + Hypothesis** (tương quan, chưa phải nguyên nhân).
- Feature importance từ model = **Hypothesis về driver**, không phải kết luận nhân quả.
- Muốn khẳng định dạng "giảm phí X sẽ giảm churn Y%" → bắt buộc validate bằng **A/B test hoặc holdout experiment** trên nhóm được target, không suy diễn trực tiếp từ correlation.

## Data cần có

12 cột đã cung cấp (`customer_id` loại khỏi model, 10 cột input, 1 cột target `churn`). Cần xác nhận cỡ mẫu và tỷ lệ churn thực tế trước khi vào EDA.

## Definition of Done (giai đoạn Business Understanding)

- [ ] Đã chốt 3 lớp câu hỏi và thứ tự triển khai ở trên với stakeholder
- [ ] Assumption về churn window & định nghĩa "segment" được xác nhận hoặc điều chỉnh
- [ ] Feature engineering plan sẵn sàng chuyển sang bước EDA
- [ ] KPI đo thành công đã chốt (Recall@K/Precision@K, retention ROI)

## Next step

Chuyển sang `/data-science:eda-python` để thực hiện Data Understanding: profiling, missing/distribution check, correlation với `churn`, rồi feature engineering theo plan ở trên.
