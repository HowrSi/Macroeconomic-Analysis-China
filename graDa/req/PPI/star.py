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
key['dfwds'] = '[{"wdcode":"zb","valuecode":"A010801"}]'
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


print(lst)
array = np.array(lst).reshape(3, 13)
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
df.index=["工业生产者出厂价格指数(上年同月=100)",
          "生产资料工业生产者出厂价格指数(上年同月=100)",
          "生活资料工业生产者出厂价格指数(上年同月=100)"
          ]
df.to_excel('../源数据/PPI.xlsx')
print(type(df))