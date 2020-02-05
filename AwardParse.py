import spacy
from spacy.matcher import PhraseMatcher
from TweetBase import TweetBase
from spacy.symbols import *
import re
from datetime import datetime
from datetime import timedelta

spacyNLP = spacy.load("en_core_web_sm")

class AwardParser(object):
    def __init__(self,year):
        self.datab = TweetBase("gg2020.json")
        self.datab.cullTwitterPunctuation()
        self.awardFilter = self.datab.anyStringList(["award for Best "])
        self.actualAwards = []
        self.year = year

    def awardFinder2(self):
        docs = []
        firstcull = self.datab.regexStringList("Best [A-Z]")

        for item in firstcull:
            docs.append(spacyNLP(item))

    def awardFinder(self): 
        docs = []
        for item in self.awardFilter:
            docs.append(spacyNLP(item))

        matcher = PhraseMatcher(spacyNLP.vocab,attr="SHAPE")
        matcher.add("Bests", None, spacyNLP("award for Best Giraffe"), spacyNLP("award for Best Saharan Giraffe"),
            spacyNLP("award for Best Person in a Movie"),spacyNLP("award for Best Person in a Thing - Possible"))

        matcherb = PhraseMatcher(spacyNLP.vocab,attr="SHAPE")
        matcherb.add("ConnectSelector",None,spacyNLP("Best Performance by a Person"),spacyNLP("Place by an Arch"),
        spacyNLP("Person in a Comedy"),spacyNLP("Person in a Good Comedy"),
        spacyNLP("Person in an Excellent Comedy"),spacyNLP("Person in an Actor"), 
        spacyNLP("Person - Musical"),spacyNLP("Actor or Actress"),spacyNLP("Person in a Motion Picture"))

        awards = []
        for doc in docs:
            a = matcher(doc)
            b = matcherb(doc)
            internalawards = []

            phrase_labels = set([nsubj,nsubjpass,dobj,iobj,pobj])

            awardRange = [0,0]
            for match_id,starta,enda in a:
                if "Best" in doc[starta:enda].text:
                    awardRange[0] = starta + 2
                    awardRange[1] = enda
            if awardRange[1] == 0:
                for ent in doc.ents:
                    if "Best" in ent.text:
                        awardRange = [ent.start,ent.end]
                    
            for match_id,start,end in b:
                if start <= awardRange[1] and end > awardRange[1]:
                    awardRange[1] = end

            print(doc[awardRange[0]:awardRange[1]])          
    
    def HostFinder(self):
        firstcull = self.datab.anyStringList(["is hosting"])
        docs = []
        hostVote = {}

        for tweet in firstcull:
            docs.append(spacyNLP(tweet))

        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    if ent.lower_ in hostVote:
                        hostVote[ent.lower_] += 1
                    else:
                        hostVote[ent.lower_] = 1
        
        return max(hostVote,key=hostVote.get)

    def WinnerFinder(self, award):
        firstcull = self.datab.filterStringList([award,"wins"])
        docs = []
        winVote = {}

        for tweet in firstcull:
            docs.append(spacyNLP(tweet))
        
        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    if ent.lower_ in winVote:
                        winVote[ent.lower_] += 1
                    else:
                        winVote[ent.lower_] = 1
        

        return max(winVote, key=winVote.get)

    def acceptActualAwards(self, actualList):
        self.actualAwards = actualList

    def FindAllWinners(self):
        allWinners = {}
        for aA in self.actualAwards:
            allWinners[aA] = self.WinnerFinder(aA)

        return aA

    def NomineeFinder(self, award, nomType):
        firstcull = self.datab.filterStringList([award, "\""])
        docs = []
        nomVote = {}

        for tweet in firstcull:
            if nomType == "PERSON":
                doc = spacyNLP(tweet)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        print(ent)
                        if ent.lower_ in nomVote:
                            nomVote[ent.lower_] += 1
                        else:
                            nomVote[ent.lower_] = 1
            elif nomType == "TITLE":
                titlefind = re.finditer(r"([\"])(?:(?=(\\?))\2.)*?\1", tweet)

                for match in titlefind:
                    print(match[0])
                    tfind = match[0]
                    if tfind.lower() in nomVote:
                        nomVote[tfind.lower()] += 1
                    else:
                        nomVote[tfind.lower()] = 1

    def PresenterFinder(self, award, winner):
        winTime = self.datab.earliestMention([award,winner,"won"])
        winnerTime = datetime.strptime(winTime,"%Y-%m-%dT%H:%M:%S")
        End = winnerTime + timedelta(minutes=5)
        Start = winnerTime - timedelta(minutes=5)
        tenMinuteList = self.datab.timeFrameFilter(str(Start).replace(" ","T"),str(End).replace(" ","T"))

        kwlist = ["announce","present"]
        PresenterFilter = filter(lambda tweet: any(kw in tweet for kw in kwlist), tenMinuteList)

        for presentertweet in list(PresenterFilter):
            print(presentertweet)
    
    def TestMethod(self):
        test = self.datab.earliestMention(["Taylor Swift","Amy Poehler"])
        testDate = datetime.strptime(test,"%Y-%m-%dT%H:%M:%S")
        testFiveMinutes = testDate + timedelta(minutes=5)
        testEarlier = testDate - timedelta(minutes=5)
        print(str(testEarlier).replace(" ","T"))
        testList = self.datab.timeFrameFilter(str(testEarlier).replace(" ","T"),str(testFiveMinutes).replace(" ","T"))
        for tweet in testList:
            print(tweet)

    def AwardVariantFinder(self,award):
        variant = [award]
        awarray = award.split(" ")
        doc = spacyNLP(award)

        for ent in doc.ents:
            variant.append(ent)
        
        return variant

    def NameVariantFinder(self,person):
        variants = [person]
        personarray = person.split(" ")
        variants.append(personarray[0])
        variants.append(personarray[1])
        variants.append(personarray[0] + personarray[1])

        return variants

    def TheyWonAwardParser(self,filters, nomType):
        filters.append(["wins","won"])
        if nomType == "MEDIA":
            filters.append("\"")
        firstcull = self.datab.ANDorFILTER(filters)
        winVote = {}
        docs = []

        for tweet in firstcull:
            mentionedMovies = list(re.finditer(r"([\"'])(?:(?=(\\?))\2.)*?\1", tweet))
            subj = ""
            pred = ""
            ignore = False
            doc = spacyNLP(tweet)

            for word in doc:
                if word.text == ".":
                    break
                if nomType == "MEDIA" and word.text == "\"":
                    subj = mentionedMovies[0][0]
                #if word.text == "won" and word.pos_ != "VERB":
                #    ignore = True
                if word.dep_ in ["nsubj","nsubjpass"] and word.head.text in ["wins","won"] and nomType == "PERSON":
                    if word.ent_iob_ == "I":
                        subj = next(x for x in doc.ents if word.text in x.text).text
                    else:
                        subj = word.text
                elif word.dep_ == "dobj" and word.head.text in ["wins","won"]:
                    pred = word.text

            
            if not ignore and subj != "" and pred != "":
                print(tweet)
                print(subj," ",pred)
                #return subj
            #return False

    def CongratulationsParser(self, filters, nomType):
        filters.append(["Congratulations to","Congrats to"],["for winning Best","for winning the award","for Best"])
        if nomType == "MEDIA":
            filters.append("\"")
        firstcull = self.datab.ANDorFILTER(filters)
        
        for tweet in firstcull:
            mentionedMovies = list(re.finditer(r"([\"'])(?:(?=(\\?))\2.)*?\1", tweet))
            obj = ""
            doc = spacyNLP(tweet)

            for word in doc:
                if word.text == ".":
                    break
                if nomType=="MEDIA" and word.text=="\"":
                    obj = mentionedMovies[0][0]
                if word.text in ["Congratulations", "Congrats"] and doc[word.i+1].dep_ in ["prep"] and nomType=="PERSON":
                    if word.ent_iob_ == "I":
                        obj = next(x for x in doc.ents if word.text in x.text).text
                #if word.text in ["Congratulations", "Congrats"] and doc[word.i+1].dep_ in [""]
                




        return 0

    def VariantSimilarity(self, string1, string2):
        return 0

    def NominatedForParser(self,filters):
        return 0

    def NomineeListParser(self,filters):
        return 0

    def AllPresentersFinder(self,filters):
        return 0

    def PresentedTogetherParser(self,filters):
        return 0

    def TimeBasedPresentation(self,filters):
        return 0
    
    
ap = AwardParser(2020)

ap.TheyWonAwardParser([["Best","best"],["Limited Series","limited Series","limited series"],["Actress","actress"],["Supporting"]],"PERSON")




# 'best television limited series or motion picture made for television'
# cecil b. demille award



#p.NomineeFinder("Drama","TITLE")

#ap.PresenterFinder("Best Director","Sam Mendes")









