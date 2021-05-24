import requests
from pyyoutube import Api
import pandas as pd
import time 
import datetime

df=pd.read_csv('Channel.csv',engine='python')
df.dropna(subset = ["ID"], inplace=True)
df=df.reset_index(drop=True)

URLT = 'https://api.twitch.tv/helix/streams?user_login='
api = Api(api_key="AIzaSyBToNS7k_So6Ci_4sklt2DfK5IXdpN2rEs")
authURL = 'https://id.twitch.tv/oauth2/token'
Client_ID = 'gz9d78zfjgqr7syjhve7ogl0gjn9in'
Secret  = 'j0snruq4ut0blhulvgkbgzm7ay6ze4'

AutParams = {'client_id': Client_ID,
             'client_secret': Secret,
             'grant_type': 'client_credentials'
             }


cycle=24 # Nombre de cycles à réaliser 
temps=900 #Temps entre cycle (secondes)


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


def NbVid (ID) : 
    Channel=api.get_channel_info(channel_id=ID)
    Channel=Channel.items[0].to_dict()
    return Channel['statistics']['videoCount']


compteur=0


YTVid=pd.DataFrame(list(df["Channel"]))
TWLIVE=pd.DataFrame(list(df["Channel"]))
Names=list(df["Channel"])
HOURS=[]

while compteur != cycle+1 :
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
        else: 
            info=[]
            info.append(b)
            off=["no game","no viewer","no title"]
            info=info+off            
            lisL.append(info)
    TWLIVE[compteur+1]=lisL
    for clef in df["ID"]:
        d=NbVid(clef)
        lisY.append(d)
    YTVid[compteur+1]=lisY
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    HOURS.append((st))
    time.sleep(temps)   
    compteur=compteur+1
    print("Temps restant")
    print(str(datetime.timedelta(seconds=(cycle-compteur)*temps)))
    print("Cycles restant")
    print(cycle-compteur)



YTNOUV=YTVid
YTVid=YTVid.set_index(0)

df_TW=TWLIVE.set_index(0)    
df_TW=df_TW.transpose()
df_TW.index=HOURS

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

YTNOUV.to_csv("YTNOUV.CSV")
df_l.to_csv("df_l.CSV")
df_tw.to_csv("df_tw.CSV")



