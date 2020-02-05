import json
import re
from bisect import bisect_left

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
                retState.append(tweet)

        return retState

    def timeFrameFilter(self,time1,time2):
        times = [tweet['created_at'] for tweet in self.data]
        times.reverse()
        early = len(self.data) - bisect_left(times,time1)
        late = len(self.data) - bisect_left(times,time2)
        
        filtered = []
        print(self.data[early])
        for tweet in self.data[late:early]:
            filtered.append(tweet['text'])

        return filtered
            

    def earliestMention(self,filtersList):
        for tweet in reversed(self.data):
            text = tweet['text']

            if all([kw in text for kw in filtersList]):
                return tweet['created_at']


    #accepts a list of filters, tries to find all the 
    def ANDorFILTER(self,filtersList):
        retState = []
        for tweet in self.data:
            allFound = True
            for filter in filtersList:
                if isinstance(filter,list):
                    if not any([kw in tweet['text'] for kw in filter]):
                        allFound = False
                        break
                elif isinstance(filter,re.Pattern):
                    if re.match(filter,tweet['text']) == False:
                        allFound = False
                        break
                elif isinstance(filter,tuple):
                    if filter[0] in tweet['text']:
                        allFound = False
                        break
                else:
                    if filter not in tweet['text']:
                        allFound = False
                        break
            if allFound:
                retState.append(tweet['text'])

        return retState

    def MentionedTogether(self,string1,string2):
        return len(self.ANDorFILTER([string1,string2]))

    def PercentageMentionedTogether(self,string1,string2):
        mention1 = len(self.anyStringList(string1))
        mention2 = len(self.anyStringList(string2))
        together = self.MentionedTogether(string1,string2)
        return together / (mention1+mention2-together)
        
                         

            
