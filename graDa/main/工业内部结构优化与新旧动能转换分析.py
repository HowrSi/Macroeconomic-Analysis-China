#coding=utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体（若系统无中文字体需调整）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据文件（假设所有文件在当前目录）
files = {
    'PPI': '../req/数据清洗/PPI.xlsx',
    'PPIRM': '../req/数据清洗/PPIRM.xlsx',
    '非制造业PMI': '../req/数据清洗/非制造业PMI.xlsx',
    '服务生产指数': '../req/数据清洗/服务生产指数.xlsx',
    '工业企业主义经济指标': '../req/数据清洗/工业企业主义经济指标.xlsx',  # 注意文件名
    '货币供应量': '../req/数据清洗/货币供应量.xlsx',
    '进出口价格指标': '../req/数据清洗/进出口价格指标.xlsx',
    '居民消费指数': '../req/数据清洗/居民消费指数.xlsx',
    '三大类工业': '../req/数据清洗/三大类工业.xlsx',
    '失业率': '../req/数据清洗/失业率.xlsx',
    '制造业PMI': '../req/数据清洗/制造业PMI.xlsx'
}

# 读取所有sheet，统一日期格式
data = {}
for name, path in files.items():
    df = pd.read_excel(path)
    # 假设第一列是月份，列名可能为"月份"或"A"
    if '月份' in df.columns:
        date_col = '月份'
    else:
        date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    df.set_index(date_col, inplace=True)
    # 按日期排序
    df.sort_index(inplace=True)
    data[name] = df

# 创建图表
fig = plt.figure(figsize=(16, 20))

# 1. PPI及其分项（生产资料、生活资料）
ax1 = fig.add_subplot(3, 2, 1)
df_ppi = data['PPI'][['工业生产者出厂价格指数(上年同月=100)',
                      '生产资料工业生产者出厂价格指数(上年同月=100)',
                      '生活资料工业生产者出厂价格指数(上年同月=100)']]
ax1.plot(df_ppi.index, df_ppi.iloc[:,0], marker='o', label='全部工业')
ax1.plot(df_ppi.index, df_ppi.iloc[:,1], marker='s', label='生产资料')
ax1.plot(df_ppi.index, df_ppi.iloc[:,2], marker='^', label='生活资料')
ax1.axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
ax1.set_title('工业生产者出厂价格指数(上年同月=100)')
ax1.set_ylabel('指数')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.6)

# 2. 主要原材料购进价格指数对比
ax2 = fig.add_subplot(3, 2, 2)
df_ppirm = data['PPIRM'][['燃料、动力类购进价格指数(上年同月=100)',
                          '黑色金属材料类购进价格指数(上年同月=100)',
                          '有色金属材料和电线类购进价格指数(上年同月=100)',
                          '化工原料类购进价格指数(上年同月=100)',
                          '建筑材料及非金属矿类购进价格指数(上年同月=100)']]
for col in df_ppirm.columns:
    ax2.plot(df_ppirm.index, df_ppirm[col], marker='.', label=col[:10]+'...')
ax2.axhline(y=100, color='gray', linestyle='--', linewidth=0.8)
ax2.set_title('主要原材料购进价格指数(上年同月=100)')
ax2.set_ylabel('指数')
ax2.legend(loc='upper left', fontsize=8)
ax2.grid(True, linestyle='--', alpha=0.6)

# 3. 三大类工业增加值同比增速
ax3 = fig.add_subplot(3, 2, 3)
df_ind = data['三大类工业'][['采矿业增加值同比增长(%)',
                           '制造业增加值同比增长(%)',
                           '电力、热力、燃气及水生产和供应业增加值同比增长(%)']]
ax3.plot(df_ind.index, df_ind.iloc[:,0], marker='o', label='采矿业')
ax3.plot(df_ind.index, df_ind.iloc[:,1], marker='s', label='制造业')
ax3.plot(df_ind.index, df_ind.iloc[:,2], marker='^', label='电力热力燃气')
ax3.set_title('三大类工业增加值同比增速(%)')
ax3.set_ylabel('%')
ax3.legend()
ax3.grid(True, linestyle='--', alpha=0.6)

# 4. 制造业PMI关键分项
ax4 = fig.add_subplot(3, 2, 4)
df_pmi = data['制造业PMI'][['制造业采购经理指数', '生产指数', '新订单指数', '新出口订单指数']]
ax4.plot(df_pmi.index, df_pmi.iloc[:,0], marker='o', label='PMI')
ax4.plot(df_pmi.index, df_pmi.iloc[:,1], marker='s', label='生产')
ax4.plot(df_pmi.index, df_pmi.iloc[:,2], marker='^', label='新订单')
ax4.plot(df_pmi.index, df_pmi.iloc[:,3], marker='d', label='新出口订单')
ax4.axhline(y=50, color='gray', linestyle='--', linewidth=0.8)
ax4.set_title('制造业PMI及其分项')
ax4.set_ylabel('指数')
ax4.legend()
ax4.grid(True, linestyle='--', alpha=0.6)

# 5. 工业企业利润与库存增速
ax5 = fig.add_subplot(3, 2, 5)
df_indicator = data['工业企业主义经济指标']
# 利润总额累计增长、产成品存货增减（累计增长？这里存货增减是同比？）
# 注意：表中“产成品存货_增减”列是同比增速（%），直接使用
ax5.plot(df_indicator.index, df_indicator['利润总额_累计增长'], marker='o', label='利润总额累计增长%')
ax5.plot(df_indicator.index, df_indicator['产成品存货_增减'], marker='s', label='产成品存货同比%')
ax5.set_title('工业企业利润与产成品存货增速')
ax5.set_ylabel('%')
ax5.legend()
ax5.grid(True, linestyle='--', alpha=0.6)

# 6. 出口与进口增长
ax6 = fig.add_subplot(3, 2, 6)
df_trade = data['进出口价格指标']
ax6.plot(df_trade.index, df_trade['出口总值同比增长(%)'], marker='o', label='出口同比%')
ax6.plot(df_trade.index, df_trade['进口总值同比增长(%)'], marker='s', label='进口同比%')
ax6.set_title('进出口总值同比增速')
ax6.set_ylabel('%')
ax6.legend()
ax6.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('工业新旧动能转换分析.png', dpi=300)
plt.show()