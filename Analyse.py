import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

TwitchF=pd.read_csv("Twitch_F.CSV",index_col=[0], header=[0,1])
YoutubeF=pd.read_csv("Youtube_F.csv",index_col=[0], header=[0,1])

df=TwitchF.join(YoutubeF, how='inner')


def get_last_elements(a, axis=0):
  shape = list(a.shape)
  shape[axis] = 1
  return np.take(a,-1,axis=axis).reshape(tuple(shape))

df=df.replace({"live": 1 , "off": -1, "post":True, "no post":False})

df2=df["Domingo"]
df2.reset_index(inplace=True)
df2 = df2.rename(columns = {'index':'Date'})


fig, ax = plt.subplots()
plt.bar(df2["Date"], df2["Live"])

x = df2[df2['Video Post']==True]
x=x["Date"]

for date in x :
    if len(x) !=0 :
        plt.axvline(date, color="red", linestyle="--", lw=2)
    
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
a=0

while a !=0:
    if len(x) !=0 :
       plt.axvline(get_last_elements(x), color="red", linestyle="--", lw=2,label="Youtube Post")
    a=1

fig.autofmt_xdate()
plt.tight_layout()
