"""Module 2 — EDA. Distributions, outliers, correlations, churn by segment, RFM-style viz.
Discipline (eda-python): label each finding observation / hypothesis / causal-claim.
Run on raw data first to FIND problems; re-read after M3 cleaning."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from data_profiling import ProfileReport

from src.common.io import load_config, rpath, read_csv

def run():
    cfg = load_config()
    base = read_csv(cfg["paths"]["raw"])
    tx = read_csv(cfg["paths"]["synthetic"])
    fig_dir = rpath(cfg["paths"]["figures"])

    behavior_agg = tx.groupby('customer_id').agg({
        'txn_count': ['sum', 'mean', 'std'],           # Số lượng giao dịch
        'txn_amount': ['sum', 'mean', 'std'],          # Tổng tiền giao dịch
        'app_logins': ['sum', 'mean'],                 # Số lần đăng nhập app
        'complaints': ['sum'],                         # Tổng khiếu nại
        'channel_atm': ['sum'],                        # Tổng giao dịch ATM
        'channel_mobile': ['sum'],                     # Tổng giao dịch mobile
        'channel_branch': ['sum'],                     # Tổng giao dịch branch
    })
    
    behavior_agg.columns = ['_'.join(col).strip() for col in behavior_agg.columns.values]
    behavior_agg = behavior_agg.reset_index()

    df_final = base.merge(behavior_agg, on='customer_id', how='left')

    # EDA
    profile = ProfileReport(df_final, title="Bank Customer Churn Data Profiling", explorative=True)
    profile.to_file(fig_dir / "eda_profile_report.html")

    # Clustering
    X = (
        df_final
        .drop(columns=["customer_id", "churn"])
        .select_dtypes("number")
        .fillna(0)
    )

    best_k = max(
        range(2, 8),
        key=lambda k: silhouette_score(
            X,
            KMeans(n_clusters=k, random_state=42).fit_predict(X)
        ),
    )

    labels = KMeans(n_clusters=best_k, random_state=42).fit_predict(X)

    # Cluster profile (z-score)
    profile = X.assign(cluster=labels).groupby("cluster").mean()

    plt.figure(figsize=(10, 4))
    sns.heatmap(profile, cmap="RdBu_r", center=0)
    plt.tight_layout()
    plt.savefig(fig_dir / "cluster_profile.png")
    plt.close()

    # Churn rate
    (
        df_final.assign(cluster=labels)
        .groupby("cluster")["churn"]
        .mean()
        .plot.bar(rot=0)
    )

    plt.ylabel("Churn Rate")
    plt.tight_layout()
    plt.savefig(fig_dir / "cluster_churn.png")
    plt.close()

    return ["eda_profile_report.html", "cluster_profile.png", "cluster_churn.png"]

if __name__ == "__main__":
    run()

"""
Kết quả EDA view tại research/outputs/figures/eda_profile_report.html.
Các quan sát:
- Phân bố tuổi hơi lạ, không mượt, hình như có những data làm chẵn tuổi.
- Lượng khách hàng thâm niên 10 năm tụt bất thường.
- Số người sử dụng product 3 và 4 hơi ít
- Số lượt lẫn khối lượng giao dịch là hợp của 2 phân bố nhỏ gọi ý 2 phân khúc khách hàng
- Tần suất phàn nàn đạt đỉnh tại 3 -> có thể phản hồi đến lần thứ 3 là bắt đầu churn
- Churn tương quan cao với: số lượt đăng nhập, số lượt phàn nàn, số lượt giao dịch.
  ngoài ra tuổi, khối lượng giao dịch, số dư, điểm tín dụng cũng tác động nhẹ.
- Kênh sử dụng (atm/chi nhánh/điện thoại), mức lương, thâm niên, có sử dụng dịch vụ tín dụng
  hay không, không có tác động đến churn.
- Với phân cụm thì số cụm tối ưu là 4: 
    - Cụm 0: Số dư thâp + Lương cao
    - Cụm 1: Số dư thấp + Lương thấp
    - Cụm 2: Số dư cao + Lương cao
    - Cụm 3: Số dư cao + Lương thấp
- Churn rate của cụm 0,1 là ~ 14% và cụm 2,3 là ~24%. -> Khách hàng giữ nhiều tiền trong ngân
  hàng hình như kỳ vọng nhiều hơn. Mức lương ko tác động đến tỉ lệ churn.
"""