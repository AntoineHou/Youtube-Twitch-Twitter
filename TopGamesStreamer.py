import json
import requests
import pandas as pd
from pandas.io.json import json_normalize

client_id= "gz9d78zfjgqr7syjhve7ogl0gjn9in"
client_secret= "j0snruq4ut0blhulvgkbgzm7ay6ze4"


access_code = requests.post(("https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials").format(client_id, client_secret))
access_token = json.loads(access_code.text)
access_token = access_token['access_token']
headers = {'client-id':client_id,'Authorization': 'Bearer '+access_token}

games_response = requests.get('https://api.twitch.tv/helix/games/top?first=100', headers=headers)

games_response_json = json.loads(games_response.text)
topgames_data = games_response_json['data']
topgames_df = pd.DataFrame.from_dict(json_normalize(topgames_data), orient='columns')

url="https://api.twitch.tv/helix/streams?first=100&game_id="

list_df={}
    
for games in topgames_df.iterrows() :
    a=games[1]["id"]
    r=requests.get(url+a,headers=headers) 
    r=r.json()
    r=r["data"]
    d=pd.DataFrame(r)
    a=["fr","en"]
    d = d[d['language'].isin(a)]
    list_df[games[1]["name"]]=d
    
reform = {(outerKey, innerKey): values for outerKey, innerDict in list_df.items() for innerKey, values in innerDict.items()}
df=pd.DataFrame.from_dict(reform, orient='index').transpose()
df.columns = pd.MultiIndex.from_tuples(df.columns)

list_games=list(topgames_df["name"])

to_del=["ASMR","Just Chatting","Music","Science & Technology","Art","Talk Shows & Podcasts"]
for eleme in to_del :
    list_games.remove(eleme)

list_df2=[]

for game in list_games :
    mock_df=df[game]
    mock_df=mock_df.dropna()
    Followers=[]
    Views=[]
    for chann in mock_df["user_id"] :
            link="https://api.twitch.tv/kraken/channels/{}/?client_id={}&api_version=5".format(chann,client_id)
            r=requests.get(link).json()
            Followers.append(r["followers"])
            Views.append(r["views"])
    mock_df["Followers"]=Followers
    mock_df["Views"]=Views
    list_df2.append(mock_df)

dff = pd.concat(list_df2, ignore_index=True)
dff=dff[~(dff['Followers']<= 1000)]

categories=[]

data_value_followers=dff["Followers"]
quant=list(data_value_followers.quantile([.33, .66]))

#Catégories : 1= EN/Petite chaine| 2= En/Moyenne | 3= EN/Grosse chaine 
#             4= FR/Petite chaine| 5= FR/Moyenne | 6= FR/Grosse chaine 

for row in dff.iterrows():
    if row[1]["language"] == "en" :
        if row[1]["Followers"] < quant[0] :
            categories.append(1)
        elif row[1]["Followers"] > quant[1] : 
            categories.append(3)
        else :
            categories.append(2)
    if row[1]["language"] == "fr" :
        if row[1]["Followers"] < quant[0] :
            categories.append(4)
        elif row[1]["Followers"] > quant[1] : 
            categories.append(6)
        else :
            categories.append(5)

dff["Categories"]=categories

cat=[1,2,3,4,5,6]
samples=[]

for cate in cat:
    rslt_df = dff[dff['Categories'] == cate]
    sample=rslt_df.sample(n=3)
    samples.append(sample)
    
test_data= pd.concat(samples, ignore_index=True)
test_data=test_data.drop(["user_name","id","user_id","game_id","game_name","type","title","viewer_count","started_at","thumbnail_url","Categories","tag_ids","is_mature","Followers","Views"],axis=1)
test_data.to_csv("test_data.csv")



