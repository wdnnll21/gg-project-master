import spacy
from spacy.matcher import PhraseMatcher
from TweetBase import TweetBase
from spacy.symbols import *
import re
from datetime import datetime
from datetime import timedelta

spacyNLP = spacy.load("en_core_web_sm")
synonyms = {"television":["tv"],"picture":["motion picture","movie","film","feature film"],"film":["movie","feature film"],"movie":["motion picture","film"]}

class AwardParser(object):
    def __init__(self,year):
        self.datab = TweetBase("gg2020.json")
        self.datab.cullTwitterPunctuation()
        self.awardFilter = self.datab.anyStringList(["award for Best "])
        self.actualAwards = []
        self.year = year

    def awardFinder2(self):
        awards = {}
        firstcull = self.datab.regexStringList(" Best [A-Z]")

        for item in firstcull:
            #docs.append(spacyNLP(item))
            splt = item.split(" ")
            indx = splt.index("Best")
            end = indx
            for itex in splt[indx:]:
                if itex == "":
                    break
                punctual = False
                for punct in ["\n","?","\"","\'","\\","/","\t","\xa0","Should"]:
                    if punct in itex:
                        punctual = True
                        break
                for punct in ["!",".",":"]:
                    if punct in itex and itex[0].isupper():
                        end += 1
                        punctual = True
                        break
                if punctual:
                    break
                if "Best" in itex and indx != end:
                    break
                if itex[0].isupper():
                    end += 1
                elif itex in ["by","in","a","an","-","or"]:
                    end += 1
                elif itex == "for" and splt[end-1] == "Made":
                    end += 1
                else:
                    break
            while splt[end - 1] in ["by","in","a","an","-","or","for","Golden","Globe","To","Award"]:
                end -= 1
            for punct in ["!",".",":"]:
                splt[end-1].replace(punct,"")
            result = " ".join(splt[indx:end])
            if result.lower() in awards and " - " in result:
                awards[result.lower()] += 1
            else:
                awards[result.lower()] = 1

        print(sorted(awards,key=awards.get))
        
        
            



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
        filters.extend([["Congratulations","Congrats"],["for winning Best","for winning the award","for Best"]])
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
                #if word.dep_ in ["pobj"] and word.head.text in ["to"] and nomType=="PERSON":
                  #  if word.ent_iob_ == "I":
                     #   obj = next(x for x in doc.ents if word.text in x.text).text
                    #else:
                    #    obj = word.text
                # elif word.text in ["Congratulations", "Congrats"] 
                if word.text in ["Congratulations", "Congrats"] and nomType=="PERSON":
                   idx = word.i
                   obj = next((ent for ent in doc.ents if ent.start > idx and ent.label_ == "PERSON"),False)
                   if obj:
                       obj = obj.text
                            
            
            if obj:
                print(tweet)
                print(obj)
                

        return 0

    #returns 1 if First String is Stronger, 2 if second string is stronger, -1 if dissimilar, 0 if partially similar
    #string strength is determined by number of groups
    def VariantSimilarity(self, string1, string2):
        split1 = string1.lower().split(" ")
        split2 = string2.lower().split(" ")
        #a = "supporting" in split1
        #b = "supporting" in split2
        # if (a and not b) or (not a and b):
        #    return -1

        WordGroups = []
        WordGroups2 = []
        internals = []
        for word in split1:
            if len(word) > 3:
                internals.append(word)
            else:
                split1.remove(word)
                if len(internals) > 0:
                    WordGroups.append(internals.copy())
                internals = []
        if len(internals) > 0:
            WordGroups.append(internals.copy())
            internals = []

        for word2 in split2:
            if len(word2) > 3:
                internals.append(word2)
            else:
                split2.remove(word2)
                if len(internals) > 0:
                    WordGroups2.append(internals.copy())
                internals = []
        if len(internals) > 0:
            WordGroups2.append(internals.copy())

        TwoOntoOneMatches = 0
        OneOntoTwoMatches = 0

        for group in WordGroups:
            match = False
            for word2 in split2:
                if word2 in group:
                    match = True
                    break
                #elif word2 in synonyms:
                #    for syno in synonyms[word2]:
                #        if syno in string1.lower():
                #            match = True
                #            break

            if match:
                TwoOntoOneMatches+=1
        for group2 in WordGroups2:
            match = False
            for word in split1:
                if word in group2:
                    match = True
                    break
                """elif word in synonyms:
                    for syno in synonyms[word]:
                        if syno in string1.lower():
                            match = True
                            break"""
            if match:
                OneOntoTwoMatches+=1

        if OneOntoTwoMatches == len(WordGroups2) and TwoOntoOneMatches < len(WordGroups):
            return 0

        if TwoOntoOneMatches == len(WordGroups) and OneOntoTwoMatches < len(WordGroups2):
            return 0

        if OneOntoTwoMatches == len(WordGroups2) and TwoOntoOneMatches == len(WordGroups): 
            if len(WordGroups2) > len(WordGroups):
                return 2
            elif len(WordGroups2) == len(WordGroups):
                return 3
            else:
                return 1

        return -1

    #accepts a sorted dictionary of awards, determines all similarities, returns replaced dictionary
    def AwardSimilarityCombo(self,dicti):
        i = 1
        for key in dicti:
            for key2 in dicti[1:]:
                if key == key2:
                    continue
                sim = self.VariantSimilarity(key,key2)
                if sim == 3:
                    if dicti[key] >= dicti[key2]:
                        dicti[key] += dicti[key2]
                        dicti.pop(key2,1)
                    else:
                        dicti[key2] += dicti[key]
                        dicti.pop(key,1)
                elif sim == 2:
                    dicti[key2] += dicti[key]
                    dicti.pop(key,1)
                elif sim == 1:
                    dicti[key] += dicti[key2]
                    dicti.pop(key2,1)
                    


        



                


         

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

#ap.TheyWonAwardParser([["Best","best"],["Limited Series","limited Series","limited series"],["Actress","actress"],["Supporting"]],"PERSON")

ap.awardFinder2()
#print(ap.VariantSimilarity("Best Supporting Actress in a Motion Picture","Best Performance by an Actress in a Supporting Role in a Motion Picture"))
#ap.CongratulationsParser(["Best Performance by an Actor in a Television Series—Musical or Comedy"],"PERSON")
# 'best television limited series or motion picture made for television'
# cecil b. demille award



#p.NomineeFinder("Drama","TITLE")

#ap.PresenterFinder("Best Director","Sam Mendes")









