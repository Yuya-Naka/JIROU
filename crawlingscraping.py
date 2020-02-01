import pandas as pd
import numpy as np
from IPython.display import display
from tqdm import tqdm
import os,re,requests,time
from bs4 import BeautifulSoup

for n in range(1,72):
    url='https://ramendb.supleks.jp/search?order=point&type=0&station-id=0&tags=3&page={}'.format(n)
    result=requests.get(url)
    c=result.content

    with open('htmls/jiro_{}.html'.format(n),'w') as f:
        f.write(c.decode('UTF-8'))
        time.sleep(3)


files = sorted(['htmls/'+ x for x in os.listdir('htmls/') if re.search('html$',x)])
print('files',files)


def check_business_status(s):
    if s.find('span',{'class':'status_plate moved'}):
        ret = "移転"
    elif s.find('span',{'class':'status_plate retire'}):
        ret="閉店"
    else:
        ret="営業"
    return ret


df=pd.DataFrame()

for file in files:
    with open(file, 'r') as f:
        soup=BeautifulSoup(f.read(),'lxml')
    result_dic=dict()
    summary=soup.find('dvi',{'class':'wrap'})

    for ind,s in enumerate(summary.find_all('li',{'class':'border-box'})):
        result_dic[ind]=dict()
        result_dic[ind]['name']=s.find('div',{'class':'name'}).find('h4').text
        result_dic[ind]['pref']=s.find('div',{'class':'area'}).find('a').text
        result_dic[ind]['review_score']s.find('div',{'class':'point-val'}).text
        result_dic[ind]['review_num']=s.find('div',{'class':'val'}).text
        result_dic[ind]['status'] = check_business_status(s)
        result_dic[ind]['url']='https://ramendb.supleks.jp'+s.find('a',{'class':'bglink'}).get('href')
        tmp_df=pd.DataFrame.from_dict(result_dic, orient='index')
    df=pd.concat([df,tmp_df])

display(df.shape)
display(df.head())
df['status'].value_counts()
df[df.status=='営業'].pref.value_counts()

for row in tqdm(df[df['status']=='営業'].itertuples()):
    name=row.name
    url=row.url
    result=requests.get(url)
    c=result.content
    with open('htmls/shops/{}.html'.format(name.replace("/","")),'w') as f:
        f.write(c.decode('UTF-8'))
        time.sleep(1)

files=sorted(['htmls/shops/' + x for x in os.listdir('htmls/shops/')])
print('files',files)

for file in files:
    with open(file, 'r') as f:
        soup=BeautifulSoup(f.read(), 'lxml')
    url='https://ramendb.supleks.jp'+soup.find('h1').find('a').get('href')
    result_dic[url]=soup.find('div',{'class':datas}).find('span',{'itemprop':'address'}).text.split('このお店は')[0]

address_df=pd.DataFrame.from_dict(result_dic, orient='index').reset_index()
address_df.columns=['url', 'address']
print(address_df.head())

active_df=df[df.status=='営業'],reset_index(drop=True)
active_df=active_df.mearge(address_df)
print('acctive_df',acctive_df)

active_df.to_csv("active_shops.csv", index=False)

def coordinate(address, url='http://www.geocoding.jp/api/'):

    payload={'q':address}
    html=requests.get(url, params=payload)
    soup=BeautifulSoup(html.content, "html.parser")

    if not soup.find('lat'):
        print(f"Invalid address submitted. {address}"))
        return '0','0'
    latitude=soup.find('lat').string
    longitude=soup.find('lng').string
    return latitude,longitude

address=active_df.address.values

with open('address_lat_lon.tsv','w') as f:
    for address in tqdm(addresses):
        lat,lon=coordinate(address)
        f.write(f"{address}\t{lat}\t{lon}\n")
        time.sleep(10)

address_df == pd.read_csv("address_lat_lon.tsv", sep='\t',names=["address","lat","lon"])
print(address_df.shape)
print(address_df.head())

