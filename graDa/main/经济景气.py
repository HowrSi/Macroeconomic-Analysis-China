import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # 方案一：引入 seaborn 库 (如果使用方案二，请注释掉这行)

# --- 1. 数据读取 ---
# 读取数据 (请确保文件路径正确)
df_mfg = pd.read_excel('../req/数据清洗/制造业PMI.xlsx', parse_dates=['月份'])
df_service = pd.read_excel('../req/数据清洗/非制造业PMI.xlsx', parse_dates=['月份'])

# 确保月份列是日期格式并排序
df_mfg = df_mfg.sort_values('月份')
df_service = df_service.sort_values('月份')

# --- 2. 计算综合PMI (基于GDP权重估算) ---
# 假设权重: 制造业 40%, 非制造业 60% (基于行业增加值占比的近似值)
WEIGHT_MFG = 0.4
WEIGHT_SERVICE = 0.6

# 合并数据
df_combined = pd.merge(df_mfg[['月份', '制造业采购经理指数']],
                       df_service[['月份', '非制造业商务活动指数']],
                       on='月份')

# 计算综合PMI
df_combined['综合PMI产出指数'] = (df_combined['制造业采购经理指数'] * WEIGHT_MFG +
                                  df_combined['非制造业商务活动指数'] * WEIGHT_SERVICE)

# --- 3. 可视化分析 (修复版) ---
plt.figure(figsize=(14, 7))

# =============== 选择一种方案取消注释 ===============
# 方案一：使用 Seaborn 风格 (最推荐，需安装 seaborn)
sns.set_style("whitegrid") # 设置背景网格
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans'] # 解决中文乱码
plt.rcParams['axes.unicode_minus'] = False

# 方案二：使用 Matplotlib 自带风格 (如果不安装 seaborn，取消下面两行的注释)
# plt.style.use('ggplot') # 使用 ggplot 风格
# plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS'] # 解决中文乱码
# plt.rcParams['axes.unicode_minus'] = False
# =============== 选择结束 ===============

# 绘制线条
plt.plot(df_combined['月份'], df_combined['制造业采购经理指数'],
         marker='o', linewidth=2.5, label='制造业 PMI')
plt.plot(df_combined['月份'], df_combined['非制造业商务活动指数'],
         marker='s', linewidth=2.5, label='非制造业 PMI')
plt.plot(df_combined['月份'], df_combined['综合PMI产出指数'],
         marker='^', linewidth=3, color='purple', linestyle='--', label='综合 PMI (加权)')

# 添加基准线 (50为荣枯线)
plt.axhline(y=50, color='r', linestyle='-', alpha=0.5, label='荣枯线 (50)')

# 图表美化
plt.title('宏观经济景气指数监测 (2025-2026)', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('时间', fontsize=12)
plt.ylabel('指数值', fontsize=12)
plt.legend(fontsize=12, loc='upper left')
plt.grid(True, alpha=0.3)

# 优化日期显示
plt.gcf().autofmt_xdate()

# 显示数值标签 (仅显示最近几个月的数据以避免重叠)
for i, row in df_combined.iterrows():
    if row['月份'].year == 2026 or (row['月份'].year == 2025 and row['月份'].month >= 10):
        plt.annotate(f"{row['综合PMI产出指数']:.1f}",
                    (row['月份'], row['综合PMI产出指数']),
                    textcoords="offset points",
                    xytext=(0,10), ha='center', fontsize=9, color='purple')

plt.tight_layout()
plt.show()

# --- 4. 输出关键结论 ---
print(" 经济景气分析报告 (截至 2026年01月)")
print("-" * 50)
latest_date = df_combined['月份'].max()
latest_data = df_combined[df_combined['月份'] == latest_date].iloc[0]

print(f" 最新监测日期: {latest_date.strftime('%Y-%m')}")
print(f" 制造业 PMI: {latest_data['制造业采购经理指数']}")
print(f" 非制造业 PMI: {latest_data['非制造业商务活动指数']}")
print(f" 综合 PMI (加权): {latest_data['综合PMI产出指数']:.2f}")
print(f" 结论: 当前经济处于 {'扩张' if latest_data['综合PMI产出指数'] > 50 else '收缩'} 区间。")