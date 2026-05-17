#coding=utf-8
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
ppi = pd.read_excel('../req/数据清洗/PPI.xlsx', sheet_name='Sheet1')
ppirm = pd.read_excel('../req/数据清洗/PPIRM.xlsx', sheet_name='Sheet1')
non_manu_pmi = pd.read_excel('../req/数据清洗/非制造业PMI.xlsx', sheet_name='Sheet1')
service_index = pd.read_excel('../req/数据清洗/服务生产指数.xlsx', sheet_name='Sheet1')
industry_fin = pd.read_excel('../req/数据清洗/工业企业主义经济指标.xlsx', sheet_name='Sheet1')
money_supply = pd.read_excel('../req/数据清洗/货币供应量.xlsx', sheet_name='Sheet1')
trade = pd.read_excel('../req/数据清洗/进出口价格指标.xlsx', sheet_name='Sheet1')
cpi = pd.read_excel('../req/数据清洗/居民消费指数.xlsx', sheet_name='Sheet1')
three_industry = pd.read_excel('../req/数据清洗/三大类工业.xlsx', sheet_name='Sheet1')
unemployment = pd.read_excel('../req/数据清洗/失业率.xlsx', sheet_name='Sheet1')
manu_pmi = pd.read_excel('../req/数据清洗/制造业PMI.xlsx', sheet_name='Sheet1')

# 统一日期格式
def parse_date(df):
    df['月份'] = pd.to_datetime(df['月份'])
    return df

ppi = parse_date(ppi)
ppirm = parse_date(ppirm)
non_manu_pmi = parse_date(non_manu_pmi)
service_index = parse_date(service_index)
industry_fin = parse_date(industry_fin)
money_supply = parse_date(money_supply)
trade = parse_date(trade)
cpi = parse_date(cpi)
three_industry = parse_date(three_industry)
unemployment = parse_date(unemployment)
manu_pmi = parse_date(manu_pmi)

# 按日期排序
for df in [ppi, ppirm, non_manu_pmi, service_index, industry_fin, money_supply, trade, cpi, three_industry, unemployment, manu_pmi]:
    df.sort_values('月份', inplace=True)

# 合并关键指标到同一个DataFrame（以月份为键）
merged = ppi[['月份', '工业生产者出厂价格指数(上年同月=100)',
              '生产资料工业生产者出厂价格指数(上年同月=100)',
              '生活资料工业生产者出厂价格指数(上年同月=100)']].copy()
merged = merged.merge(ppirm[['月份', '工业生产者购进价格指数(上年同月=100)',
                              '燃料、动力类购进价格指数(上年同月=100)',
                              '黑色金属材料类购进价格指数(上年同月=100)',
                              '有色金属材料和电线类购进价格指数(上年同月=100)']],
                      on='月份', how='left')
merged = merged.merge(cpi[['月份', '居民消费价格指数(上年同月=100)']], on='月份', how='left')
merged = merged.merge(manu_pmi[['月份', '出厂价格指数', '主要原材料购进价格指数']], on='月份', how='left')
merged = merged.merge(industry_fin[['月份', '利润总额_累计增长', '营业收入_累计增长', '营业成本_累计增长']], on='月份', how='left')
merged = merged.merge(money_supply[['月份', '货币(M1)供应量同比增长(%)']], on='月份', how='left')

# 计算价格差：PPI - PPIRM（代表利润空间变化方向，正表示出厂价相对购进价上涨，利于利润）
merged['PPI_PPIRM_diff'] = merged['工业生产者出厂价格指数(上年同月=100)'] - merged['工业生产者购进价格指数(上年同月=100)']

plt.figure(figsize=(12,6))
plt.plot(merged['月份'], merged['工业生产者出厂价格指数(上年同月=100)'], marker='o', label='PPI:全部工业品')
plt.plot(merged['月份'], merged['工业生产者购进价格指数(上年同月=100)'], marker='s', label='PPIRM:全部原材料')
plt.plot(merged['月份'], merged['居民消费价格指数(上年同月=100)'], marker='^', label='CPI')
plt.axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
plt.title('PPI、PPIRM与CPI同比走势（上年同月=100）')
plt.xlabel('月份')
plt.ylabel('指数')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12,6))
plt.plot(merged['月份'], merged['生产资料工业生产者出厂价格指数(上年同月=100)'], marker='o', label='生产资料PPI')
plt.plot(merged['月份'], merged['燃料、动力类购进价格指数(上年同月=100)'], marker='s', label='燃料动力类购进价格')
plt.plot(merged['月份'], merged['黑色金属材料类购进价格指数(上年同月=100)'], marker='^', label='黑色金属类购进价格')
plt.plot(merged['月份'], merged['有色金属材料和电线类购进价格指数(上年同月=100)'], marker='d', label='有色金属类购进价格')
plt.axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
plt.title('生产资料PPI与主要原材料购进价格同比走势')
plt.xlabel('月份')
plt.ylabel('指数')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(merged['月份'], merged['PPI_PPIRM_diff'], color='red', marker='o', label='PPI-PPIRM差值')
ax1.set_xlabel('月份')
ax1.set_ylabel('差值（百分点）', color='red')
ax1.tick_params(axis='y', labelcolor='red')
ax1.axhline(y=0, color='red', linestyle='--', linewidth=0.8)

ax2 = ax1.twinx()
ax2.plot(merged['月份'], merged['利润总额_累计增长'], color='blue', marker='s', label='工业企业利润累计同比')
ax2.set_ylabel('利润累计同比（%）', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

plt.title('PPI-PPIRM差值与企业利润累计增速')
fig.tight_layout()
plt.show()