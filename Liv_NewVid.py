import requests
from pyyoutube import Api
import pandas as pd
import time 
import datetime
from googleapiclient.discovery import build
import json 
import csv

df=pd.read_csv('ExempleChann.csv',dtype={'TweeID': 'str'},engine="python")


URLT = 'https://api.twitch.tv/helix/streams?user_login='
api = Api(api_key="AIzaSyB2m84TKUf_bpKMpV5IhfrLHKkXiA-ePyA")
authURL = 'https://id.twitch.tv/oauth2/token'
Client_ID = 'gz9d78zfjgqr7syjhve7ogl0gjn9in'
Secret  = 'j0snruq4ut0blhulvgkbgzm7ay6ze4'

api_key="AIzaSyB2m84TKUf_bpKMpV5IhfrLHKkXiA-ePyA"
youtube=build('youtube', 'v3', developerKey=api_key)

consumer_key = "Sl1b8kxfpdesC7VBEqufGbrN2"
consumer_secret = "wAB0UMxyVyNnBSBU4fihQFtQpq94Bdds94n273w8QiaRLY3o7f"
access_token = "2771537930-b02f7A23GZ389daUggwm14lRzkxbyCY0ZJRUy6l"
access_token_secret = "zESyM4t7bJ7wlJSEbWdhxNclnW32gP1xhBlpSLPmPWYa1"
  

AutParams = {'client_id': Client_ID,
             'client_secret': Secret,
             'grant_type': 'client_credentials'
             }

cycle=3
temps=30

def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i

def TwitchLive(url):
    AutCall = requests.post(url=authURL, params=AutParams) 
    access_token = AutCall.json()['access_token']
    head = {
    'Client-ID' : Client_ID,
    'Authorization' :  "Bearer " + access_token
    }
    r = requests.get(url  , headers = head).json()['data'] 
    if r:
        r = r[0]
        if r['type'] == 'live':
            return "live"
        else:
            return "off"
    else:
        return "off"

def Twitch_Info(url):
    Info=[]
    AutCall = requests.post(url=authURL, params=AutParams) 
    access_token = AutCall.json()['access_token']
    head = {
    'Client-ID' : Client_ID,
    'Authorization' :  "Bearer " + access_token
    }
    r = requests.get(url  , headers = head).json()['data'] 
    Info.append(r[0]['game_name'])
    Info.append(r[0]['viewer_count'])
    Info.append(r[0]['title'])
    return Info 

def Twitch_viewers(ident) :
    URL0="http://tmi.twitch.tv/group/user/"
    URL1="/chatters"
    url=URL0+str.lower(ident)+URL1
    r=requests.get(url).json()
    viewers=r["chatters"]["viewers"]
    return viewers

def NbVid (ID) : 
    if str(ID) != "nan" :
        Channel=api.get_channel_info(channel_id=ID)
        Channel=Channel.items[0].to_dict()
    else :
        Channel=0
    return Channel

def Vid_Etag (ID) :
    if str(ID) != "nan" :
        url1="https://www.googleapis.com/youtube/v3/playlistItems?playlistId="
        url2="&key=AIzaSyB2m84TKUf_bpKMpV5IhfrLHKkXiA-ePyA&part=snippet&maxResults=1"
        url=url1+ID+url2
        response=requests.get(url).json()
        a=response["items"][0]["snippet"]["resourceId"]["videoId"]
    else :
        a=0
    return a
    


compteur=0

YTVid=pd.DataFrame(list(df["Channel"]))
TWLIVE=pd.DataFrame(list(df["Channel"]))
Names=list(df["Channel"])
HOURS=[]
Matrix_S=[]
Etags=[]

def live_post_stats(compteur) :
    while compteur != cycle:
        Matrix=dict.fromkeys(list(df["Channel"]),list())
        lisL=[]
        lisY=[]
        for ident in df["Channel"] :
            a=URLT+ident
            b=TwitchLive(a)
            if b == "live" :
                info=[]
                info.append(b)
                info.append(Twitch_Info(a))
                info=list(flatten(info))
                lisL.append(info)
                viewers=Twitch_viewers(ident)
                Matrix[ident]=viewers
            else: 
                info=[]
                info.append(b)
                off=["no game","no viewer","no title"]
                info=info+off            
                lisL.append(info)
        TWLIVE[compteur+1]=lisL
        upload_playlist=[]
        for clef in df["ID"]:
            d=NbVid(clef)
            try :
                e=d['statistics']['videoCount']
                f=d["contentDetails"]["relatedPlaylists"]["uploads"]
                lisY.append(e)  
                upload_playlist.append(f)
            except TypeError : 
                lisY.append(0)  
        YTVid[compteur+1]=lisY
        for key in upload_playlist : 
            b=Vid_Etag(key)
            chan=key
            if b !=0 : 
                if b not in Etags :
                    Etags.append(b)
                    mock_dict=[b,chan]
                    with open("target_video.csv", "a",newline="") as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        writer.writerow(mock_dict)
            else :
                pass
        ts = time.time()
        sts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        HOURS.append((sts))
        Matrix_S.append(Matrix)
        time.sleep(temps)   
        compteur=compteur+1
        with open('Matrix_S.json', 'w') as fout:
            json.dump(Matrix_S , fout)
        print("Temps restant")
        print(str(datetime.timedelta(seconds=(cycle-compteur)*temps)))
        print("Cycles restant")
        print(cycle-compteur)
        
