import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. 准备数据 ---
data = {
    '月份': ['2025-03', '2025-04', '2025-05', '2025-06', '2025-07',
           '2025-08', '2025-09', '2025-10', '2025-11', '2025-12', '2026-01'],
    '制造业_PMI': [50.1, 50.9, 50.2, 49.0, 49.5,
                 49.3, 49.4, 49.8, 49.0, 49.2, 50.3],
    '非制造业_PMI': [50.4, 50.6, 50.8, 50.3, 50.1,
                   50.2, 50.5, 49.9, 50.1, 50.4, 50.5],
}
df = pd.DataFrame(data)

# 创建时间索引 (1, 2, 3...) 并转为二维数组供 sklearn 使用
X_train = np.arange(len(df)).reshape(-1, 1)

# --- 2. 训练模型 ---
model_mfg = LinearRegression()
model_service = LinearRegression()

model_mfg.fit(X_train, df['制造业_PMI'])
model_service.fit(X_train, df['非制造业_PMI'])

# --- 3. 生成预测数据 (2026-02 到 2026-05) ---
# 当前数据有11个，我们要预测接下来的 2, 3, 4, 5月 (共4个月)
future_months_count = 4
# 生成从 11 到 14 的序列 (对应接下来的4个月)
X_future_indices = np.arange(len(df), len(df) + future_months_count).reshape(-1, 1)

# 预测数值
y_mfg_pred = model_mfg.predict(X_future_indices)
y_service_pred = model_service.predict(X_future_indices)

# 生成对应的日期标签
future_dates = pd.date_range(start='2026-02', periods=future_months_count, freq='M').strftime('%Y-%m')

# --- 4. 绘图 ---
plt.figure(figsize=(12, 6))

# 绘制原始数据
plt.plot(df['月份'], df['制造业_PMI'], marker='o', label='制造业 PMI (历史)', color='#1f77b4')
plt.plot(df['月份'], df['非制造业_PMI'], marker='o', label='非制造业 PMI (历史)', color='#ff7f0e')

# 绘制预测数据 (使用虚线)
plt.plot(future_dates, y_mfg_pred, marker='x', linestyle='--', label='制造业 PMI (预测)', color='#1f77b4')
plt.plot(future_dates, y_service_pred, marker='x', linestyle='--', label='非制造业 PMI (预测)', color='#ff7f0e')

# 添加荣枯线
plt.axhline(50, color='red', linestyle='--', alpha=0.6, label='荣枯线 (50)')

# 标注预测数值
for i, txt in enumerate(y_mfg_pred):
    plt.text(future_dates[i], txt + 0.1, f"{txt:.2f}", color='#1f77b4', ha='center')

for i, txt in enumerate(y_service_pred):
    plt.text(future_dates[i], txt - 0.2, f"{txt:.2f}", color='#ff7f0e', ha='center')

plt.title('2026年2月-5月 PMI 趋势预测 (线性回归模型)')
plt.xlabel('时间')
plt.ylabel('PMI 指数')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(48, 52) # 设置Y轴范围以便更好观察
plt.show()

# --- 5. 打印具体预测值 ---
print("📅 2026年2月-5月 预测结果：")
for i in range(future_months_count):
    print(f"{future_dates[i]}: 制造业 {y_mfg_pred[i]:.2f} | 非制造业 {y_service_pred[i]:.2f}")