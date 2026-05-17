import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import platform
import os


# ==========================================
# 1. 配置 Matplotlib 以支持中文显示
# ==========================================
def setup_chinese_font():
    system_name = platform.system()
    font_list = []

    if system_name == 'Windows':
        font_list = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    elif system_name == 'Darwin':  # macOS
        font_list = ['PingFang SC', 'Heiti TC', 'STHeiti', 'Arial Unicode MS']
    else:  # Linux
        font_list = ['WenQuanYi Micro Hei', 'SimHei', 'Arial Unicode MS']

    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False
    print(f"[系统信息] 检测到操作系统: {system_name}, 已配置中文字体。")


setup_chinese_font()

# ==========================================
# 2. 数据读取
# ==========================================
file_paths = {
    'mfg': '../req/数据清洗/制造业PMI.xlsx',
    'nmfg': '../req/数据清洗/非制造业PMI.xlsx',
    'svc': '../req/数据清洗/服务生产指数.xlsx'
}

data_frames = {}
for key, path in file_paths.items():
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件未找到: {path}，请确保文件在当前目录下。")

    df = pd.read_excel(path)

    # 自动识别时间列
    date_col = None
    for col in df.columns:
        col_str = str(col)
        if '月' in col_str or 'Date' in col_str or 'date' in col_str:
            date_col = col
            break
    if not date_col:
        date_col = df.columns[0]

    df['日期'] = pd.to_datetime(df[date_col])
    data_frames[key] = df
    print(f"[数据加载] 成功加载 {path}, 时间列识别为: {date_col}")


# ==========================================
# 3. 智能列名查找 (修复 TypeError)
# ==========================================
def find_value_column(df, must_have_keywords, or_keywords=None):
    """
    查找包含必须关键词，且包含任意一个可选关键词的列。

    参数:
    - must_have_keywords: list of str, 必须包含的词
    - or_keywords: list of str, 至少包含其中一个的词 (可选)
    """
    for col in df.columns:
        col_str = str(col)

        # 检查必须包含的词
        has_must = all(k in col_str for k in must_have_keywords)

        if not has_must:
            continue

        # 检查可选词 (OR 逻辑)
        if or_keywords:
            has_or = any(k in col_str for k in or_keywords)
            if not has_or:
                continue

        return col

    # 如果没找到，返回第一个数值列作为备选
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != '日期':
            return col
    return None


# --- 制造业 PMI (权重 0.5) ---
# 必须包含: '制造', '指数'
col_mfg = find_value_column(data_frames['mfg'], ['制造', '指数'])
if col_mfg:
    data_frames['mfg']['score_mfg'] = data_frames['mfg'][col_mfg] * 0.5
    print(f"[制造业] 使用列: {col_mfg}")
else:
    raise ValueError("未在制造业PMI文件中找到合适的指数列。")

# --- 非制造业 PMI (权重 0.3) ---
# 必须包含: '非制造', '指数'
col_nmfg = find_value_column(data_frames['nmfg'], ['非制造', '指数'])
if col_nmfg:
    data_frames['nmfg']['score_nmfg'] = data_frames['nmfg'][col_nmfg] * 0.3
    print(f"[非制造业] 使用列: {col_nmfg}")
else:
    raise ValueError("未在非制造业PMI文件中找到合适的指数列。")

# --- 服务业生产指数 (权重 0.2) ---
# 必须包含: '服务'
# 或者包含: '增速' 或 '指数' (针对 '服务业生产指数当月同比增速(%)' 这种情况)
col_svc = find_value_column(data_frames['svc'], ['服务'], or_keywords=['增速', '指数'])
if col_svc:
    data_frames['svc']['score_svc'] = data_frames['svc'][col_svc] * 0.2
    print(f"[服务业] 使用列: {col_svc}")
else:
    raise ValueError("未在服务业指数文件中找到合适的列。")

# ==========================================
# 4. 合并数据
# ==========================================
df_m = data_frames['mfg'][['日期', 'score_mfg']]
df_nm = data_frames['nmfg'][['日期', 'score_nmfg']]
df_s = data_frames['svc'][['日期', 'score_svc']]

merged = pd.merge(df_m, df_nm, on='日期', how='inner')
combined_data = pd.merge(merged, df_s, on='日期', how='inner')

combined_data['综合景气指数'] = (
        combined_data['score_mfg'] +
        combined_data['score_nmfg'] +
        combined_data['score_svc']
)

combined_data.sort_values('日期', inplace=True)
combined_data.reset_index(drop=True, inplace=True)

print(f"\n[数据构建完成] 共 {len(combined_data)} 条记录。")
print(combined_data.head())

# ==========================================
# 5. 可视化：历史走势
# ==========================================
plt.figure(figsize=(14, 7))
plt.plot(combined_data['日期'], combined_data['综合景气指数'], 'b-o', linewidth=2, label='综合景气指数', markersize=6)
plt.axhline(y=50, color='r', linestyle='--', linewidth=1.5, label='临界点 (50)')

plt.title('中国经济景气指数走势 (基于PMI等先行指标)', fontsize=16, pad=15)
plt.xlabel('时间', fontsize=12)
plt.ylabel('景气指数', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('economic_sentiment_index_cn.png', dpi=300)
plt.show()

# ==========================================
# 6. 预测与可视化
# ==========================================
X = np.array(range(len(combined_data))).reshape(-1, 1)
y = combined_data['综合景气指数']
model = LinearRegression()
model.fit(X, y)
future_steps = 6
last_idx = len(combined_data) - 1
future_X = np.array(range(last_idx + 1, last_idx + 1 + future_steps)).reshape(-1, 1)
future_y = model.predict(future_X)
last_date = combined_data['日期'].iloc[-1]
try:
    future_dates = pd.date_range(start=last_date, periods=future_steps + 1, freq='ME')[1:]
except:
    future_dates = pd.date_range(start=last_date, periods=future_steps + 1, freq='M')[1:]

plt.figure(figsize=(14, 7))
plt.plot(combined_data['日期'], combined_data['综合景气指数'], 'b-o', linewidth=2, label='历史数据', markersize=6)
plt.plot(future_dates, future_y, 'r--s', linewidth=2, label='预测趋势 (未来6个月)', markersize=8)
plt.axhline(y=50, color='gray', linestyle=':', linewidth=1.5, label='临界点 (50)')

plt.fill_betweenx([0, 100], combined_data['日期'].max(), future_dates.max(), color='red', alpha=0.05)

plt.title('中国经济景气指数及未来预测 (2026)', fontsize=16, pad=15)
plt.xlabel('时间', fontsize=12)
plt.ylabel('景气指数', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('economic_sentiment_forecast_cn.png', dpi=300)
plt.show()

print("\n=== 未来6个月预测结果 ===")
for date, val in zip(future_dates, future_y):
    print(f"{date.strftime('%Y年%m月')}: {val:.2f}")