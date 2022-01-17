import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('../..')))
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions_RTX3090 import createDirIfNotExist,getPOSInfo,writeDictToFileText
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render
import copy
import nltk
from pathlib import Path
from nltk.data import find
from bllipparser import RerankingParser
import nltk
from pyparsing import OneOrMore, nestedExpr
from nltk.tokenize import word_tokenize,sent_tokenize
from pycorenlp import StanfordCoreNLP
from sklearn.feature_extraction.text import TfidfVectorizer




fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fopInputASTTreeSitter=fopRoot+'step3_treesitter_tokenize/'
fopInputSortBySimilarityScore=fopInputAfterTranslation+'sortBySimilarityScore/'

lstFpAST=[]




























