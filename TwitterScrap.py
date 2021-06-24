import tweepy
import pandas as pd
import time
import json
import datetime

df=pd.read_csv('Chann.csv',dtype={'TweeID': 'str'},engine="python")
Name=list(df["Channel"])

def load_api():
    consumer_key = "Sl1b8kxfpdesC7VBEqufGbrN2"
    consumer_secret = "wAB0UMxyVyNnBSBU4fihQFtQpq94Bdds94n273w8QiaRLY3o7f"
    access_token = "2771537930-b02f7A23GZ389daUggwm14lRzkxbyCY0ZJRUy6l"
    access_token_secret = "zESyM4t7bJ7wlJSEbWdhxNclnW32gP1xhBlpSLPmPWYa1"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,parser=tweepy.parsers.JSONParser())

apit = load_api()

cycle=3
temps=30

def NBTweet (ID) : 
    if str(ID) != "nan" :
        user = apit.get_user(ID)
        statuses_count = user["statuses_count"]
    else :
        statuses_count=0
    return statuses_count

def tweet_scrap(UsersID, NTweet) : 
    Tweet = apit.user_timeline(UsersID,count=NTweet)
    dic={}
    a=0
    while a != len(Tweet) : 
        dic[str(a)]=Tweet[a]
        a=a+1
    return dic
   

Tweets_NB_DF=pd.DataFrame(list(df["Channel"]))
Tweets_NB_DF=Tweets_NB_DF.set_index(0)
New_Tweet_Df=pd.DataFrame(list(df["Channel"]))
New_Tweet_Df=New_Tweet_Df.set_index(0)
Tweet_ID=pd.DataFrame(list(df["Channel"]))
Tweet_ID=Tweet_ID.set_index(0)

df=df.set_index("Channel")

compteur=0

aaa=0
commun=[]
t_coll=[]
while aaa != len(Name) :
    commun.append(0)
    t_coll.append(0)
    aaa=aaa+1
    
Hours=[]

while compteur != cycle:
    listwe=[]
    for twid in df["TweeID"]: 
        if str(twid)=="nan" :
            t=NBTweet(twid)
            listwe.append(t)
        else :
            t=NBTweet(twid[:-1])
            listwe.append(t)
    Tweets_NB_DF[compteur+1]=listwe
    if len(Tweets_NB_DF.columns)>=2 :
        t_coll=[]
        commun=[] 
        ccc=0
        col_p=list(Tweets_NB_DF[compteur]) #précédence
        col_a=list(Tweets_NB_DF[compteur+1]) #actuel 
        while ccc != len(col_p) :
            if col_p[ccc]==col_a[ccc] :
                t_coll.append(0)
                commun.append(0)
                ccc=ccc+1
            else : 
                name=Name[ccc]
                ID=df.loc[name]["TweeID"][:-1]
                info=tweet_scrap(ID,1)
                info=info["0"]["id_str"]
                t_coll.append(info)
                commun.append(1)
                ccc=ccc+1   
    New_Tweet_Df[compteur+1]=commun
    Tweet_ID[compteur+1]=t_coll
    ts = time.time()
    sts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    Hours.append((sts))
    time.sleep(temps)
    compteur=compteur+1       
    print("Temps restant")
    Tweet_ID.to_csv("Tweet_ID.csv")
    print(str(datetime.timedelta(seconds=(cycle-compteur)*temps)))
    print("Cycles restant")
    print(cycle-compteur)

New_Tweet_Df=New_Tweet_Df.transpose()
Tweets_NB_DF=Tweets_NB_DF.transpose()
Tweet_ID=Tweet_ID.transpose()

#l=[New_Tweet_Df,Tweets_NB_DF,Tweet_ID]
#dff=pd.concat(l,keys= ['NewTweet', 'NbTweet', 'TweetID'],axis=1)
#dff=dff.transpose()
#Tweet_ID["Hours"]=Hours
#Tweet_ID=Tweet_ID.set_index("Hours")
#Tweet_ID.to_csv("Tweet_ID.csv")
