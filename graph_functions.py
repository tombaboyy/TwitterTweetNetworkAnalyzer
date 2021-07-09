# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 10:01:59 2021

@author: Petri
"""
import pandas as pd

def form_edges(tweet_db):   
    #tweetin kirjoittaja
    edges = {}
    for i in range(len(tweet_db)):
        user_id = int(tweet_db.loc[i,"user"]["id"])
        user_name = tweet_db.loc[i,"user"]["screen_name"]
        id_and_name = "{},{}".format(user_name, user_id)
        if id_and_name in edges:
            id_and_name = "{},{}_{}".format(user_name,user_id,i)
            edges[id_and_name] = {}
        else:
            edges[id_and_name] = {}
    
        
        tweet_id = tweet_db.loc[i, "id"]
        edges[id_and_name]["tweet id"] = tweet_id
    
        tweet_replies_to = [] 
        if tweet_db.loc[i, "in_reply_to_screen_name"] != None:
            tweet_replies_to.append(tweet_db.loc[i, "in_reply_to_screen_name"])
            tweet_replies_to.append(int(tweet_db.loc[i, "in_reply_to_user_id"]))
            edges[id_and_name]["replay"] = tweet_replies_to
            
        is_retweeted = []
        if not pd.isnull(tweet_db.loc[i, "retweeted_status"]):
            is_retweeted.append(tweet_db.loc[i, "retweeted_status"]["user"]["screen_name"])
            is_retweeted.append(int(tweet_db.loc[i, "retweeted_status"]["user"]["id"]))
            edges[id_and_name]["retweet"] = is_retweeted
        
        is_quotet = []
        if not pd.isnull(tweet_db.loc[i, "quoted_status"]):
            is_quotet.append(tweet_db.loc[i, "quoted_status"]["user"]["screen_name"])
            is_quotet.append(int(tweet_db.loc[i, "quoted_status"]["user"]["id"]))
            edges[id_and_name]["quote"] = is_quotet
        
        mentions = []
        if tweet_db.loc[i, "entities"]["user_mentions"]:
            
            for user in tweet_db.loc[i, "entities"]["user_mentions"]:
                p_id = user["id"]
                name = user["screen_name"]
                id_and_name_m = [name,p_id]
                mentions.append(id_and_name_m)
                edges[id_and_name]["mentions"] = mentions
        """        
        retweetters = []
        if tweet_db.loc[i, "retweet_count"] != 0:
            iidee = tweet_db.loc[i, "id"]
            print(iidee)
            retweetters = api.retweets(iidee,tweet_db.loc[i, "retweet_count"])
            for tweet in retweetters:
                 print(tweet)
                 user_how_retweetted_id = tweet.user.id
                 user_how_retweetted_name = tweet.user.screen_name
                 retweetters.append([user_how_retweetted_id, user_how_retweetted_name])
            edges[id_and_name]["retweetters"] = retweetters
        """
    return edges

def make_grap(data,G):
    for tweettaaja in data:
        tweettaaja_lyhyt = tweettaaja
        if '_' in tweettaaja.split(",")[1]:
            tweettaaja_lyhyt = tweettaaja.split(",")[0] + "," + tweettaaja.split(",")[1].split("_")[0]
            
        if 'mentions' in data[tweettaaja]:
            for men in data[tweettaaja]['mentions']:                    
                id_ = men[0]
                name = men[1]
                how ="{},{}".format(id_,name)
                G.add_edge(tweettaaja_lyhyt,how)
                
        if 'replay' in data[tweettaaja]:
            how ="{},{}".format(data[tweettaaja]['replay'][0],data[tweettaaja]['replay'][1])                
            G.add_edge(tweettaaja_lyhyt,how)
            #data[tweettaaja]["tweet id"]
            
        if 'retweet' in data[tweettaaja]:
            how ="{},{}".format(data[tweettaaja]['retweet'][0],data[tweettaaja]['retweet'][1])                
            G.add_edge(tweettaaja_lyhyt,how)
            
        if 'quote' in data[tweettaaja]:
            how ="{},{}".format(data[tweettaaja]['quote'][0],data[tweettaaja]['quote'][1])                
            G.add_edge(tweettaaja_lyhyt,how)
    
    return G

def data_man(edge_data):
    muokattu_dict = {}
    for key in edge_data:
        if key.split(",")[0] in muokattu_dict:
            None
        else:
            muokattu_dict[key.split(",")[0]] = {"mentions":[], "replay": [], 
                                                "retweet":[], "quote":[]}
        ihm = edge_data[key]
        replay = ""
        if "replay" in ihm:
            muokattu_dict[key.split(",")[0]]["replay"].append(ihm["replay"][0])
            replay = ihm["replay"][0]
            
        retweet = ""

        if "retweet" in ihm:

            muokattu_dict[key.split(",")[0]]["retweet"].append(ihm["retweet"][0])
            replay = ihm["retweet"][0]
        
        if "quote" in ihm:
            muokattu_dict[key.split(",")[0]]["quote"].append(ihm["quote"][0])          
        
        if "mentions" in ihm:
            for user in ihm["mentions"]:
                if user[0] != replay and user[0] != retweet:
                        muokattu_dict[key.split(",")[0]]["mentions"].append(user[0])
    
    return muokattu_dict
                

pf = pd.read_json("tweets.json")
data_for_edges = form_edges(pf)
data_for_show = data_man(data_for_edges)