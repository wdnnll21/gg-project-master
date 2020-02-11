# gg-project-master
Golden Globe NLP Parsing

To run: Install requirements from requirements.txt (primarily spaCy and the English small web-trained model). Place additional years JSON files into the autograder directory. The TweetBase data object parses the JSON model, and requires each year to be named in the gg(year).json format (e.g. gg2016.json). If the JSON file must be located in another directory or have a different name, modify the AwardParser constructor to send the absolute filepath to TweetBase. 


The basic approach is to narrow the field of tweets with broad-level keywords and specific inputs, and then apply named entity recognition and/or regular expressions to parse relevant information. Dependency taggers identify specific grammatical structures (such as Congratulating an award-winner) within filtered phrases and output expected values.


Please note that version management was primarily done locally through VS Code and commits were pushed from a single machine because our team elected to work on said machine during meetings through the LiveShare plugin.


