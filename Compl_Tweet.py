import tweepy
import pandas as pd 

df=pd.read_csv("Tweet_ID.csv")

def load_api():
    consumer_key = "Sl1b8kxfpdesC7VBEqufGbrN2"
    consumer_secret = "wAB0UMxyVyNnBSBU4fihQFtQpq94Bdds94n273w8QiaRLY3o7f"
    access_token = "2771537930-b02f7A23GZ389daUggwm14lRzkxbyCY0ZJRUy6l"
    access_token_secret = "zESyM4t7bJ7wlJSEbWdhxNclnW32gP1xhBlpSLPmPWYa1"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,parser=tweepy.parsers.JSONParser())

apit = load_api()

def info_status (User,TweetID) :
        status=apit.get_status(TweetID) 
        text=status["text"]
        retweet_count=status["retweet_count"]
        favorite_count=status["favorite_count"]
        hashtags=[]
        if len(status["entities"]["hashtags"]) != 0 :
            a=0
            while a != len(status["entities"]["hashtags"]) :
                hashtags.append(status["entities"]["hashtags"][a]["text"])
                a=a+1
        else :
            hashtags=0
        dictionary={User : [text,retweet_count,favorite_count,hashtags]}
        return dictionary

def no_Id_compl(User) : 
     dictionary={User : ["0","0","0","0"]}
     return dictionary

    
for columns in df.columns:
    a=df[columns]
    mock=[]
    for row in a :
        if row == 0 :
            mock.append(no_Id_compl(columns))
        else :
            try : 
                mock.append(info_status(columns,str(row)))
            except tweepy.TweepError : 
                mock.append(no_Id_compl(columns))
    exec('{} = pd.DataFrame(mock)'.format(columns))
    
alldfs = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]
alldfs.remove("df")

for df_name in alldfs: 
    a=df_name
    eval(df_name).columns= ['Info']

data_frames =[]

for data_frame in alldfs: 
    data_frames.append(eval(data_frame))
    del data_frame

data_frames_correction=[]

for dataframe in data_frames : 
    data_frames_correction.append(pd.DataFrame(dataframe["Info"].to_list(), columns=['text', 'retweet_count','favorite_count','hashtags']))

data_frames_correction2=[]

for data in data_frames_correction :
    data["NBMention"]=data["text"].str.count('@')
    data_frames_correction2.append(data)
    
    
dff=pd.concat(data_frames_correction2,axis=1, keys=alldfs)


#dff.to_csv("Twitter.csv")


