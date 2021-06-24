import pandas as pd 
import requests
import numpy as np
import twitch

helix = twitch.Helix('gz9d78zfjgqr7syjhve7ogl0gjn9in', 'j0snruq4ut0blhulvgkbgzm7ay6ze4')
df=pd.read_csv("C:/Users/antoi/PycharmProjects/pythonProject/Projet/Done/Before/test_data_complet.csv")

ID=[]

for user in df["user_login"] :
    for user in helix.users(user):
        a=(user.id)
        ID.append(a)
        
        
df["ChannelIDTwitch"]=ID

Mature=[]
Created=[]
Description=[]
Followers=[]
Views=[]
broadcaster_type=[]

for chann in df["ChannelIDTwitch"] : 
    link="https://api.twitch.tv/kraken/channels/{}/?client_id=gz9d78zfjgqr7syjhve7ogl0gjn9in&api_version=5".format(chann)
    r=requests.get(link).json()
    Mature.append(r["mature"])
    Created.append(r["created_at"][:10])
    Description.append(r["description"])
    Followers.append(r["followers"])
    broadcaster_type.append(r["broadcaster_type"])
    Views.append(r["views"])
    
    
df["Mature"]=Mature
df["Created"]=Created
df["Description"]=Description
df["Followers"]=Followers
df["Views"]=Views
df["broadcaster_type"]=broadcaster_type

df.to_csv('C:/Users/antoi/PycharmProjects/pythonProject/Projet/Done/Before/test_data_complet.csv',index=False)
#df.to_json('C:/Users/antoi/PycharmProjects/pythonProject/Projet/Done/Before/Chann.json', orient='records', lines=True)
