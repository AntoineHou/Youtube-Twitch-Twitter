import pandas as pd 
import re 
from datetime import datetime, timedelta
import numpy as np
import os
 
arr = os.listdir()
files=[]

for element in arr :
    if ".log" in element:
        files.append(element)
    else :
        pass
    

with open('Solary2021-06-14.log',encoding="utf8") as f:
    content = f.read().splitlines()
        

df=pd.read_csv("df_tw.csv",index_col=[0], header=[0,1])
df2=pd.read_csv("ExempleChann.csv")

Name=list(df2["Channel"])

class Data_F(object):
    def __init__(self, name, values):  
        self.name = name 
        self.values = values
        
def Structuration_Chat(df) :
    Time_stamp=list(df.index)
    line=[]
    for items in content : 
        if "seittaa" in items : 
            pass  
        else :
            line.append(items) 
    Time=[]
    Sender=[]
    Message=[]
    Other=[]
    a=0
    
    while a != len(line) :
        b=line[a][0:27]
        Time.append(b)
        c=line[a][27:]
        Message.append(c)
        a=a+1
    
    Status=[]
    
    for mess in Message : 
        if "privmsg" not in mess:
            Other.append(mess)
        else :
            b=(re.findall(r'(?<==)[a-zA-Z]+(?=\W*/)',mess))
            if len(b) !=0 :
                Status.append(b[0])
            else : 
                Status.append("Normal")
    a=0
    message=[]
    
    for mes in Message : 
        if "privmsg"  in mes:
            a=re.sub(r'.*(?=type=)',"",mes )
            message.append(a)
        else :
            pass
    MessageF=[]
    for mess in message :
        if "type=mod"  in mess : 
            a=re.findall(r'.*?\:(.*) :.*',mess)
            Sender.append(a)
        else :
            a=re.findall(r'.*?\:(.*) :.*',mess)
            Sender.append(a)
    for mass in message :
            b=mass[mass.find(' :'):]
            b=b[2:]
            b=b[b.find(' :'):]
            b=b[2:]
            MessageF.append(b)
    time=[]
    for delta in Time : 
        if "#" in delta : 
            delta=(delta[2:21])
            d=re.sub(r'T'," ",delta)
            time.append(d)
        else :
            delta=(delta[:19])
            d=re.sub(r'T'," ",delta)
            time.append(d)
    df=pd.DataFrame(list(zip(time,Sender,Message)),columns=["Time","Sender","Message"])
    Sender= [''.join(ele) for ele in Sender]
    SenderL=list(set(Sender))
    SenderL.append("chess24")
    new_col=[]
    for row in MessageF :
        direction=[]
        for users in SenderL:
            if users in row :
                direction.append(users)
            else :
                pass
        new_col.append(direction)
    df["Reciever"]=new_col
    df["Message"]=df['Message'].str.split('\:').str[-1].str.strip()    
    df["Longueur"]=df["Message"].str.len()
    df["NbMention"]=df["Reciever"].str.len()
    df['Time'] =  pd.to_datetime(df['Time'])
    df["Status"]=Status    
    s1=datetime.strptime(Time_stamp[0], '%Y-%m-%d %H:%M:%S')- timedelta(days=15)
    s2=datetime.strptime(Time_stamp[0], '%Y-%m-%d %H:%M:%S')+ timedelta(days=15)
    Time_stamp=pd.to_datetime(pd.Series(Time_stamp), format='%Y-%m-%d %H:%M:%S')
    Time_stamp=pd.DataFrame(np.insert(Time_stamp.values, 0, values=s1, axis=0))
    Time_stamp=pd.DataFrame(np.insert(Time_stamp.values, len(Time_stamp), values=s2, axis=0))
    aa=0
    bb=0
    New_col=[]
    while bb != len(df) :
        for items in df["Time"]: 
            if items > Time_stamp[0][aa] and items<Time_stamp[0][aa+1] :
                New_col.append(Time_stamp[0][aa])
                bb=bb+1
            else : 
                aa=aa+1
                bb=bb+1
                New_col.append(Time_stamp[0][aa])
    
    df["Time_Stamp"]=New_col
    return df
    
a=0
df_logs=[]        

while a !=len(files) :
    with open(files[a],encoding="utf8") as f:
        content = f.read().splitlines()
    d=(Structuration_Chat(df))
    name=re.sub('[0-9]+', '', str(files[a]))
    name = name.split("-", 1)
    name=name[0]
    e=Data_F(name,d)
    df_logs.append(e)
    a=a+1
    

for name in Name :
  for log in df_logs: 
        if log.name == name :
           print(True)
        else : 
          pass

    
