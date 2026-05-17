#coding=utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# --- 核心修复 1: 强制设置控制台输出为 UTF-8 ---
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')  # 静默执行，不显示切换信息

# 设置绘图字体 (防止图表中文乱码)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("正在加载数据...")
print(f"当前工作目录: {os.getcwd()}")  # 打印当前目录，方便你确认文件位置

# 文件列表 (确保这些文件就在当前脚本所在的文件夹内)
# 注意：文件名必须完全一致，包括后缀名
file_mapping = {
    '服务业生产指数': '../req/数据清洗/服务生产指数.xlsx',
    'PPI': '../req/数据清洗/PPI.xlsx',
    '工业分类': '../req/数据清洗/三大类工业.xlsx',
    '货币供应': '../req/数据清洗/货币供应量.xlsx',
    '失业率': '../req/数据清洗/失业率.xlsx',
    '非制造业PMI': '../req/数据清洗/非制造业PMI.xlsx',
    'PPIRM': '../req/数据清洗/PPIRM.xlsx',
    '制造业PMI': '../req/数据清洗/制造业PMI.xlsx',
    'CPI': '../req/数据清洗/居民消费指数.xlsx',
    '进出口': '../req/数据清洗/进出口价格指标.xlsx',
    '工业企业': '../req/数据清洗/工业企业主义经济指标.xlsx' ,
    '失业率' : '../req/数据清洗/失业率.xlsx'# 注：文件名疑似有错别字，按上传文件名处理
}

data = {}
loaded_count = 0

for name, filename in file_mapping.items():
    full_path = os.path.join(os.getcwd(), filename)

    if not os.path.exists(full_path):
        # 核心修复 2: 去掉特殊符号，使用纯文本报错
        print(f"[错误] 未找到文件: {filename}")
        print(f"       请在文件夹 '{os.getcwd()}' 中确认该文件是否存在。")
        continue

    try:
        df = pd.read_excel(full_path)

        # 智能识别日期列
        date_col = None
        for col in df.columns:
            col_str = str(col)
            if '月份' in col_str or '日期' in col_str or '时间' in col_str or '年' in col_str:
                date_col = col
                break

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            # 如果转换成功，设为索引
            if not df[date_col].isna().all():
                df.set_index(date_col, inplace=True)
            else:
                # 如果日期列全是空，尝试用第一列
                df.set_index(df.columns[0], inplace=True)
                df.index = pd.to_datetime(df.index, errors='coerce')
        else:
            # 没有明显的日期列名，强制尝试第一列
            first_col = df.columns[0]
            df[first_col] = pd.to_datetime(df[first_col], errors='coerce')
            if not df[first_col].isna().all():
                df.set_index(first_col, inplace=True)

        data[name] = df
        # 核心修复 3: 去掉特殊符号
        print(f"[成功] {name} 已加载 (行数: {len(df)})")
        loaded_count += 1

    except Exception as e:
        # 核心修复 4: 安全地打印错误信息
        print(f"[失败] {name} 加载出错: {str(e)}")

if loaded_count == 0:
    print("\n严重错误: 没有成功加载任何数据文件。")
    print("请检查：")
    print("1. Excel文件是否已复制到脚本所在目录？")
    print("2. 文件名是否与代码中的完全一致？")
    sys.exit(1)

print(f"\n总共成功加载 {loaded_count} 个数据集。开始分析...")

col_total = None
col_youth = None




# --- 数据整合与分析 ---
gdp_proxy = pd.DataFrame()

# 1. 提取工业增加值
if '工业分类' in data:
    df_ind = data['工业分类']
    # 寻找包含"制造业"和"增长/增速"的列
    target_col = None
    for col in df_ind.columns:
        if '制造业' in str(col) and ('增长' in str(col) or '增速' in str(col)):
            target_col = col
            break
    if not target_col:
        # 备选策略：取数值型的第一列
        num_cols = df_ind.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            target_col = num_cols[0]

    if target_col:
        gdp_proxy['工业增加值'] = df_ind[target_col]

# 2. 提取服务业
if '服务业生产指数' in data:
    df_ser = data['服务业生产指数']
    target_col = None
    for col in df_ser.columns:
        if '同比' in str(col) or '增速' in str(col):
            target_col = col
            break
    if not target_col:
        num_cols = df_ser.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            target_col = num_cols[0]

    if target_col:
        gdp_proxy['服务业增加值'] = df_ser[target_col]

# 计算合成指标
if '工业增加值' in gdp_proxy.columns and '服务业增加值' in gdp_proxy.columns:
    gdp_proxy = gdp_proxy.dropna()
    if len(gdp_proxy) > 0:
        gdp_proxy['合成经济增速'] = gdp_proxy['工业增加值'] * 0.4 + gdp_proxy['服务业增加值'] * 0.6



# --- 绘图 ---
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('2025-2026 中国经济增长趋势与驱动因素分析', fontsize=16, fontweight='bold')


