import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from youtubesearchpython import ChannelsSearch
import time 
import numpy as np
from itertools import groupby
import stweet as st
import re 
import json

df=pd.read_csv('political_channel.csv')
df["LinkTW"]="https://www.twitch.tv/"+df["Channel"]+"/about"

aa=0
listchannel=[]
twitter=[]

while aa<len(df) :
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(df["LinkTW"][aa])
    time.sleep(1)
    data = driver.page_source
    driver.close()
    soup = BeautifulSoup(data, 'html.parser')
    url=[]
    for a in soup.find_all("a", href=True) :
        url.append(a['href'])
    tw=[]
    for link in url :
        if "twitter" in link :
            tw.append(link)
        else :
            tw=tw
    twitter.append(tw)
    aa=aa+1
    
df=df.assign(TWI=twitter)
df['TWI'] = df['TWI'].apply(lambda x: list(set(x)))


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
    elif "c/" in lien :
        lien=lien.replace("c/", "") 
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

df=df.set_index(["Channel"])

dictionnary={}

for chann in df["YT2"].iteritems() : 
    if len(str(chann[1]))>3 :
        a=ChannelsSearch(chann[1], limit=5)
        a=dict(a.result())
        try : 
            a=a['result']
            b=[(a[0]['title']),(a[0]['videoCount']),(a[0]['subscribers']),(a[0]['id'])]
            dictionnary[chann[0]]=b
        except IndexError :
            dictionnary[chann[0]]=[0,0,0,0]
    else :
        dictionnary[chann[0]]=[0,0,0,0]

mock_df=pd.DataFrame(dictionnary).transpose().reset_index()
mock_df.columns=["Channel","Name2","Vid2","Sub2","ID2"]

dff["Name2"]=mock_df["Name2"]
dff["Vid2"]=mock_df["Vid2"]
dff["Sub2"]=mock_df["Sub2"]
dff["ID2"]=mock_df["ID2"]


ListTwi=[]
NBTweet=[]
NBFollower=[]
TweeID=[]


for twi in dff["TWI"] : 
    raw=[]
    for item in twi : 
        item=item.lower()
        if "status" in item : 
            pass 
        else : 
            match = re.search(r'^.*?\btwitter\.com/@?(\w{1,15})(?:[?/,].*)?$',item)
            a=match.group(1)
            raw.append(a)        
    raw=list(set(raw))
    if len(raw) == 0:
        ListTwi.append(np.nan)
        NBTweet.append(np.nan)
        NBFollower.append(np.nan)
        TweeID.append(np.nan)
    else :
        if "lang" in raw[0] :
            raw[0]=raw[0].split("?",1)[0]
        ListTwi.append(raw[0])
        get_users_task = st.GetUsersTask(raw)
        users_collector = st.CollectorUserOutput()
        st.GetUsersRunner(
            get_user_task=get_users_task,
            user_outputs=[users_collector]
        ).run()
        users = users_collector.get_scrapped_users()
        if len(users) != 0 :
            users=users[0]
            NBTweet.append(users.statuses_count)
            NBFollower.append(users.followers_count)
            TweeID.append(str(users.rest_id_str)+"_")
        else : 
            NBTweet.append(np.nan)
            NBFollower.append(np.nan)
            TweeID.append(np.nan)
    print(raw)

        
dff["TweetName"]=ListTwi
dff["NBTweet"]=NBTweet
dff["NBFollower"]=NBFollower
dff["TweeID"]=TweeID

dff.to_json('temp.json', orient='records', lines=True)