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

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputStep2Pseudocode=fopRoot+'step2_pseudo_tokenize/'
fopInputStep2ReplaceDict=fopRoot+'step2_code_replaceDict/'
fopInputStep2BeforeTranslation=fopRoot+'step2_beforeTranslation/step1/'
fopInputStep2Folds=fopRoot+'step2_beforeTranslation/folds/'
fopFold4=fopInputStep2Folds+'fold-4/'
fpTestSource=fopFold4+'test.source.txt'
fpTestP2Source=fopFold4+'test.source_p2.txt'

f1=open(fpTestSource,'r')
arrSouces=f1.read().strip().split('\n')
f1.close()
f1=open(fpTestP2Source,'w')
f1.write('\n'.join(arrSouces[17020:]))
f1.close()














