#coding=utf-8
import pandas as pd

# 读取Excel文件
file_path = '../源数据/制造业PMI.xlsx'
df = pd.read_excel(file_path)
df = pd.DataFrame(df)

# 填充缺失值（同行其他值的平均值）
for index, row in df.iterrows():
    # 获取当前行非空值
    non_null_values = row[1:].dropna()  # 跳过第一列(Unnamed: 0)
    if len(non_null_values) > 0:
        # 计算平均值
        mean_value = non_null_values.mean()
        # 填充缺失值
        df.loc[index, df.columns[1:][df.loc[index, df.columns[1:]].isnull()]] = mean_value

#转置列表，以方便后续的数据分析
def melt():
    df_transposed = df.set_index('Unnamed: 0').T
    # 第二步：重置索引，将时间变成一列
    df_transposed = df_transposed.reset_index()
    # 第三步：重命名列，将"index"改为"月份"
    df_transposed.rename(columns={'index': '月份'}, inplace=True)

    df_transposed['月份'] = pd.to_datetime(df_transposed['月份'], format='%Y年%m月')

    output_path = '../数据清洗/制造业PMI.xlsx'
    df_transposed.to_excel(output_path, index=False)
melt()

