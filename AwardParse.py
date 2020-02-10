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

    def awardFinder2(self):
        docs = []
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
            for punct in ["!",".",":",","]:
                splt[end-1] = splt[end-1].replace(punct,"")
            result = " ".join(splt[indx:end])
            if result.lower() in awards:
                awards[result.lower()] += 1
            else:
                awards[result.lower()] = 1

        awardlist = sorted(awards,key=awards.get)
        response = {}

        for award in awardlist:
            strl = award
            strl = strl.replace(","," -")
            strl = strl.replace("tv","television")
            if "-" in award:
                if award.index("-") < 14:
                    continue
                elif "-" in strl[strl.index("-") + 1:]:
                    strl = strl[0:strl[strl.index("-") + 1:].index("-")]
            if len(award) < 22:
                continue
            if " at " in award or "you" in award:
                continue
            response[strl] = awards[award]
        
        """graph = {}
        roots = []
        others = []
        i = 1
        for award in response.keys():
            g = self.AwardGroupParse(award)
            children = []
            parents = []
            for awardz in list(response.keys())[i:]:
                if award != awardz:
                    h = self.AwardGroupParse(awardz)
                    leveler = self.SameAward(g,h)
                    if leveler == 1:
                        children.append(awardz)
                    if leveler == 2:
                        parents.append(awardz)
            graph[award] = [children,parents]
            if parents == [] and children != []:
                roots.append(award)
            else:
                others.append(award)
            i+=1

        for root in roots:
            for child in graph[root][0]:
                if len(graph[child][1]) > 0:
                    response[root] += response[child] / len(graph[child][1])
                else:
                    response[root] += response[child]

        for unit in others:
            response[unit] = -1 """

        print([(x, response[x]) for x in response if response[x] > 1])
        

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
        
        firstcull = self.datab.ANDorFILTER([[award],["wins","goes to",award + " - "]],True)
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
        for aA in self.actualAwards:
            gG = self.AwardGroupParse(aA)
            nomType = "MEDIA"
            if "act" in aA or "direct" in aA or "screenp" in aA or "award" in aA:
                nomType = "PERSON"
            
            if nomType == "PERSON":
                win1 = self.TheyWonAwardParser([aA],nomType)
                if not win1 or win1 == "who":
                    win1 = self.WinnerFinder(aA,nomType)
                if win1 == '':
                    win1 = self.CongratulationsParser(gG,nomType)
                if win1 == False:
                    win1 = ''
                allWinners[aA] = win1
            else:
                win1 = self.WinnerFinder(aA,nomType)
                if win1 == '':
                    win1 = self.TheyWonAwardParser([aA],nomType)
                if win1 == False:
                    win1 = self.CongratulationsParser(gG,nomType)
                if win1 == False:
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
            
            if "act" in aA or "direct" in aA or "screenp" in aA:
                nomType = "PERSON"
            
            mergedNominees = self.NominatedForParser(aA,nomType)
            if aA in self.winners and self.winners[aA] not in [False,None,'']:
                mergedNominees.update(self.BeatParser([self.winners[aA]],nomType))

            
            if len(mergedNominees) > 5:
                allNominees[aA] = sorted(mergedNominees,key=mergedNominees.get)[-5:]
            else:
                allNominees[aA] = list(mergedNominees)
        
        return allNominees
                

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
                    tfind = match[0].replace("\"","").replace("\'","").lower()
                    if tfind in nomVote:
                        nomVote[tfind] += 1
                    else:
                        nomVote[tfind] = 1

    def PresenterFinder(self, award, winner):
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
            return [a[-1],a[-2]]

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
        firstcull = self.datab.ANDorFILTER(filters,True)
        winVote = {}
        docs = []

        if len(firstcull) > 100:
            firstcull = firstcull[0:100]

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
        filters.extend([["congratulations","congrats"],["for winning best","for winning the award","for best"]])
        if nomType == "MEDIA":
            filters.append("\"")
        firstcull = self.datab.ANDorFILTER(filters,True)
        winVote = {}
        
        if len(firstcull) > 100:
            firstcull = firstcull[0:100]

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

    def SameAward(self,groups1,groups2):
        TotalMatch1 = True
        TotalMatch2 = True
        EveryWordMatch1 = True
        EveryWordMatch2 = True

        for group in groups1:
            onefound = False
            for word in group:
                found = False
                for groupb in groups2:
                    if word in groupb:
                        found = True
                        onefound = True
                        break
                if found == False:
                    EveryWordMatch1 = False
                else:
                    break
            if onefound == False:
                TotalMatch1 = False
        
        for groupb in groups2:
            onefound = False
            for word in groupb:
                found = False
                for groupa in groups1:
                    if word in groupa:
                        found = True
                        onefound = True
                        break
                if found == False:
                    EveryWordMatch2 = False
                else:
                    break
            if onefound == False:
                TotalMatch2 = False

        if EveryWordMatch1 and EveryWordMatch2:
            if len(groups1) > len(groups2):
                return 1
            return 2
        if TotalMatch1 and TotalMatch2 and EveryWordMatch1:
            return 2
        if TotalMatch1 and TotalMatch2 and EveryWordMatch2:
            return 1
        if TotalMatch1 and TotalMatch2:
            if len(groups1) > len(groups2):
                return 1
            return 2
        else:
            return 0

    """def SameAwardB(self,awarda,awardb):
        award1 = awarda.lower()
        award2 = awardb.lower()
        for filtere in ["-",".",", i",","," in "," by "," a "," an ", " or ","!",":",";","\'","\"","\n"]:
            award1 = award1.replace(filtere," ")
            award2 = award2.replace(filtere," ")
        award1.replace("tv","television")
        award2.replace("tv","television")

        split1 = award1.split(" ")
        split2 = award2.split(" ")

        TotalMatch = True
        Tmatch2 = True
        for word1 in split1:
            if word1 not in award2:
                TotalMatch = False
                break
        for word2 in split2:
            if word2 not in award1:
                Tmatch2 = False
                break

        if TotalMatch and Tmatch2:
            if " - " in awarda and " - " not in awardb:
                return awarda
            if " - " in awardb and " - " not in awarda:
                return awardb
            if len(awarda) >= len(awardb):
                return awarda
            else:
                return awardb
        if TotalMatch:
            return awardb
        if Tmatch2:
            return awarda
        return False"""

    """#accepts a sorted dictionary of awards, determines all similarities, returns replaced dictionary
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
                    dicti.pop(key2,1)   """

    def NominatedForParser(self,award,nomType):
        groups = self.AwardGroupParse(award)

        filters = [[" nomin"]]
        filters.extend(groups)
        nominees = {}
        if nomType == "MEDIA":
            filters.append(["\"","\'"])
            firstcull = self.datab.ANDorFILTER(filters,True)
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
            firstcull = self.datab.ANDorFILTER(filters,True)
            if(len(firstcull) > 100):
                firstcull = firstcull[0:100]
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
        filters = [winner,[" beat"," rob"," stole"," steal"]]
        firstcull = self.datab.ANDorFILTER(filters,True)
            
        nominees = {}
        if len(firstcull) > 100:
            firstcull = firstcull[0:100]
        for tweet in firstcull:
            doc = spacyNLP(tweet)
            if nomtype == "PERSON":
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and ent.text not in winner and "olden" not in ent.lower_:
                        if ent.lower_ in nominees:
                            nominees[ent.lower_]+=1
                        else:
                            nominees[ent.lower_]=1
            else:
                for word in doc:
                    if word.dep_ == "dobj" and word.head.text in ["beat","beats","rob","robbed","stole","steal","steals"] and word.text[0].isupper():
                        a = self.MovieNameFinder(word.text).replace("\"","").replace("\'","").lower()
                        if a in nominees:
                            nominees[a]+=1
                        else:
                            nominees[a]=1
        
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
            
    def PresenterFinder2(self, award):
        groups = self.AwardGroupParse(award)
        filters = [[" present"," announc"]]
        filters.extend(groups)
        firstcull = self.datab.ANDorFILTER(filters,True)

        presenters = {}
        if len(firstcull) > 500:
            firstcull = firstcull[0:500]
        for tweet in firstcull: 
            doc = spacyNLP(tweet)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and "olden" not in ent.text:
                    if ent.lower_ in presenters:
                        presenters[ent.lower_] += 1
                    else:
                        presenters[ent.lower_] = 1

        a = sorted(presenters)
        for f in a:
            f.encode('ascii','ignore').decode('unicode_escape')
            if f == '\'':
                a.remove(f)
        if len(a) == 0:
            #return self.PresenterFinder(award,self.winners[award])
            return []
        elif len(a) == 1:
            #r = self.PresenterFinder(award,self.winners[award])
            #if len(r) > 0:
            #    return [a[-1],r[0]]
            return [a[-1]]
        else:
            return [a[-1],a[-2]]
        

    def Top5BestDressed(self):
        firstcull = self.datab.ANDorFILTER([["beautiful","gorgeous","ravishing","best dressed"]],False)

        docs = []
        hostVote = {}
        if len(firstcull) > 500:
            firstcull = firstcull[0:500]

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

    def awardParseClosed(self):
        awardParse = self.awardparseOpen()
        if awardParse == []:
            self.awardFinder2()

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
            

ap = AwardParser(2015)
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
ap.acceptActualAwards(OFFICIAL_AWARDS_1315)
print(ap.FindAllWinners())
#print(ap.awardParseRegex())

#ap.TheyWonAwardParser([["Best","best"],["Limited Series","limited Series","limited series"],["Actress","actress"],["Supporting"]],"PERSON")

#ap.DrinkingGames()

#print(ap.awardFinder2())
#print(ap.SameAward("best actor in a motion picture drama","best performance by an actor in a motion picture - drama")
#)
#print(ap.HostFinder()) 
#print(ap.datab.ANDorFILTER([])


#print(ap.CongratulationsParser([["best motion picture"],["drama"]],"MEDIA"))