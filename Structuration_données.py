import pandas as pd 

TwitchF=pd.read_csv("df_tw.csv",index_col=[0], header=[0,1])

Twitch_Data=pd.read_csv("df_l.csv")
Twitch_Data=Twitch_Data.rename(columns={"Unnamed: 0":"Time"})
Twitch_Data=Twitch_Data.set_index("Time")

Youtube_Data=pd.read_csv("YTNOUV.csv")
Youtube_Data=Youtube_Data.rename(columns={"Unnamed: 0":"Time"})
Youtube_Data=Youtube_Data.set_index("Time")

df2 =pd.concat([Twitch_Data,Youtube_Data], axis=1)

NAME=[]
DATA=[]

for c in df2.keys():
    B=df2[c]
    exec('{} = pd.DataFrame(B)'.format(c))
    
del Twitch_Data,Youtube_Data,df2
     
alldfs = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]
alldfs.remove("B")
alldfs.remove("TwitchF")


def importname () :
    return alldfs 

for df_name in alldfs: 
    a=df_name
    eval(df_name).columns= ['Live', 'Video Post']

data_frames =[]

for data_frame in alldfs: 
    data_frames.append(eval(data_frame))
    del data_frame

df3=pd.concat(data_frames,axis=1, keys=alldfs)
df3.columns.names = ['Streamer','Youtube_Post/Twitch_Live']

def importation () : 
    return df3

def twitch_data_f():
    return TwitchF