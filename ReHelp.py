from TweetBase import TweetBase
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

import re
import json

tb = TweetBase("gg2015.json",2015)
tb.cullTwitterPunctuation()
tb2 = TweetBase("gg2013.json",2013)
tb3 = TweetBase("gg2020.json",2020)

tb2.cullTwitterPunctuation()
tb3.cullTwitterPunctuation()

d = {}
g = {}

for award in OFFICIAL_AWARDS_1315:
    a = tb.ANDorFILTER([award],True)
    b = tb2.ANDorFILTER([award],True)
    d[award] = a
    g[award] = b

e = {}

for award in OFFICIAL_AWARDS_1819:
    c = tb3.ANDorFILTER([award],True)
    e[award] = c

with open("adeeff.json","w",encoding="utf-8") as f:
    json.dump([g,d,e],f)

data = []
with open("adeeff.json",encoding="utf-8") as x:
    data = json.load(x)

g = data[0]
d = data[1]
e = data[2]

def regexTester(expression):
    matched15 = 0
    print("2015:")
    for award in d:
        
        dart = matched15
        for tweet in d[award]:
            ad = re.search(expression,tweet,re.IGNORECASE)
            if ad != None:
                matched15+=1
                #print(ad[0])
                break
        if dart == matched15:
            print("Missing ",award)
    

    print("2013:")
    matched13 = 0
    for award in g:
        dart = matched13
       
        for tweet in g[award]:
            ad = re.search(expression,tweet,re.IGNORECASE)
            if ad != None and "award in ad[0]":
                matched13+=1
                break
        if dart == matched13:
            print("Missing ",award)

    matched20 = 0

    print("2020:")
    for award in e:
        dart = matched20
        
        for tweet in e[award]:
            ad = re.search(expression,tweet,re.IGNORECASE)
            if ad != None and "award in ad[0]":
                matched20+=1
                #print(ad[0])
                break
        if dart == matched20:
            print("Missing ",award)

    print(matched13,matched15,matched20)

#regexTester("(Best|BEST|best)(([\s][A-Z\-][a-z,]{2,})| in a| in an| by an| or| \-| for)+(: | : |\n|[a-z]$)")
#regexTester("(- |^|:|: |,|, |'|\n)(BEST|best|Best) [A-Za-z, \-]+(: | : |\n|$|[\s]*\n|[\s]*$|')")
#regexTester("Best [A-Za-z, \-]+- Golden Globes")
#regexTester("Best [A-Z][A-Za-z ]+ - [A-Za-z, ]+( -|\n|$|[\s]+$)")
#regexTester("(^|\n)Best [A-Z][A-Za-z ]+ - [A-Z][A-Za-z, ]+([\s]+\n|\n|:)")
#regexTester("BEST [A-Z]+ ")
#regexTester("Best .*\-")
#regexTester("(: |[\s]{2,}|^)Best [A-Za-z, \-]+([\s]{2,}|\n|$)")
#adr = tb.getRegexFullMatchOnly(re.compile("(^|\n)Best (([A-Z][a-z, ]+ )|[a-z]{1,2} |- )+(:|\n|$)"))
#regexTester("(: |^)Best [A-Z][A-Za-z ]+ - [A-Za-z ]+( -|\n| : |: )")
#regexTester("\nBest [A-Za-z ,\-]+\n\n")
#regexTester("(^[\s]*|\n[\s*]|:[\s]*|-[\s]*)Best (([A-Z][a-z, ]+ )|[a-z]{1,2} |- )+([\s]*\n|\n|[\s]*:|:)")




