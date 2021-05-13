from nltk.parse import stanford
import os
os.environ['STANFORD_PARSER'] = '/Users/hungphan/git/dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
os.environ['STANFORD_MODELS'] = '/Users/hungphan/git/dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
sp = stanford.StanfordParser()
trees = [tree for tree in sp.parse("this is a sentence".split())]
print(trees[0])