#-*- coding: utf-8 -*-
from com.ibm.dev.auth import authenInfo
import tweepy
import json
import MySQLdb
import os
import re
import time


class authAccount:
        
    def __init__(self,CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET):
        self.CONSUMER_KEY = CONSUMER_KEY
        self.CONSUMER_SECRET = CONSUMER_SECRET
        self.ACCESS_KEY = ACCESS_KEY
        self.ACCESS_SECRET = ACCESS_SECRET
        
    def authTwitterAccount(self):
        auth = tweepy.OAuthHandler(self.CONSUMER_KEY,self.CONSUMER_SECRET)
        auth.set_access_token(self.ACCESS_KEY, self.ACCESS_SECRET)
        return auth
    
class dbConn:
    def __init__(self, HOST ,USER , PASSWORD , DATABASE):
        self.USER = USER
        self.PASSWORD = PASSWORD
        self.HOST = HOST
        self.DATABASE = DATABASE
                
    def doConnDB(self):
        connection = MySQLdb.connect(self.HOST, self.USER, self.PASSWORD, self.DATABASE)
        return connection
        
   
auth = authAccount(authenInfo.CONSUMER_KEY,authenInfo.CONSUMER_SECRET,authenInfo.ACCESS_KEY,authenInfo.ACCESS_SECRET)
temp_api  = auth.authTwitterAccount()
api = tweepy.API(temp_api)
temp =1  

dbConnection = dbConn(authenInfo.HOST, authenInfo.USER, authenInfo.PASSWORD, authenInfo.DATABASE)
conn = dbConnection.doConnDB()
cursor = conn.cursor()

#https://twitter.com/realmudo/status/880986512564690946

orgTweet = api.retweets(880986512564690946,100)

for tweet in orgTweet:
    add_twit = ("INSERT INTO tb_retweet_info(screenNm,tweetNum,tweetId,sourceId) VALUES(%s,%s,%s,%s)")
    data_twit = (tweet.user.screen_name, tweet.id_str, tweet.user.id, tweet.retweeted_status.id)
    
    cursor.execute(add_twit, data_twit)
    conn.commit()

cursor.execute("SELECT screenNm,sourceId FROM tb_retweet_info")

for screen_name,source_id in cursor:
    screen_name_parsing =''.join(map(str,screen_name))    
    
    users = tweepy.Cursor(api.user_timeline, id=screen_name_parsing, include_entities=True).items()
        
    while True:
        try:      
            cnt = 0      
            user = next(users)
            str_1 = user.entities.__str__() 
            #print("str_1 : ",user)
            tl_source_id_temp = re.findall("source_status_id': (.*?),", str_1) 
            tl_source_id =''.join(tl_source_id_temp).__str__() 
            tweet_num = user.id_str
            
            # 공백없으면 계속, 있으면 공백으로 split  
            if user.text.find(" ") == -1:
                continue
            else:
                if user.text.find("RT") == -1:
                    continue
                else:
                    split_text_timelineList = user.text.split(' ',2) 
                    
                    split_text_timeline = split_text_timelineList[2]
                
                    split_text_timelineParsing = split_text_timeline.split("https",2)
                    split_text_originalParsing = api.get_status(source_id).text.split('https',2)
                
                
                       
                    if split_text_timelineParsing[0] == split_text_originalParsing[0]:
                        print("            Tweet After Retweet        ",api.get_status(temp).text)
                        print("            Time After Retweet        ",api.get_status(temp).created_at)
                                           
                        split_text_timeline = ""
                        split_text_timelineList = ""
                        split_text_originalList = ""
                        break
            
                    else:
                        split_text_timeline = ""
                        split_text_timelineList = ""
                        split_text_originalList = ""
                        temp = tweet_num
                
                
                
                
        except tweepy.TweepError:
            print("time sleep now")
            time.sleep(60*15)
            continue
        except StopIteration:
            break

