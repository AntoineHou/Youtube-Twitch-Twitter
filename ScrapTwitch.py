import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from youtubesearchpython import ChannelsSearch
import time 
import numpy as np
from itertools import groupby

df=pd.read_csv('Channel.csv')
df["LinkTW"]="https://www.twitch.tv/"+df["Channel"]+"/about"

aa=0
listchannel=[]

while aa<len(df) :
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(df["LinkTW"][aa])
    time.sleep(5)
    data = driver.page_source
    driver.close()
    soup = BeautifulSoup(data, 'html.parser')
    url=[]
    for a in soup.find_all("a", href=True) :
        url.append(a['href'])
    yt=[]
    for link in url :
        if "youtube" in link :
            yt.append(link)
        else :
            yt=yt
    listchannel.append(yt)
    aa=aa+1
    
df=df.assign(YT=listchannel)
df['YT'] = df['YT'].apply(lambda x: list(set(x)))

bb=0
df["YT1"] = np.nan


while bb<len(df) :
    for link in df['YT'][bb] :
        separators = set(',')
        result = [''.join(group) for k, group in groupby(str(link), key=lambda x: x not in separators) if k]
        df['YT1'][bb] = result
    bb=bb+1


df["Name"] = np.nan
df["Vid"] = np.nan
df["Sub"] = np.nan
df["ID"] = np.nan

df1=df[df.YT1.isnull()]
df2 = df[df['YT1'].notna()]
df2.reset_index(drop=True, inplace=True)

cc=0

while cc<len(df2) :
    lien=str(df2['YT1'][cc])
    if "?view_as=subscriber" in lien :
        lien=lien.replace("?view_as=subscriber", "")   
    elif "/videos" in lien :
        lien=lien.replace("/videos","")
    elif "?sub_confirmation=1" in lien :
        lien=lien.replace("?sub_confirmation=1", "") 
    chann=ChannelsSearch(lien, limit=5)
    chann=dict(chann.result())
    chann=chann['result']
    if len(chann)>0 :
        df2["Name"][cc]=chann[0]['title']
        df2["Vid"][cc] =chann[0]['videoCount']
        df2["Sub"][cc] =chann[0]['subscribers']
        df2["ID"][cc] =chann[0]['id']
    else :
        pass
    cc=cc+1

dff=pd.concat([df1,df2])
dff.to_csv('Channel.csv',index=False)
