#coding=utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取各文件（请确保文件路径正确）
cpi_df = pd.read_excel('../req/数据清洗/居民消费指数.xlsx')
ppi_df = pd.read_excel('../req/数据清洗/PPI.xlsx')
ppirm_df = pd.read_excel('../req/数据清洗/PPIRM.xlsx')
m2_df = pd.read_excel('../req/数据清洗/货币供应量.xlsx')  # 可选，用于观察货币因素
# 可根据需要读取其他文件

# 统一日期格式：将“月份”列转换为datetime，并设置为索引
for df in [cpi_df, ppi_df, ppirm_df, m2_df]:
    df['月份'] = pd.to_datetime(df['月份'])
    df.set_index('月份', inplace=True)
    df.sort_index(inplace=True)

    # 查看CPI数据结构
    print(cpi_df.head())
    # 选取CPI总指数及关键分项
    cpi_clean = cpi_df[['居民消费价格指数(上年同月=100)',
                        '食品烟酒类居民消费价格指数(上年同月=100)',
                        '非食品居民消费价格指数(上年同月=100)',
                        '不包括食品和能源居民消费价格指数(上年同月=100)']].copy()
    cpi_clean.columns = ['CPI', 'CPI_食品烟酒', 'CPI_非食品', 'CPI_核心']

    # 查看PPI数据结构
    print(ppi_df.head())
    ppi_clean = ppi_df[['工业生产者出厂价格指数(上年同月=100)',
                        '生产资料工业生产者出厂价格指数(上年同月=100)',
                        '生活资料工业生产者出厂价格指数(上年同月=100)']].copy()
    ppi_clean.columns = ['PPI', 'PPI_生产资料', 'PPI_生活资料']

    # 查看PPIRM数据结构
    print(ppirm_df.head())
    ppirm_clean = ppirm_df[['工业生产者购进价格指数(上年同月=100)']].copy()
    ppirm_clean.columns = ['PPIRM']

    # 合并主要价格指数
    price_df = cpi_clean.join([ppi_clean, ppirm_clean], how='inner')
    price_df = price_df.astype(float)
    price_df.head()

#一、主要价格指数走势对比
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
# 子图1：CPI、PPI、PPIRM
axes[0].plot(price_df.index, price_df['CPI'], marker='o', label='CPI (上年同月=100)')
axes[0].plot(price_df.index, price_df['PPI'], marker='s', label='PPI')
axes[0].plot(price_df.index, price_df['PPIRM'], marker='^', label='PPIRM')
axes[0].axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
axes[0].set_ylabel('指数 (上年同月=100)')
axes[0].legend()
axes[0].set_title('CPI、PPI与PPIRM同比走势')
# 子图2：CPI分项
axes[1].plot(price_df.index, price_df['CPI'], marker='o', label='CPI总体')
axes[1].plot(price_df.index, price_df['CPI_食品烟酒'], marker='s', label='食品烟酒')
axes[1].plot(price_df.index, price_df['CPI_非食品'], marker='^', label='非食品')
axes[1].plot(price_df.index, price_df['CPI_核心'], marker='d', label='核心CPI(不含食品能源)')
axes[1].axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
axes[1].set_ylabel('指数 (上年同月=100)')
axes[1].legend()
axes[1].set_title('CPI分项走势')
# 子图3：PPI分项
axes[2].plot(price_df.index, price_df['PPI'], marker='o', label='PPI总体')
axes[2].plot(price_df.index, price_df['PPI_生产资料'], marker='s', label='生产资料')
axes[2].plot(price_df.index, price_df['PPI_生活资料'], marker='^', label='生活资料')
axes[2].axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
axes[2].set_ylabel('指数 (上年同月=100)')
axes[2].legend()
axes[2].set_title('PPI分项走势')
plt.xlabel('月份')
plt.tight_layout()
output_name = '主要价格指数走势对比'
plt.savefig(output_name, dpi=300, bbox_inches='tight')
plt.show()

#二、计算总体相关系数
corr_matrix = price_df[['CPI', 'PPI', 'PPIRM']].corr()
print("相关系数矩阵：\n", corr_matrix)
# 绘制散点图矩阵
sns.pairplot(price_df[['CPI', 'PPI', 'PPIRM']])
plt.suptitle('CPI、PPI、PPIRM散点图矩阵', y=1.02)

output_name = 'CPI与PPI的相关性分析'
plt.savefig(output_name, dpi=300, bbox_inches='tight')

plt.show()
#三、滞后相关性分析（探究传导时滞）
from statsmodels.tsa.stattools import ccf

