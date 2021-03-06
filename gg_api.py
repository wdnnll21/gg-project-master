'''Version 0.35'''
import AwardParse
from AwardParse import AwardParser 

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
ap = None

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    return ap.HostFinder()

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    print("got awards",year)
    return ap.awardParseRegexFinal()
    

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    if year in ['2013','2015']:
        ap.acceptActualAwards(OFFICIAL_AWARDS_1315)
        if len(ap.winners) == 0:
            get_winner(year)
        return ap.FindAllNominees()
    else:
        ap.acceptActualAwards(OFFICIAL_AWARDS_1819)
        if len(ap.winners) == 0:
            get_winner(year)
        return ap.FindAllNominees()

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    if ap.year == year and len(ap.winners) > 1:
        return ap.winners
    if year in ['2013','2015']:
        ap.acceptActualAwards(OFFICIAL_AWARDS_1315)
        return ap.FindAllWinners()
    else:
        ap.acceptActualAwards(OFFICIAL_AWARDS_1819)
        return ap.FindAllWinners()

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    if year in ['2013','2015']:
        ap.acceptActualAwards(OFFICIAL_AWARDS_1315)
        return ap.getAllPresenters()
    else:
        ap.acceptActualAwards(OFFICIAL_AWARDS_1819)
        return ap.getAllPresenters()

def get_games(year):
    """ap.DrinkingGames returns a list of every unique drinking game
    submitted at the Golden Globes
    """
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    return ap.DrinkingGames()

def get_weinstein(year):
    """Weinstein returns a dictionary with two keys: unique-mentions (valued as a number)
    and most-associated-terms (a list of strings)
    """
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    return ap.WeinsteinMachine()

def get_best_dressed(year):
    """Returns a list of 5 well-dressed individuals"""
    global ap
    if ap == None or ap.year != year:
        ap = AwardParser(year)
    return ap.Top5BestDressed()


def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    return

if __name__ == '__main__':
    main()
