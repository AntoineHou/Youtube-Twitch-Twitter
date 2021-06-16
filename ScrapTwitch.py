import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from youtubesearchpython import ChannelsSearch
import time 
import numpy as np
from itertools import groupby
import stweet as st

df=pd.read_csv('Chess - most watched Twitch channels - SullyGnome.csv')
df["LinkTW"]="https://www.twitch.tv/"+df["Channel"]+"/about"

aa=0
listchannel=[]
twitter=[]

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
    tw=[]
    for link in url :
        if "youtube" in link :
            yt.append(link)
        if "twitter" in link :
            tw.append(link)
        else :
            yt=yt
            tw=tw
    listchannel.append(yt)
    twitter.append(tw)
    aa=aa+1
    
df=df.assign(YT=listchannel)
df['YT'] = df['YT'].apply(lambda x: list(set(x)))
df=df.assign(TWI=twitter)
df['TWI'] = df['TWI'].apply(lambda x: list(set(x)))

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

ListTwi=[]
NBTweet=[]
NBFollower=[]
TweeID=[]


for twi in dff["TWI"] : 
    raw=[]
    for item in twi : 
        if "www" in item :
            a=item.replace('https://www.twitter.com/','')
            a=a.lower()
            raw.append(a)
        else :
            a=item.replace('https://twitter.com/','')
            a=a.lower()
            raw.append(a)
    raw=list(set(raw))
    if len(raw) == 0:
        ListTwi.append(np.nan)
        NBTweet.append(np.nan)
        NBFollower.append(np.nan)
        TweeID.append(np.nan)
    else :
        ListTwi.append(raw[0])
        get_users_task = st.GetUsersTask(raw)
        users_collector = st.CollectorUserOutput()
        
        st.GetUsersRunner(
            get_user_task=get_users_task,
            user_outputs=[users_collector]
        ).run()
        users = users_collector.get_scrapped_users()
        users=users[0]
        NBTweet.append(users.statuses_count)
        NBFollower.append(users.followers_count)
        TweeID.append(users.rest_id_str)

        
dff["TweetName"]=ListTwi
dff["NBTweet"]=NBTweet
dff["NBFollower"]=NBFollower
dff["TweeID"]=TweeID


dff.to_csv('ExempleChann.csv',index=False)
