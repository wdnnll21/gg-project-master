import spacy
from spacy.matcher import PhraseMatcher
from TweetBase import TweetBase
from spacy.symbols import *
import re

spacyNLP = spacy.load("en_core_web_sm")

class AwardParser(object):
    def __init__(self):
        self.datab = TweetBase("gg2020.json")
        self.datab.cullTwitterPunctuation()
        self.awardFilter = self.datab.anyStringList(["award for Best "])
        self.actualAwards = []

    def awardFinder(self): 
        docs = []
        for item in self.awardFilter:
            docs.append(spacyNLP(item))

        matcher = PhraseMatcher(spacyNLP.vocab,attr="SHAPE")
        matcher.add("Bests", None, spacyNLP("award for Best Giraffe"), spacyNLP("award for Best Saharan Giraffe"),
            spacyNLP("award for Best Person in a Movie"),spacyNLP("award for Best Person in a Thing - Possible"))

        matcherb = PhraseMatcher(spacyNLP.vocab,attr="SHAPE")
        matcherb.add("ConnectSelector",None,spacyNLP("Best Performance by a Person"),spacyNLP("Place by an Arch"),spacyNLP("Person in a Comedy"),spacyNLP("Person in a Good Comedy"),spacyNLP("Person in an Excellent Comedy"),spacyNLP("Person in an Actor"), spacyNLP("Person - Musical"),spacyNLP("Actor or Actress"))

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
        allWinners = []
        for aA in self.actualAwards:
            allWinners.append([aA, self.WinnerFinder(aA)])

    def NomineeFinder(self, award, nomType):
        firstcull = self.datab.filterStringList([award,"\""])
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
                titlefind = re.findall(r"([\"])(?:(?=(\\?))\2.)*?\1", tweet)

                for match in titlefind:
                    print(tweet)
                    print(match)
                    tfind = str(match)
                    if tfind.lower() in nomVote:
                        nomVote[tfind.lower()] += 1
                    else:
                        nomVote[tfind.lower()] = 1


    


ap = AwardParser()

ap.NomineeFinder("Drama","TITLE")






