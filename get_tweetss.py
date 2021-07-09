# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 11:19:44 2021

@author: Petri
"""
import tweepy
import json
import pandas as pd
import time

consumer_key = ''
consumer_secret = ''
access_token= ''
access_token_secret= ''

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

HAKUSANA = "Pöysti"
määrä = 250
KAIKKI = False

def get_tweets(api, HAKUSANA, monta):   
    # Get tweets
    if KAIKKI:
        t = time.time()
        # do stuff
        tweets = tweepy.Cursor(api.search,
                      q="*", lang='fi').items(10000)
        elapsed = time.time() - t
        print("elapsed 1: {}".format(elapsed))
        my_list_of_tweets = []
        for tweet in tweets:
            my_list_of_tweets.append(tweet._json)
        
        # save to json
        with open('tweets.json', 'w') as file:
                file.write(json.dumps(my_list_of_tweets, indent=4))
        elapsed1 = time.time() - elapsed        
        print("elapsed 2: {}".format(elapsed1))
       
    else:
        search_words = HAKUSANA
        
        tweets = tweepy.Cursor(api.search,
                      q=search_words).items(määrä)
        
        my_list_of_tweets = []
        for tweet in tweets:
            my_list_of_tweets.append(tweet._json)
        
        # save to json
        with open('tweets.json', 'w') as file:
                file.write(json.dumps(my_list_of_tweets, indent=4))
            
t = get_tweets(api, HAKUSANA, määrä)
pf = pd.read_json("tweets.json")

print("\n------------------------------\n")
print("Mistä asti tweettejä tuli: {}".format(pf.tail(1)["created_at"]))
print("\n----------------------\n")
print("Milloin edellinen oli lähtetytty: {}".format(pf.head(1)["created_at"]))
print("\n------------------------------\n")


