# gg-project-master
Golden Globe NLP Parsing

To run: Install requirements from requirements.txt (primarily spaCy and the English small web-trained model). Place additional years JSON files into the autograder directory. The TweetBase data object parses the JSON model, and requires each year to be named in the gg(year).json format (e.g. gg2016.json). If the JSON file must be located in another directory or have a different name, modify the AwardParser constructor to send the absolute filepath to TweetBase. 

The basic approach is to narrow the field of tweets with broad-level keywords and specific inputs, and then apply named entity recognition and/or regular expressions to parse relevant information. Dependency taggers identify specific grammatical structures (such as Congratulating an award-winner) within filtered phrases and output expected values.

Due to the nature of unresolvable constraints on tweets without hardcoded spellings, we often get many more results than anticipated. While trimming these as best we can with voting and regular expressions, for many of our results, we elected to over-submit on some occasions. (For instance, some people were mentioned as nominees in the field of tweets relating to a certain award. Often, these nominees got fewer votes than noise, so we attempted to leave both in.)

Please note that version management was primarily done locally through VS Code and commits were pushed from a single machine because our team elected to work on said machine during meetings through the LiveShare plugin.

Human Readable Formatting:

A file called Human_Readable.py is included. It can be run, and will print to HR(year).txt. It cannot account for any low readability in the results.

To use, from Human_Readable import Export, and call Export with the year (i.e. Export('2013'))

A version of our output for the year 2013 is submitted as an expected style guide.

Extra Parsing Methods:

1.) Best Dressed - Returns a list of the Top 5 People referenced as being beautiful or dressed well in public commentary, a Golden Globes Red Carpet standard. 

Call from gg_api using get_best_dressed(), or see Notes below for AwardParser call implementation

Expect a result like : ["Bob Jones","Rick Smith","Susie Johnson","Jane Doe","Julie Friend"]

2.) Drinking Games - Returns a list of proposed drinking games, seemingly the most common reason to watch the Globes at all.

Call from gg_api using get_games(), or see Notes for AwardParser call implementation.

Expect a result like : ["When ...","If...","EveryTime..."]
This function will return slightly different results each time it is run. We are not responsible for the irresponsible games mentioned.

3.) Weinstein Association Tracker - Returns a list of one-word associations to track the history of mentions of an infamous Hollywood exec in regards to the scene of Hollywood stars before and after public disgrace.

Call from gg_api using get_weinstein(), or see Notes for AwardParser call implementation.

Expect a result like : {"unique-mentions":30, "most-associated-terms":["trial","scandal","walker","complacent","disgrace"]}



Other Notes:

 - Our implementation is an AwardParser object. You can run any of these methods from the python console with:

from AwardParse import AwardParser
myAwardParser = AwardParser(2015)
ap.Top5BestDressed()
ap.DrinkingGames()
ap.WeinsteinMachine()



