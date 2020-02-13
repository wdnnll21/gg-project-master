import gg_api

def Export(year):
    official_awards = gg_api.OFFICIAL_AWARDS_1819
    if int(year) <= 2015:
        official_awards = gg_api.OFFICIAL_AWARDS_1315

    host = gg_api.get_hosts(year)
    awards = gg_api.get_awards(year)
    nominees = gg_api.get_nominees(year)
    presenters = gg_api.get_presenters(year)
    winners = gg_api.get_winner(year)
    games = gg_api.get_games(year)
    weinstein = gg_api.get_weinstein(year)
    bestdressed = gg_api.get_best_dressed(year)

    stringout = "GOLDEN GLOBES " + str(year) + "\n\n"
    stringout += "Hosts: " + str(host) + "\n\n"
    stringout += "Awards: \n"

    for string in awards:
        stringout += str(string) + "\n"

    stringout += "\nWinners, Presenters, and Nominees:\n"
    for award in official_awards:
        stringout+="Award: " + award + "\n"
        stringout+="Winner: " + winners[award] + "\n"
        stringout+="Nominees: " + str(nominees[award]) + "\n"
        stringout+="Presenters: " + str(presenters[award]) + "\n" 
        stringout+="\n"

    stringout += "\nBest Dressed:\n"
    for string in bestdressed:
        stringout += string + "\n"

    stringout += "\nSome Drinking Games:\n"
    for string in games:
        stringout += string + "\n"

    stringout += "\nWeinstein Analysis:\nNumber of Unique Mentions:" + str(weinstein['unique-mentions']) + "\nMost Associated Terms:\n" + str(weinstein['most-associated-terms'])

    with open("HR" + str(year) + ".txt","w",encoding = "utf-8") as j:
        j.write(stringout)

    



