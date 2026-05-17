# coding=utf-8

import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time
import json



def getTime():
    return int(round(time.time() * 1000))

#要爬取的网址
url = 'http://data.stats.gov.cn/easyquery.htm?cn=A01'
#读取网页元素，确保一一对应
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0'}  # 浏览器代理
key = {}  # 参数键值对
key['m'] = 'QueryData'
key['dbcode'] = 'hgyd'
key['rowcode'] = 'zb'
key['colcode'] = 'sj'
key['wds'] = '[]'
key['dfwds'] = '[{"wdcode":"zb","valuecode":"A0B01"}]'
key['k1'] = str(getTime())
key['h']=1
r = requests.get(url, headers=headers, params=key)

#读取json文件，但是还在内存中
js = json.loads(r.text)


length = len(js['returndata']['datanodes'])
with open("dataJs.json",'w') as f:
    f.write(json.dumps(js,ensure_ascii=False,indent=4))
print(length)
#使用
def getList():
    List = []
    for i in range(length):
        str_data = js['returndata']['datanodes'][i]['data']['strdata']
        try:
            # 如果是JSON格式的字符串
            value = json.loads(str_data)
            List.append(value)
        except json.JSONDecodeError:
            # 如果不是JSON，尝试其他方法
            try:
                value = eval(str_data)
                List.append(value)
            except:
                List.append(None)
    return List

lst = getList()

cnames = []
try:
    wdnodes =js["returndata"]["wdnodes"]
    for item in wdnodes:
        nodes = item.get("nodes", [])
        for node in nodes:
            if "cname" in node:
                cnames.append(node["cname"])
except KeyError as e:
    print(f"JSON 结构不符合预期，缺少键值: {e}")

cnames=cnames[:-13]
lst = getList()

array = np.array(lst).reshape(len(cnames), 13)
df = pd.DataFrame(array)
df = df.drop(columns=[0])

#做标签
times=0
colunm=[]
year=2026
mounth = 1
for x in range(1,2):
    for y in range(1,13):
        if(mounth<1):
            mounth=12
            year=2025
        colunm.append(str(year) + '年' + str(mounth) + '月')
        mounth-=1
    year+=1
times+=1

df.columns = colunm
if len(cnames) == len(df):
    df.index = cnames  # 直接赋值列表即可，Pandas 会自动转换
else:
    raise ValueError("cnames 的长度必须与 DataFrame 的行数一致")

df.to_excel('../源数据/制造业PMI.xlsx')