# 取同比变化率（实际已经是同比指数，为方便可计算环比变化，但同比本身已反映趋势）
# 我们直接使用同比指数进行互相关分析
x = price_df['PPI'].values
y = price_df['CPI'].values

# 计算互相关函数（最大滞后6期）
lags = range(-6, 7)
ccf_values = [ccf(x, y, adjusted=False)[abs(lag)] for lag in lags]

# 绘制
plt.figure(figsize=(10,5))
plt.stem(lags, ccf_values, basefmt=" ")
plt.xlabel('滞后阶数（月）')
plt.ylabel('互相关函数')
plt.title('PPI与CPI的互相关分析（负滞后表示PPI领先CPI）')
plt.axhline(y=0, color='gray', linestyle='--')
plt.axvline(x=0, color='gray', linestyle='--')
plt.grid(True)
output_name = '滞后相关性分析（探究传导时滞）'
plt.savefig(output_name, dpi=300, bbox_inches='tight')
plt.show()

#四、分项传导：生产资料PPI vs CPI非食品，生活资料PPI vs CPI食品烟酒
fig, axes = plt.subplots(1, 2, figsize=(14,5))

# 左图：生产资料PPI vs CPI非食品
axes[0].plot(price_df.index, price_df['PPI_生产资料'], marker='o', label='PPI生产资料')
axes[0].plot(price_df.index, price_df['CPI_非食品'], marker='s', label='CPI非食品')
axes[0].axhline(y=100, color='gray', linestyle='--')
axes[0].set_ylabel('指数 (上年同月=100)')
axes[0].legend()
axes[0].set_title('生产资料PPI与CPI非食品')

# 右图：生活资料PPI vs CPI食品烟酒
axes[1].plot(price_df.index, price_df['PPI_生活资料'], marker='o', label='PPI生活资料')
axes[1].plot(price_df.index, price_df['CPI_食品烟酒'], marker='s', label='CPI食品烟酒')
axes[1].axhline(y=100, color='gray', linestyle='--')
axes[1].set_ylabel('指数 (上年同月=100)')
axes[1].legend()
axes[1].set_title('生活资料PPI与CPI食品烟酒')

plt.tight_layout()

output_name = '生产资料PPI vs CPI非食品，生活资料PPI vs CPI食品烟酒'
plt.savefig(output_name, dpi=300, bbox_inches='tight')
plt.show()

#五、价格传导机制示意图：PPIRM→PPI→CPI
# 绘制三个指数的标准化走势（以2025年1月为基期100）
price_norm = price_df[['PPIRM', 'PPI', 'CPI']].div(price_df.loc[price_df.index[0], ['PPIRM', 'PPI', 'CPI']], axis=1) * 100

plt.figure(figsize=(12,6))
plt.plot(price_norm.index, price_norm['PPIRM'], marker='o', label='PPIRM (购进价格)')
plt.plot(price_norm.index, price_norm['PPI'], marker='s', label='PPI (出厂价格)')
plt.plot(price_norm.index, price_norm['CPI'], marker='^', label='CPI (消费价格)')
plt.axhline(y=100, color='gray', linestyle='--')
plt.ylabel('定基指数 (2025-01=100)')
plt.title('价格传导链：PPIRM → PPI → CPI（定基）')
plt.legend()
plt.grid(True)

output_name = '价格传导机制示意图：PPIRM→PPI→CPI'
plt.savefig(output_name, dpi=300, bbox_inches='tight')
plt.show()

#六、货币供应量M2与通胀的关系
# 读取M2同比数据
m2_growth = m2_df[['货币和准货币(M2)供应量同比增长(%)']].copy()
m2_growth.columns = ['M2同比']

# 合并
price_m2 = price_df[['CPI']].join(m2_growth, how='inner')

fig, ax1 = plt.subplots(figsize=(12,5))

ax1.plot(price_m2.index, price_m2['CPI'], 'b-o', label='CPI')
ax1.set_xlabel('月份')
ax1.set_ylabel('CPI (上年同月=100)', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.axhline(y=100, color='b', linestyle='--', linewidth=0.5)

ax2 = ax1.twinx()
ax2.plot(price_m2.index, price_m2['M2同比'], 'r-s', label='M2同比')
ax2.set_ylabel('M2同比增长 (%)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

plt.title('CPI与M2同比走势')
fig.tight_layout()

output_name = '货币供应量M2与通胀的关系'
plt.savefig(output_name, dpi=300, bbox_inches='tight')

plt.show()