live_post_stats(compteur)

YTNOUV=YTVid
YTVid=YTVid.set_index(0)

df_TW=TWLIVE.set_index(0)    
df_TW=df_TW.transpose()
df_TW.index=HOURS

# Twitch données 

f=df_TW.to_dict()
df2=pd.DataFrame(f)

datat=[]

for name in Names :
    tags = df2[name].apply(pd.Series)
    tags = tags.rename(columns = lambda x : name+str(x))
    datat.append(tags)
    
df_tw=pd.concat(datat,axis=1, keys=Names)

levels=[]
comp_name=0
while comp_name != len(datat) :
    levels.append('Live')
    levels.append('Game')
    levels.append('Viewers')
    levels.append('Name')
    comp_name=comp_name+1

df_tw.columns.set_levels(levels, 1, inplace=True,verify_integrity=False)
df_tw.columns.names = ['Streamer','Info']
df_tw=df_tw.transpose()

df_tw.to_csv("TW2.CSV")

df_tw = pd.read_csv("TW2.csv", index_col=[0,1], skipinitialspace=False)
df_tw=df_tw.transpose()


df_l=df_tw.loc[:, (slice(None), ["Live"])]
df_l.columns = df_l.columns.droplevel("Info")


#Youtube 

Name=[]

for item in YTNOUV[0].iteritems():
    Name.append(item[1])

YTNOUV=YTNOUV.set_index(0)

colonnes=(len(YTNOUV.columns))

for names in Name :
        a=["no post"]
        b=[]
        for row in YTNOUV.loc[names]:
            b.append(row)
            if  len(b) == colonnes:
                c=0
                d=1
                e=0
                f=len(b)
                while e != f-1 :
                    if b[c] == b[d] :
                        a.append("no post")
                    else : 
                        a.append("post")
                    c=c+1
                    d=d+1
                    e=e+1
            else :
                pass
        YTNOUV.loc[names] = a

YTNOUV.columns=HOURS
YTNOUV=YTNOUV.transpose()

#Network Co-Watching 

compt_dic=0

df_=pd.DataFrame(index=Name, columns=Name)
df_=df_.fillna(0)

while compt_dic != len(Matrix_S) :
    Mat=Matrix_S[compt_dic]
    Network={}
    for key , values in Mat.items() : 
        for key2, values2 in Mat.items():
            count=0
            for viewers in values2 :
                if viewers in values :
                    count=count+1
                else :
                    pass 
            dic_inter={key2:count}
            if key not in Network: 
                 Network[key]=dic_inter
            else: 
               Network[key].update(dic_inter)
    compt_dic=compt_dic+1
    AdjencyMatrix=pd.DataFrame(Network)
    df_=df_.add(AdjencyMatrix)

df_=df_/cycle
df_=df_.astype(int)

#Network Viewer Commun : 

df_C=pd.DataFrame(index=Name, columns=Name)
df_C=df_.fillna(0)

res = pd.DataFrame(Matrix_S).to_dict(orient='list')
reseaux={}


for key , value in res.items() :
    key2=key 
    value2=list(flatten(value))
    value2=list(set(value2))
    mock_dic={key2:value2}  
    reseaux.update(mock_dic)

reseaux2={}

for key , values in reseaux.items() : 
        for key2, values2 in reseaux.items():
            count=0
            for viewers in values2 :
                if viewers in values :
                    count=count+1
                else :
                    pass 
            dic_inter={key2:count}
            if key not in reseaux2: 
                 reseaux2[key]=dic_inter
            else: 
               reseaux2[key].update(dic_inter)      
               
AdjencyMatrix2=pd.DataFrame(reseaux2)

# rétention 

ccc=0 #Compteur générale boucle 
new_df=[]


while ccc != len(Name) :
    ddd=0
    m_na=Name[ccc]
    mo_df=df_l[m_na]
    new_column=[]
    for value in res[m_na]:
        value2=list(flatten(value))
        value2=list(set(value2))
    df_mo=pd.DataFrame(index=value2)
    while ddd != len(mo_df) :
        if mo_df[ddd]==0 : 
            df_mo[ddd]=0
            ddd=ddd+1
        else : 
            viewer=Matrix_S[ddd][m_na]
            list_com=[]
            for viewers in df_mo.index:
                if viewers in viewer:
                    list_com.append(1)
                else :
                    list_com.append(0)                    
            df_mo[ddd]=list_com
            ddd=ddd+1
    new_column.append(df_mo)
    for dataframe in new_column :
        a=0
        while a != len(dataframe.columns) :
            aa=dataframe[a].sum()
            if aa != 0 : 
                new_df.append(aa/len(dataframe))
                a=a+1
            else :
                new_df.append(0)
                a=a+1
    ccc=ccc+1
    
composite_list = [new_df[x:x+cycle] for x in range(0, len(new_df),cycle)]

ccc=0

while ccc != len(Name) :
    m_na=Name[ccc]
    df_tw[m_na, "Retention"]=composite_list[ccc]
    ccc=ccc+1

YTNOUV.to_csv("YTNOUV.CSV")
df_l.to_csv("df_l.CSV")
df_tw.to_csv("df_tw.CSV")
df_.to_csv("AdjencyMatrix.csv")
AdjencyMatrix2.to_csv("AdjencyMatrix2.csv")
