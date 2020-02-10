import json
import re
from bisect import bisect_left
from HardQuery import categories

class TweetBase(object):
    def __init__(self, filename, year):
        super(TweetBase, self)
        self.data = []
        self.year = year
        self.HardQueries = {}
        if year == 2020:
            with open(filename,encoding="utf8") as json_tweets:
                for line in json_tweets:
                    self.data.append(json.loads(line))
        else: 
            with open(filename, encoding="utf8") as json_tweets:
                self.data = json.load(json_tweets)

    def PerformHardQueries(self) :
        for 

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
        self.basiccull()
        for tweet in self.data:
            tweet['text'] = tweet['text'].replace("’","'").replace("—","-")
            tweet['text'] = re.sub(r'\w*([#@]|http|\:\/\/|.co\/)\w*',"",tweet['text'])
    
    def regexStringList(self,expression):
        retState = []
        
        for tweet in self.data:
            ser = re.search(expression,tweet['text'])
            if ser:
                retState.append(tweet['text'])

        return retState

    def timeFrameFilter(self,time1,time2):
        if self.year == 2020:
            times = [tweet['created_at'] for tweet in self.data]
        else:
            times = [tweet['timestamp_ms'] for tweet in self.data]
        times.reverse()
        early = len(self.data) - bisect_left(times,time1)
        late = len(self.data) - bisect_left(times,time2)
        
        filtered = []
        #print(self.data[early])
        for tweet in self.data[late:early]:
            filtered.append(tweet['text'])

        return filtered
            

    def earliestMention(self,filtersList):
        for tweet in reversed(self.data):
            text = tweet['text'].lower()

            if all([kw in text for kw in filtersList]):
                if self.year == 2020:
                    return tweet['created_at']
                else:
                    return tweet['timestamp_ms']


    #accepts a list of filters, tries to find all the 
    def ANDorFILTER(self,filtersList,caseless=False):
        retState = []
        dataset = []
        if filtersList[0] in self.HardQueries:
            del filtersList[0]
            dataset = HardQueries[filtersList[0]]
        else:
            
        for tweet in self.data:
            tweettext = tweet['text']
            if caseless:
                tweettext = tweet['text'].lower()
            allFound = True
            for filter in filtersList:
                if isinstance(filter,list):
                    if not any([kw in tweettext for kw in filter]):
                        allFound = False
                        break
                elif isinstance(filter,re.Pattern):
                    if re.search(filter,tweettext) == None:
                        allFound = False
                        break
                elif isinstance(filter,tuple):
                    if any([kw in tweettext for kw in filter]):
                        allFound = False
                        break
                else:
                    if filter not in tweettext:
                        allFound = False
                        break
            if allFound:
                retState.append(tweet['text'])

        return retState

    def getRegexFullMatchOnly(self,regex):
        retState = []
        for tweet in self.data:
            ser = re.search(regex,tweet['text'])
            if ser:
                retState.append(ser[0])

        return retState


    def MentionedTogether(self,string1,string2):
        return len(self.ANDorFILTER([string1,string2]))

    def PercentageMentionedTogether(self,string1,string2):
        mention1 = len(self.anyStringList(string1))
        mention2 = len(self.anyStringList(string2))
        together = self.MentionedTogether(string1,string2)
        return together / (mention1+mention2-together)

    def basiccull(self):
        data2 = []
        for tweet in self.data:
            if "RT @" not in tweet['text']:
                data2.append(tweet)
        self.data = data2
        
                         

            
