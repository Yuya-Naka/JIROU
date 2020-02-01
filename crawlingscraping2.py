import pandas as pd
import numpy as np
from IPython.display import display
from tqdm import tqdm
import os
import re
from bs4 import BeautifulSoup
import requests
import time

'''
for n in range(1,72):
    url = 'https://ramendb.supleks.jp/search?order=point&type=0&station-id=0&tags=3&page={}'.format(n)
    result = requests.get(url)
    c = result.content
    with open('htmls/jiro_{}.html'.format(n),'w') as f:
        f.write(c.decode('UTF-8'))
        time.sleep(3)
'''

files = sorted(['htmls/'+ x for x in os.listdir('htmls/') if re.search('html$',x)])
file = files[0]
print('23行',file)

def check_business_status(s):
    if s.find('span',{'class':'status_plate moved'}):
        ret = "移転"
    elif s.find('span',{'class':'status_plate retire'}):
        ret = "閉店"
    else:
        ret = "営業"
    return ret

df=pd.DataFrame()

for file in files:
    with open(file,'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    result_dic = dict()
    summary = soup.find('div', {'class':'wrap'})
    for ind, s in enumerate(summary.find_all('li',{'class':'border-box'})):
        result_dic[ind] = dict()
        result_dic[ind]['name'] = s.find('div',{'class':'name'}).find('h4').text
        result_dic[ind]['pref'] = s.find('div',{'class':'area'}).find('a').text
        result_dic[ind]['review_score'] = s.find('div',{'class':'point-val'}).text
        result_dic[ind]['review_num'] = s.find('div',{'class':'val'}).text
        result_dic[ind]['status'] = check_business_status(s)
        result_dic[ind]['url'] = 'https://ramendb.supleks.jp' + s.find('a',{'class':'bglink'}).get('href')
        tmp_df = pd.DataFrame.from_dict(result_dic, orient='index')
        #print('46行目',tmp_df.shape)
    df = pd.concat([df,tmp_df])

#display(df.shape)
#(1491, 6)
#display(df)
#0               ちばから   千葉県        98.90        568     営業    https://ramendb.supleks.jp/s/4227.html

#print('52',df['status'].value_counts())
#営業    1243
#閉店     248
#print('54',df[df.status=="営業"].pref.value_counts())
# 東京都     342
#埼玉県     161
#神奈川県     96

'''
for row in tqdm(df[df['status']=='営業'].itertuples()):
    name = row.name
    #print('59行',name)
    #59行 ラーメン二郎 ひばりヶ丘駅前店
    url = row.url
    result = requests.get(url)
    c = result.content
    with open('htmls/shops/{}.html'.format(name.replace("/","")),'w') as f:
        f.write(c.decode('UTF-8'))
        time.sleep(1)
'''

files = sorted(['htmls/shops/'+ x for x in os.listdir('htmls/shops/') if re.search('html$',x)])
file = files[0]
print('69行',file)

result_dic = {}
for file in files:
    #print('74行',file) #htmls/shops/麺歩 バガボンド.html
    with open(file,'r',encoding="utf-8",errors='ignore') as f:
        soup = BeautifulSoup(f.read(),'lxml')
    url = 'https://ramendb.supleks.jp' + soup.find('h1').find('a').get('href')
    result_dic[url] = soup.find('div',{'class':'datas'}).find('span',{'itemprop':'address'}).text.split('このお店は')[0]


address_df = pd.DataFrame.from_dict(result_dic, orient='index').reset_index()
address_df.columns = ['url', 'address']
#print('83行',address_df.head()) #0   https://ramendb.supleks.jp/s/80400.html             北海道札幌市中央区北2条西3丁目 敷島ビル B1F

active_df = df[df.status == '営業'].reset_index(drop=True)
active_df = active_df.merge(address_df)
#print('87行',active_df.head())#0              ちばから   千葉県        98.90        568     営業   https://ramendb.supleks.jp/s/4227.html           〒290-0072 千葉県市原市西国分

active_df.to_csv("active_shops.csv", index=False)


def coordinate(address, url='http://www.geocoding.jp/api/'):
    
    payload = {'q': address}
    html = requests.get(url, params=payload)
    soup = BeautifulSoup(html.content, "html.parser")
    if not soup.find('lat'):
        print(f"Invalid address submitted. {address}")
        return '0', '0'
    latitude = soup.find('lat').string
    longitude = soup.find('lng').string
    return latitude, longitude

addresses = active_df.address.values
print("111行",addresses)# ['〒290-0072 千葉県市原市西国分寺台1丁目3番16号' '〒188-0001 東京都西東京市谷戸町3-27-24 ひばりヶ丘プラザ1F''〒231-0033 神奈川県横浜市中区長者町6-94' ... '〒350-1306 埼玉県狭山市富士見1-28-7 ゲオ狭山店前''〒102-0071 東京都千代田区富士見2-12-16' '東京都港区東新橋1-2-11 三陸ビル1F']addressesの値のリストが返ってくる

'''
with open('address_lat_lon.tsv', 'w') as f:
    for address in tqdm(addresses):
        lat, lon = coordinate(address)
        f.write(f"{address}\t{lat}\t{lon}\n")
        time.sleep(10)
'''
address_df = pd.read_csv("address_lat_lon.tsv", sep='\t',names=["address","lat","lon"])
print('120行',address_df.shape)#120行 (1240, 3)
print('121行',address_df.head())#0   〒290-0072 千葉県市原市西国分寺台1丁目3番16号  35.501649  140.112527


def clean_address(ad):
    ad = re.sub("〒[0-9]{3}\-[0-9]{4} ","",ad)
    ad = ad.split(" ")[0]
    return ad


fail_df = address_df.query("lat == 0")
fail_df.loc[:,"cleansed_address"] = fail_df.address.apply(lambda x:clean_address(x))
print('131行',fail_df.head())#13   〒153-0041 東京都目黒区駒場4-6-8 佐藤ビル1F  0.0  0.0      東京都目黒区駒場4-6-8



address_fail = fail_df.cleansed_address

'''
with open('address_lat_lon_fail.tsv', 'w') as f:
    for address in tqdm(address_fail):
        lat, lon = coordinate(address)
        f.write(f"{address}\t{lat}\t{lon}\n")
        time.sleep(10)
'''

address_df = pd.read_csv("address_lat_lon.tsv", sep='\t',names=["address","lat","lon"])
print('142行',address_df.shape)#(1240, 3)
display(address_df.head())

fail_df = address_df[address_df.lat == 0]
fail_df.loc[:,"cleansed_address"] = fail_df.address.apply(lambda x:clean_address(x))
print('147行',fail_df.shape)
display(fail_df.head())#  address lat  lon  cleansed_address 〒153-0041 東京都目黒区駒場4-6-8 佐藤ビル1F  0.0  0.0      東京都目黒区駒場4-6-8
fail_result_df = pd.read_csv("address_lat_lon_fail.tsv", sep="\t",names=["cleansed_address","lat","lon"])
fail_df = fail_df[["address","cleansed_address"]].merge(fail_result_df,on="cleansed_address")[["address","lat","lon"]]
print('151行',fail_df.shape)# (152, 3)
display(fail_df.head())# 〒153-0041 東京都目黒区駒場4-6-8 佐藤ビル1F  35.664005  139.678508

merged_address_df = pd.concat([address_df[address_df.lat !=0],fail_df[fail_df.lat !=0]])
print('163行',merged_address_df.shape)# (1357, 3)
display(merged_address_df.head())#  address  lat  lon 〒290-0072 千葉県市原市西国分寺台1丁目3番16号  35.501649  140.112527
merged_address_df.to_csv("merged_address_df.csv")

active_df = pd.read_csv("active_shops.csv")
print('167行',active_df.shape)# (1240, 7)
display(active_df.head())# name pref review_score review_num status url   address


active_df = active_df.merge(merged_address_df, on="address", how="right")
#print(active_df.duplicated().any()) #DataFrameに重複しているものがあるかチェックする。
active_df=active_df.drop_duplicates(['name'])#重複している場所を削除している name列でチェックしている
print('175行',active_df.shape)# 
display(active_df.head())#name pref review_score  ...     address    lat lon

active_df.to_csv("active_shops_with_latlon.csv")
