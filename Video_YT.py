from googleapiclient.discovery import build
import pandas as pd 
from Structuration_données import importation
from Structuration_données import twitch_data_f
from Structuration_données import importname
import requests
import time 

TwitchF=twitch_data_f()
df_f=importation()

df_i=pd.read_csv('ExempleChann.csv',engine='python')
name=importname()
df_i=df_i.set_index('Channel')

api_key="AIzaSyBToNS7k_So6Ci_4sklt2DfK5IXdpN2rEs"
youtube=build('youtube', 'v3', developerKey=api_key)

#Modifier la date au besoin
dictionnary={}
etags={}
compteur=0
    
for names in name : 
    b=df_f[names]["Video Post"]
    d=0
    e=0
    while d != len(b) :
        if b[d] == "no post" :
            d=d+1
        else : 
            e=e+1
            d=d+1
            dictionnary[names]=e
                

while compteur != len(name) :
        streamer=name[compteur]
        if streamer in  dictionnary :
            nb_vid=dictionnary.get(streamer)
            id_channel=df_i.loc[streamer]["ID"]
            request = youtube.search().list( part='id', channelId=id_channel, publishedBefore ="2021-05-23T00:19:00Z", #Date
            type='video', order='date',maxResults=nb_vid)
            response=request.execute()
            response=response['items']
            etag=[]
            for tag in response :
                etag.append(tag['id']['videoId'])
            etags[streamer]=etag
        else :
            etags[streamer]=""
        compteur=compteur+1

part_string='statistics,snippet'


def compl_data (data_frame, column_name, fill_value, list_compl) :
    listvid=list(data_frame["Video Post"])
    taille=len(listvid)
    compt=0
    compt2=0
    list_val_fill=[]
    while compt != taille :
        if listvid[compt] == "post" :
            list_val_fill.append(list_compl[compt2])
            compt2=compt2+1
        else:
            list_val_fill.append(fill_value)
        compt=compt+1
    données[column_name]=list_val_fill
    return données
   

all_df=[]

for key , value in etags.items() :
    données=df_f[key]
    if len(value) != 0 : 
        a=youtube.videos().list(part=part_string, id=value)
        a=a.execute()
        title=[]
        description=[]
        tags=[]
        if len(a["items"]) == 0 :
            pass 
        if len(a["items"]) == 1 :
            items=a["items"][0]
            title.append(items["snippet"]["title"])
            description.append(items["snippet"]["description"])
            if "tags" in items.items() :
                tags.append(items["snippet"]["tags"])
        if len(a["items"])>1  :
            d=0
            while d != len(a["items"]) :
                items=a["items"][d]
                title.append(items["snippet"]["title"])
                description.append(items["snippet"]["description"])
                if "tags" in items.items() :
                    tags.append(items["snippet"]["tags"])
                d=d+1
        v=compl_data(données,"title","no title",title)
        v=compl_data(données,"description","no description",description)
        if len(tags) !=0:
            v=compl_data(données,"tags","no tags",tags)
        v=v.drop(columns=["Live"])
        all_df.append(v)
    else : 
        v=données
        v["title"]="no title"
        v["description"]="no description"
        v["tags"]="no tags"
        v=v.drop(columns=["Live"])
        all_df.append(v)
            
Youtube_f=pd.concat(all_df,axis=1, keys=name)

#TwitchF.to_csv("Twitch_F.CSV")
Youtube_f.to_csv("Youtube_F.CSV")

#df3= (pd.concat([TwitchF, Youtube_f], axis=1))
#df3.to_csv("DonnéesExemple.CSV")

