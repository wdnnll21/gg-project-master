class AwardPoints(object):
    def __init__(self,nom,med,cat):
        self.nomType = 
        self.medType = 
        self.nomcategory =
        self.medcategory = 

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


    



    
    




    
        