# 图1: 经济增长
ax1 = axes[0, 0]
if '合成经济增速' in gdp_proxy.columns:
    ax1.plot(gdp_proxy.index, gdp_proxy['工业增加值'], marker='o', label='制造业增加值')
    ax1.plot(gdp_proxy.index, gdp_proxy['服务业增加值'], marker='s', label='服务业生产指数')
    ax1.plot(gdp_proxy.index, gdp_proxy['合成经济增速'], marker='^', linestyle='--', color='red', label='合成经济景气度')
    ax1.set_title('供给侧趋势：工业 vs 服务业')
    ax1.set_ylabel('同比增长 (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
else:
    ax1.text(0.5, 0.5, '数据不足，无法绘制合成指数', transform=ax1.transAxes, ha='center')

# 图2: 价格指数
ax2 = axes[0, 1]
if 'PPI' in data and 'CPI' in data:
    ppi_df = data['PPI']
    cpi_df = data['CPI']

    # 智能找列
    ppi_col = next((c for c in ppi_df.columns if '出厂' in str(c) or 'PPI' in str(c)), ppi_df.columns[0])
    cpi_col = next((c for c in cpi_df.columns if '消费' in str(c) or 'CPI' in str(c)), cpi_df.columns[0])

    # 处理指数转涨跌幅
    ppi_vals = ppi_df[ppi_col] - 100 if ppi_df[ppi_col].mean() > 90 else ppi_df[ppi_col]
    cpi_vals = cpi_df[cpi_col] - 100 if cpi_df[cpi_col].mean() > 90 else cpi_df[cpi_col]

    ax2.bar(ppi_df.index, ppi_vals, width=20, alpha=0.6, label='PPI', color='orange')
    ax2.plot(cpi_df.index, cpi_vals, marker='d', color='green', label='CPI')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.set_title('价格体系：PPI 与 CPI')
    ax2.legend()
else:
    ax2.text(0.5, 0.5, 'PPI或CPI数据缺失', transform=ax2.transAxes, ha='center')

# 图3: 外贸与货币
ax3 = axes[1, 0]
if '进出口' in data and '货币供应' in data:
    trade_df = data['进出口']
    money_df = data['货币供应']

    export_col = next((c for c in trade_df.columns if '出口' in str(c)), None)
    m2_col = next((c for c in money_df.columns if 'M2' in str(c) or '货币' in str(c)), None)

    if export_col and m2_col:
        ax3_twin = ax3.twinx()
        ax3.bar(trade_df.index, trade_df[export_col], alpha=0.6, label='出口增速', color='purple')
        ax3.set_ylabel('出口增速 (%)', color='purple')

        ax3_twin.plot(money_df.index, money_df[m2_col], color='blue', marker='x', label='M2增速')
        ax3_twin.set_ylabel('M2增速 (%)', color='blue')

        ax3.set_title('需求侧：外贸与货币')
        # 合并图例
        lines_1, labels_1 = ax3.get_legend_handles_labels()
        lines_2, labels_2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(lines_1 + lines_2, labels_1 + labels_2)
    else:
        ax3.text(0.5, 0.5, '未找到出口或M2列', transform=ax3.transAxes, ha='center')
else:
    ax3.text(0.5, 0.5, '进出口或货币数据缺失', transform=ax3.transAxes, ha='center')

# 图4: PMI
ax4 = axes[1, 1]
if '制造业PMI' in data:
    pmi_df = data['制造业PMI']
    pmi_col = next((c for c in pmi_df.columns if '采购经理' in str(c) or 'PMI' in str(c)), pmi_df.columns[0])

    ax4.plot(pmi_df.index, pmi_df[pmi_col], marker='o', label='制造业PMI')
    ax4.axhline(y=50, color='red', linestyle='--', label='荣枯线 (50)')
    ax4.set_title('制造业PMI')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
output_name = 'economic_analysis_result.png'
plt.savefig(output_name, dpi=300, bbox_inches='tight')
print(f"\n[完成] 图表已保存为: {output_name}")

# --- 文字总结 ---
print("\n" + "=" * 50)
print("分析摘要")
print("=" * 50)
if '合成经济增速' in gdp_proxy.columns and len(gdp_proxy) > 1:
    val = gdp_proxy['合成经济增速'].iloc[-1]
    print(f"1. 最新合成经济增速: {val:.2f}%")
if 'PPI' in data:
    df = data['PPI']
    col = next((c for c in df.columns if '出厂' in str(c)), df.columns[0])
    print(f"2. 最新PPI指数: {df[col].iloc[-1]:.1f}")
if '制造业PMI' in data:
    df = data['制造业PMI']
    col = next((c for c in df.columns if 'PMI' in str(c) or '采购' in str(c)), df.columns[0])
    print(f"3. 最新制造业PMI: {df[col].iloc[-1]:.1f}")
print("=" * 50)

# 1. 加载失业率数据
file_path = '../req/数据清洗/失业率.xlsx'
if not os.path.exists(file_path):
    # 尝试常见变体文件名
    if os.path.exists('失业.xlsx'):
        file_path = '失业.xlsx'
    else:
        print(f"[错误] 找不到文件 {file_path}，请确认文件在当前目录。")
        sys.exit(1)

try:
    df_unemp = pd.read_excel(file_path)
    # 智能识别日期列
    date_col = None
    for col in df_unemp.columns:
        if '月份' in str(col) or '日期' in str(col) or '时间' in str(col):
            date_col = col
            break
    if not date_col:
        date_col = df_unemp.columns[0]
    df_unemp[date_col] = pd.to_datetime(df_unemp[date_col], errors='coerce')
    df_unemp.set_index(date_col, inplace=True)
    df_unemp = df_unemp.sort_index()
    print(f"[成功] 失业率数据加载完成，时间范围：{df_unemp.index.min()} 至 {df_unemp.index.max()}")

except Exception as e:
    print(f"[失败] 读取失业率文件出错：{e}")
    sys.exit(1)

# 2. 识别关键列
# 寻找包含 "调查失业率" (总体) 和 "16-24岁" (青年) 的列
col_total = None
col_youth = None

for col in df_unemp.columns:
    col_name = str(col)
    if '调查失业率' in col_name and '16-24' not in col_name and '不含在校' not in col_name:
        col_total = col
    if '16-24' in col_name or '青年' in col_name:
        col_youth = col

# 如果没找到精确匹配，尝试模糊匹配数值列
if not col_total:
    num_cols = df_unemp.select_dtypes(include=['float', 'int']).columns
    if len(num_cols) >= 1:
        col_total = num_cols[0]  # 假设第一列数值是总体
    if len(num_cols) >= 2:
        col_youth = num_cols[1]  # 假设第二列数值是青年

if not col_total:
    print("[错误] 无法在文件中识别出失业率数据列。请检查Excel表头。")
    sys.exit(1)

print(f"识别到的总体失业率列：{col_total}")
print(f"识别到的青年失业率列：{col_youth if col_youth else '未找到'}")

# 3. 绘图
fig, ax = plt.subplots(figsize=(14, 8))

# 绘制总体失业率
ax.plot(df_unemp.index, df_unemp[col_total], marker='o', linewidth=2.5, label='城镇调查失业率 (总体)', color='#2E86AB')
ax.fill_between(df_unemp.index, df_unemp[col_total], alpha=0.2, color='#2E86AB')

# 绘制青年失业率 (如果存在)
if col_youth and col_youth in df_unemp.columns:
    ax.plot(df_unemp.index, df_unemp[col_youth], marker='s', linewidth=2.5, label='16-24岁劳动力失业率 (青年)', color='#D64933',
            linestyle='--')
    ax.fill_between(df_unemp.index, df_unemp[col_youth], alpha=0.1, color='#D64933')

    # 标注最新值
    last_idx = df_unemp.index[-1]
    ax.text(last_idx, df_unemp[col_youth].iloc[-1] + 0.5, f'{df_unemp[col_youth].iloc[-1]:.1f}%',
            color='#D64933', fontsize=12, fontweight='bold', ha='center')

# 标注总体最新值
last_idx = df_unemp.index[-1]
ax.text(last_idx, df_unemp[col_total].iloc[-1] + 0.5, f'{df_unemp[col_total].iloc[-1]:.1f}%',
        color='#2E86AB', fontsize=12, fontweight='bold', ha='center')

# 添加警戒线
ax.axhline(y=5.5, color='gray', linestyle=':', label='政府调控目标 (~5.5%)')
ax.axhline(y=10.0, color='orange', linestyle=':', alpha=0.7, label='青年失业警戒线 (参考)')

# 图表装饰
ax.set_title('2025-2026 中国就业市场形势分析：总体稳定 vs 青年压力', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('失业率 (%)', fontsize=12)
ax.set_xlabel('时间', fontsize=12)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, which='both', linestyle='--', alpha=0.6)

# 格式化X轴日期
fig.autofmt_xdate()

# 保存
output_name = 'employment_analysis_chart.png'
plt.savefig(output_name, dpi=300, bbox_inches='tight')
print(f"\n[完成] 就业分析图表已保存为：{output_name}")

# 4. 简要文字结论
print("\n" + "=" * 50)
print("就业形势摘要")
print("=" * 50)
total_rate = df_unemp[col_total].iloc[-1]
print(f"1. 总体失业率：{total_rate:.1f}% (通常5.0%-5.5%视为合理区间)")

if col_youth and col_youth in df_unemp.columns:
    youth_rate = df_unemp[col_youth].iloc[-1]
    gap = youth_rate - total_rate
    print(f"2. 青年失业率：{youth_rate:.1f}% (显著高于总体水平)")
    print(f"3. 结构性矛盾：青年与总体失业率差距达 {gap:.1f} 个百分点，显示年轻人就业压力巨大。")
    if youth_rate > 15:
        print("   [警示] 青年失业率处于高位，可能抑制未来消费信心和住房需求。")
else:
    print("2. 未检测到分年龄段数据，无法分析结构性矛盾。")

print("=" * 50)