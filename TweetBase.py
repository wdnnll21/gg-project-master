import json
import re

class TweetBase(object):
    def __init__(self, filename):
        super(TweetBase, self)
        self.data = []
        with open(filename,encoding="utf8") as json_tweets:
            for line in json_tweets:
                self.data.append(json.loads(line))

    #returns a list of tweets that contain all filter strings
    def filterStringList(self,filtersList):
        retState = []
        for tweet in self.data:
            allFiltersFound = True
            for filter in filtersList:
                if filter not in tweet['text']:
                    allFiltersFound = False
                    break
            if allFiltersFound:
                retState.append(tweet['text'])
        return retState

    #equivalent to filterStringList, but only accepts one string
    def filterOneString(self,stringInput):
        retState = []
        for tweet in self.data:
            if stringInput in tweet['text']:
                retState.append(tweet['text'])
        return retState

    #returns a list of tweets that contain any of the filter strings
    def anyStringList(self,filtersList):
        retState = []
        for tweet in self.data:
            for filter in filtersList:
                if filter in tweet['text']:
                    retState.append(tweet['text'])
        return retState

    #removes hashtags, usernames, and links from tweetbase
    def cullTwitterPunctuation(self):
        cullList = ["#","@","http","://",".co"]
        for tweet in self.data:
            dart = tweet['text'].split(" ")
            addback = ""
            for word in dart:
                culled = False
                for cull in cullList:
                    if cull in word:
                        dart.remove(word)
                        culled = True
                        break
                if not culled:
                    addback += word + " "
            tweet['text'] = addback

    
    def regexStringList(self,expression):
        retState = []
        
        for tweet in self.data:
            ser = re.search(expression,tweet)
            if ser:
                retState.append(ser)

        return retState