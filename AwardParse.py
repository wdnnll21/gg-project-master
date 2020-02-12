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
    def __init__(self,year,filepath = None):
        if filepath == None:
            self.datab = TweetBase("gg" + str(year) + ".json",year)
        else:
            self.datab = TweetBase(filepath,year)
        print("Starting cull",year)
        self.datab.cullTwitterPunctuation()
        #self.awardFilter = self.datab.anyStringList(["award for Best "])
        self.actualAwards = []
        self.year = year
        self.movienames = []
        self.winners = {}
        self.HardQueries = {}

    def PopulateHardQueries(self):
        if len(self.HardQueries) == 0:
            self.HardQueries = self.datab.PopulateHardQueries()    
    
    def HostFinder(self):
        firstcull = self.datab.anyStringList([" is hosting"])
        secondcull = self.datab.anyStringList([" are hosting"])
        
        multihost = len(secondcull) > len(firstcull)

        if multihost: firstcull = secondcull

        docs = []
        hostVote = {}

        for tweet in firstcull:
            docs.append(spacyNLP(tweet))

        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    if len(ent.text.split(" ")) == 1:
                        continue
                    if ent.lower_ in hostVote:
                        hostVote[ent.lower_] += 1
                    else:
                        hostVote[ent.lower_] = 1
        
        if multihost:
            hVs = sorted(hostVote,key = hostVote.get)
            return [hVs[-1],hVs[-2]]

        return max(hostVote,key=hostVote.get)

    def WinnerFinder(self, award, nomType):
        self.PopulateHardQueries()

        firstcull = list(filter(lambda tweet: any(kw in tweet for kw in ["wins","goes to",award + "-"]),self.HardQueries[award]))
        docs = []
        winVote = {}
        if nomType == "PERSON":
            for tweet in firstcull:
                docs.append(spacyNLP(tweet))
            
                for doc in docs:
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":
                            if ent.lower_ in winVote:
                                winVote[ent.lower_] += 1
                            else:
                                winVote[ent.lower_] = 1
        else:
            for tweet in firstcull:
                titlefind = list(re.finditer(r"([\"])(?:(?=(\\?))\2.)*?\1", tweet))
                if len(titlefind) > 0:
                    if titlefind[0][0] in winVote:
                        winVote[titlefind[0][0]] += 1
                    else:
                        winVote[titlefind[0][0]] = 1 


        
        if len(winVote) == 0:
            return ""
        return max(winVote, key=winVote.get)

    def acceptActualAwards(self, actualList):
        self.actualAwards = actualList

    def FindAllWinners(self):
        print("finding winners",self.year)
        allWinners = {}
        self.PopulateHardQueries()
        
        for aA in self.actualAwards:
            nomType = "MEDIA"
            if "act" in aA or "direct" in aA or "screenp" in aA or "award" in aA:
                nomType = "PERSON"
            
            if nomType == "PERSON":
                win1 = self.TheyWonAwardParser(aA,nomType)
                if not win1 or win1 == "who":
                    win1 = self.WinnerFinder(aA,nomType)
                if win1 == '':
                    win1 = self.CongratulationsParser(aA,nomType)
                if win1 == None or win1 == False:
                    win1 = ''
                allWinners[aA] = win1
            else:
                win1 = self.WinnerFinder(aA,nomType)
                if win1 == '':
                    win1 = self.TheyWonAwardParser(aA,nomType)
                if win1 == False:
                    win1 = self.CongratulationsParser(aA,nomType)
                if win1 == None:
                    win1 = ''
                win1 = win1.replace("\"","").lower()
                allWinners[aA] = win1

        self.winners = allWinners
        return allWinners

    def FindAllNominees(self):
        print("finding nominees",self.year)
        allNominees = {}
        for aA in self.actualAwards:
            nomType = "MEDIA"
            
            if "act" in aA or "direct" in aA or "screenp" in aA or "cec" in aA:
                nomType = "PERSON"
            
            nN = self.newNominees(aA)
            if nN != []:
                allNominees[aA] = nN
                continue

            mergedNominees = self.NominatedForParser(aA,nomType)
            if aA in self.winners and self.winners[aA] not in [False,None,'']:
                mergedNominees.update(self.BeatParser([self.winners[aA]],nomType))

            
            if len(mergedNominees) > 9:
                allNominees[aA] = sorted(mergedNominees,key=mergedNominees.get)[-9:]
            else:
                allNominees[aA] = list(mergedNominees)
        
        return allNominees
                

    """def NomineeFinder(self, award, nomType):
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
                    tfind = match[0].replace("\"","").replace("\'","").lower()
                    if tfind in nomVote:
                        nomVote[tfind] += 1
                    else:
                        nomVote[tfind] = 1"""

    """def PresenterFinder(self, award, winner):
        winTime = self.datab.earliestMention([award,winner,"won"])
        if winTime == None:
            return []
        if self.year == 2020:
            winnerTime = datetime.strptime(winTime,"%Y-%m-%dT%H:%M:%S")
            End = winnerTime + timedelta(minutes=5)
            Start = winnerTime - timedelta(minutes=5)
            tenMinuteList = self.datab.timeFrameFilter(str(Start).replace(" ","T"),str(End).replace(" ","T"))
        else:
            End = winTime + 300000
            Start = winTime - 300000
            tenMinuteList = self.datab.timeFrameFilter(Start,End)
        

        kwlist = [" announc"," present"," on stage"," read"]
        PresenterFilter = filter(lambda tweet: any(kw in tweet for kw in kwlist), tenMinuteList)
        pVote = {}

        for presentertweet in list(PresenterFilter):
            doc = spacyNLP(presentertweet)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and "olden" not in ent.text and ent.lower_ not in winner:
                    if ent.lower_ in pVote:
                        pVote[ent.lower_]+=1
                    else:
                        pVote[ent.lower_]=1
        
        a = sorted(pVote,key=pVote.get)

        if len(pVote) == 0:
            return []
        elif len(pVote) == 1 or pVote[a[-2]] < pVote[a[-1]]/2:
            return [a[-1]]
        else:
            return [a[-1],a[-2]]"""

    """"def NameVariantFinder(self,person):
        variants = [person]
        personarray = person.split(" ")
        variants.append(personarray[0])
        variants.append(personarray[1])
        variants.append(personarray[0] + personarray[1])

        return variants"""

    def TheyWonAwardParser(self,filters, nomType):
        filterb = ["wins","won"]
        if nomType == "MEDIA":
            filterb.append("\"")
        firstcull = list(filter(lambda tweet: all(kw in tweet for kw in filterb),self.HardQueries[filters]))
        winVote = {}
        docs = []

        for tweet in firstcull:
            mentionedMovies = list(re.finditer(r"([\"'])(?:(?=(\\?))\2.)*?\1", tweet))
            for mMovie in mentionedMovies:
                if len(mMovie[0]) > 30:
                    mentionedMovies.remove(mMovie)
            
            if len(mentionedMovies) == 0:
                continue

            subj = ""
            pred = ""
            ignore = False
            doc = spacyNLP(tweet)

            for word in doc:
                if word.text == ".":
                    break
                if nomType == "MEDIA" and word.text == "\"":
                    subj = mentionedMovies[0][0]
                if word.dep_ in ["nsubj","nsubjpass"] and word.head.text in ["wins","won"] and nomType == "PERSON":
                    if word.ent_iob_ == "I":
                        subj = next(x for x in doc.ents if word.text in x.text).lower_
                    else:
                        subj = word.text.lower()
                elif word.dep_ == "dobj" and word.head.text in ["wins","won"]:
                    pred = word.text

            
            if not ignore and subj != "" and pred != "":
                if subj in winVote:
                    winVote[subj]+=1
                else:
                    winVote[subj]=1
            
        if len(winVote) == 0:
            return False

        return max(winVote,key=winVote.get)

    def CongratulationsParser(self, filters, nomType):
        filterb = [["congratulations","congrats"],["for winning best","for winning the award","for best"]]
        if nomType == "MEDIA":
            filterb.append("\"")
        firstcull = list(filter(lambda tweet: all(kw in tweet for kw in filterb[0]) and all(kw in tweet for kw in filterb[1]),self.HardQueries[filters]))
        winVote = {}
        

        for tweet in firstcull:
            mentionedMovies = list(re.finditer(r"([\"'])(?:(?=(\\?))\2.)*?\1", tweet))
            if mentionedMovies == [] and nomType == "MEDIA":
                continue
            obj = ""
            doc = spacyNLP(tweet)

            for word in doc:
                if word.text == ".":
                    break
                if nomType=="MEDIA" and word.text=="\"":
                    obj = mentionedMovies[0][0]
                    break
                if word.text in ["congratulations", "congrats", "Congratulations", "Congrats"] and nomType=="PERSON":
                    idx = word.i
                    obj = next((ent for ent in doc.ents if ent.start > idx and ent.label_ == "PERSON"),False)
                    if obj:
                       obj = obj.text
                    break
            
            """if obj:
                print(tweet)
                print(obj)"""
            if obj != "" and obj in winVote:
                winVote[obj]+=1
            else:
                winVote[obj]=1

        if len(winVote) == 0:
            return None
        
        return max(winVote, key=winVote.get)

    def AwardGroupParse(self,award):
        award1 = award.lower()
        for filtere in [".",", i",","," a "," an ", " or ","!",":",";","\'","\"","\n"]:
            award1 = award1.replace(filtere," ")
        for filterd in [" in ", " by ", " - "]:
            award1 = award1.replace(filterd,"|")

        award1.replace("tv","television")

        split1 = award1.split("|")
        split2 = []
        for segment in split1:
            split2.append(segment.split(" "))
        
        return split2

    def NominatedForParser(self,award,nomType):
        self.PopulateHardQueries()

        firstcull = self.HardQueries[award]
        if nomType == "MEDIA":
            firstcull = list(filter(lambda tweet: all(kw in tweet for kw in ["\""," nomin"]),firstcull))
        else:
            firstcull = list(filter(lambda tweet: all(kw in tweet for kw in [" nomin"]),firstcull))
        nominees = {}
        if nomType == "MEDIA":
            for tweet in firstcull:
                mentionedMovies = list(re.finditer(r"([\"'])(?:(?=(\\?))\2.)*?\1", tweet))
                for mMovie in mentionedMovies:
                    if len(mMovie[0]) > 30:
                        continue
                    if mMovie[0] not in self.movienames:
                        self.movienames.append(mMovie[0])
                    a = mMovie[0].lower().replace("\"","").replace("\'","")
                    if a in nominees:
                        nominees[a]+=1
                    else:
                        nominees[a]=1

        else:
            for tweet in firstcull:
                doc = spacyNLP(tweet)
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and "olden" not in ent.lower_:
                        if ent.lower_ in nominees:
                            nominees[ent.lower_]+=1
                        else:
                            nominees[ent.lower_] = 1

        return nominees

    def BeatParser(self,winner,nomtype):
        filters = [winner,[" beat"," rob"," stole"," steal"],(" de "," en "," y "," lo ", " la ", " el ", " los ")]
        firstcull = self.datab.ANDorFILTER(filters,True)
            
        nominees = {}
        for tweet in firstcull:
            doc = spacyNLP(tweet)
            if nomtype == "PERSON":
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and ent.lower_ not in winner and "olden" not in ent.lower_:
                        if ent.lower_ in nominees:
                            nominees[ent.lower_]+=1
                        else:
                            nominees[ent.lower_]=1
            else:
                for word in doc:
                    if word.dep_ == "dobj" and word.head.text in ["beat","beats","rob","robbed","stole","steal","steals"] and word.text[0].isupper():
                        titleIndex = word.i+1
                        movieTitle = [word.text]
                        nextWord = doc[titleIndex].text
                        titleComplete = False
                        while not titleComplete and titleIndex < len(doc) - 1:
                            if nextWord[0].isupper():
                                movieTitle.append(nextWord)
                                titleIndex+=1
                                nextWord = doc[titleIndex].text
                            elif not nextWord[0].isupper() and nextWord in ["of","the","in","a"]:
                                movieTitle.append(nextWord)
                                titleIndex+=1
                                nextWord = doc[titleIndex].text
                            else:
                                titleComplete = True
                        movieTitle = " ".join(movieTitle)
                        a = self.MovieNameFinder(movieTitle).replace("\"","").replace("\'","").lower()
                        if a in nominees:
                            nominees[a]+=1
                        else:
                            nominees[a]=1
                        break
        
        return nominees

    def MovieNameFinder(self, word):
        for mName in self.movienames:
            if word in mName:
                return mName
        
        filters = [["\""],word]
        firstcull = self.datab.ANDorFILTER(filters)

        vote = {}
        for tweet in firstcull:
            mentionedMovies = list(re.finditer(r"([\"'])(?:(?=(\\?))\2.)*?\1", tweet))
            for mMovie in mentionedMovies:
                if word in mMovie[0] and len(mMovie[0]) < 30:
                    self.movienames.append(mMovie[0])
                    if mMovie[0] in vote:
                        vote[mMovie[0]]+=1
                    else:
                        vote[mMovie[0]] = 1

        if vote != {}:
            return max(vote,key=vote.get)
        return word
            
    def firstNameFinder(self, lastName):
        filters = [lastName]
        firstcull = self.datab.ANDorFILTER(filters,True)

        for tweet in firstcull:
            doc = spacyNLP(tweet)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and lastName in ent.text and lastName!=ent.text:
                    return ent.text

    def AllPresentersFinder(self):
        print("finding presenters",self.year)
        presenters = {}
        for award in self.actualAwards:
            presenters[award] = self.PresenterFinder2(award)
        
        return presenters
    

    def getAllPresenters(self):
        stopWords = ('hate', 'love','hope','good','bad',' en ',' los ',' de ',' la ', ' un ', 'drink', 'should', 'could', 'would', ' i ', 
                    ' im ', ' i\'m ', '?', '!!')
        filters = [['present', 'announc'],stopWords]
        
        firstcull = self.datab.ANDorFILTER(filters,True)

        presenters = {}
        fullName = re.compile(r"^([A-Z][a-z]+ (?:[A-Z][a-z]+)*)$")

        for tweet in firstcull:
            doc = spacyNLP(tweet)

            for ent in doc.ents:
                if ent.label_ == "PERSON" and fullName.match(ent.text) and ent.text in presenters:
                    presenters[ent.text]+=1
                elif ent.label_ == "PERSON" and fullName.match(ent.text) and not ent.text in presenters and not "olden" in ent.text and not "present" in ent.lower_ and not "win"  in ent.lower_:
                    presenters[ent.text]=1

        '''
        finalPresenters = {}
        self.PopulateHardQueries()
        
        for name in presenters:
            for award, awardTweets in self.HardQueries.items():
                for tweet in awardTweets:
                    if "present" in tweet and "win" not in tweet:
                        if any(name in tweet.lower() for name in name.split()) and award in finalPresenters:
                            if any(name in finalPresenters[award] for name in name.split()):
                                continue
                            else:
                                finalPresenters[award].append(name)
                                break
                        elif any(name in tweet.lower() for name in name.split()) and not award in finalPresenters:
                            finalPresenters[award] = [name]
        '''
        finalPresenters = {}
        self.PopulateHardQueries()
        presenters = set(presenters)
        culledPresenters = set()

        for presenter in presenters:
            if not 'win' in presenter.lower() and not 'olden'  in presenter.lower() and not 'best'  in presenter.lower() and not presenter.lower() in self.winners.values():
                culledPresenters.add(presenter)

        for award, awardTweets in self.HardQueries.items():
            for tweet in awardTweets:
                for name in culledPresenters:
                    if name in tweet and 'present' in tweet.lower() and not 'win' in tweet.lower() and award in finalPresenters:
                        if not name.lower() in finalPresenters[award]:
                            finalPresenters[award].append(name.lower())
                    elif name in tweet and 'present' in tweet.lower() and not 'win'  in tweet.lower() and not award in finalPresenters:
                        finalPresenters[award] = [name.lower()]

        for award in self.HardQueries:
            if not award in finalPresenters:
                finalPresenters[award] = self.PresenterFinder2(award)

        return finalPresenters

    def PresenterFinder2(self, award):
        self.PopulateHardQueries()
        firstcull = self.HardQueries[award]

        firstcull = list(filter(lambda tweet: any(kw in tweet for kw in ["present","announc"]),firstcull))
        
        docs = []
        hostVote = {}

        for tweet in firstcull:
            docs.append(spacyNLP(tweet))

        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == "PERSON" and "olden" not in ent.text:
                    if ent.lower_ in hostVote:
                        hostVote[ent.lower_] += 1
                    else:
                        hostVote[ent.lower_] = 1

        hVs = sorted(hostVote,key = hostVote.get)

        if len(hVs) < 5:
            return hVs
        if len(hVs) == 0:
            return []
        return hVs[-5:]

    def DrinkingGames(self):
        firstcull = self.datab.ANDorFILTER([["drinking game", "drink!", "take a drink", "drink every", "drink when"]])
        firstcull = list(set(firstcull))

        for tweet in firstcull:
            ltweet = tweet.lower()
            if "drinking game:" in ltweet:
                print(tweet[ltweet.index("game:")+5:])
                continue
            for st in ["when "," if "," every "]:
                if st in ltweet:
                    print(tweet[ltweet.index(st):])
                    continue

    def awardparseOpen(self):
        awards = []

        format1 = [re.compile("^(BEST|best|Best) [A-Z]")]
        format2 = [re.compile("Best(([\s][A-Z\-][a-z,]{2,})| in a| in an| by an| or| \-| for)+")]

        firstcull = self.datab.ANDorFILTER([re.compile("^Best [A-Z]"),re.compile("   \n$"),"\n\n"])
        for string in firstcull:
            awards.append(string[0:string.index("\n\n")])
        if firstcull == []:
            firstcull = self.datab.ANDorFILTER([re.compile("^Best [A-Z]"),re.compile("[a-z] $"),[" : "]])
            for string in firstcull:
                awards.append(string[0:string.index(": ")])
            secondcull = self.datab.ANDorFILTER([re.compile("[a-z] - Best [A-Z]"),re.compile("[a-z][a-z]$")])
            for string in secondcull:
                awards.append(string[string.index(" - "):]) 

        return awards

    def awardParseRegex2(self):
        #regexParse = self.datab.getRegexFullMatchOnly(re.compile("Best(([\s][A-Z][a-z,\-]{2,})| in a| in an| by an| or| \-| for)+([\s][A-Z][a-z]{2,})"))
        regexParse = self.datab.getRegexFullMatchOnly(re.compile("^BEST [A-Z\-, ]+"))
        awardDict = {}

        stopwords = ["joke","carpet","dress","olden","look","moment","award","the","--","hosts"]
        for item in regexParse:
            add = True
            if any(kw in item.lower() for kw in stopwords) or len(item.split(" ")) < 4:
                add = False

            dash = item.split(" - ")
            if len(dash) > 2:
                item = " - ".join([dash[0],dash[1]])
            if len(dash) == 2 and len(dash[1].split(" ")) > 3:
                add = False
            
            if "-" in item[-5:]:
                add = False

            if add:
                if item in awardDict:
                    awardDict[item]+=1
                else:
                    awardDict[item]=1

        print(sorted(awardDict))


    def awardParseRegex(self):
        print("parsing awards",self.year)
        regexParse = self.datab.getRegexFullMatchOnly(re.compile("Best(([\s][A-Z\-][a-z,]{2,})| in a| in an| by an| or| \-| for)+"))
        tangent = ["on Picture","Series"]
        antiTangent = ["Should", "t Ac", "t Su"," a F","t Fi","olden"]
        duoTangent = [(",",", L"),("for","for Te")]
        if(int(self.year) <= 2015):
            tangent.append("Film")
        
        r2 = list(filter(lambda match: any([kw in match for kw in tangent]),regexParse))
        r3 = list(filter(lambda cull: 
            len(cull.split(" ")) > 3 and len(cull.split("\n")) == 1 and len(cull.split("-")) < 3 and not any([kw in cull for kw in antiTangent]) and
            cull[-1] not in ["r","-","n"] and not any([kw[0] in cull and not kw[1] in cull for kw in duoTangent]),r2))

        vote = {}
        for string in r3:
            if string.replace("- ","") in vote:
                vote[string] = vote[string.replace("- ","")] + 1
                del vote[string.replace("- ","")]
            elif string in vote:
                vote[string] += 1
            else:
                vote[string] = 1

        return [x for x in vote if vote[x] > 1]


    def WeinsteinMachine(self):
        firstcull = self.datab.ANDorFILTER([["Weinstein","Harvey Weinstein","Harvey","Weinzstein","Wienstien","Weinstien"]])
        context = {}
        mentionTimes = len(firstcull)
        for tweet in firstcull:
            doc = spacyNLP(tweet)
            idx = 0
            for word in doc:
                if word.text in ["Weinstein","Harvey"]:
                    idx = word.i
                    break
            start = max(idx - 3,0)
            end = min(idx + 3, len(list(doc)))
            for word in doc[start:end+1]: 
                if word.tag_ in ["NNP","NNP","NNPS","NNS","NN","VBD","VBG","VBP","VBZ"] and word.text not in ["Weinstein","Harvey","Golden","Globes"] and len(word.text) > 3:
                    if word.text in context:
                        context[word.text]+=1
                    else:
                        context[word.text]=1
                
        
        chunky = sorted(context,key=context.get)
        dictma = {'unique-mentions':mentionTimes,'most-associated-terms':chunky[-7:]}
        return dictma

    def newNominees(self,award):
        self.PopulateHardQueries()

        query = self.HardQueries[award]
        filledQ = list(filter(lambda tweet: "nominees:" in tweet and not any(kw in tweet for kw in ["present","won","win","not","n't","goes","?"]),query))

        for string in filledQ:
            spd = string[string.index("nominees:")+9:]
            a = spd.replace("and", "").split(",")
            if len(a) > 1:
                return a
        
        return []

            


        
                

            

ap = AwardParser(2015)
print(ap.awardParseRegex2())
#ap.awardParseRegex2()
#print(ap.WeinsteinMachine())
#OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
#ap.acceptActualAwards(OFFICIAL_AWARDS_1315)
#ap.FindAllWinners()
#print(ap.newNominees())
#print(ap.BeatParser("how to train your dragon 2","MEDIA"))
#print(ap.newNominees())
#print(ap.FindAllNominees())
#print(ap.AllPresentersFinder())
#print(ap.getAllPresenters())
#print(ap.getAllPresenters())#print(ap.datab.ANDorFILTER([])
