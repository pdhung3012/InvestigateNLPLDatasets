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
createDirIfNotExist(fopInputStep2ReplaceDict)
createDirIfNotExist(fopInputStep2Folds)



fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiteralsReverse={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiteralsReverse[strContent]=arrTabs[0]

fpLocation=fopInputStep2BeforeTranslation+'location.txt'
fpSource=fopInputStep2BeforeTranslation+'source.txt'
fpTarget=fopInputStep2BeforeTranslation+'target.txt'

f1=open(fpLocation,'r')
arrLocations=f1.read().strip().split('\n')
f1.close()
f1=open(fpSource,'r')
arrSources=f1.read().strip().split('\n')
f1.close()
f1=open(fpTarget,'r')
arrTargets=f1.read().strip().split('\n')
f1.close()

lstFilterLocations=set()
for loc in arrLocations:
    arrLocTabs=loc.split('\t')
    strLoc='{}\t{}'.format(arrLocTabs[0],arrLocTabs[1])
    if not strLoc in lstFilterLocations:
        lstFilterLocations.add(strLoc)

from datetime import datetime
from uuid import uuid4
eventid = datetime.now().strftime('%Y%m%d%H%M%S')
fpFilterLocation=fopInputStep2Folds+'nameOfCodes.txt'
fpFilterLocationTime=fopInputStep2Folds+'nameOfCodes_{}.txt'.format(eventid)
fpFoldDetails=fopInputStep2Folds+'foldDetails.txt'
fpFoldDetailsTime=fopInputStep2Folds+'foldDetails_{}.txt'.format(eventid)

f1=open(fpFilterLocation,'w')
f1.write('\n'.join(lstFilterLocations))
f1.close()

f1=open(fpFilterLocationTime,'w')
f1.write('\n'.join(lstFilterLocations))
f1.close()


import random
lstFolds = list(range(0, len(lstFilterLocations)))
random.shuffle(lstFolds)
lstFolds = [lstFolds[i::10] for i in range(10)]


f1=open(fpFoldDetails,'w')
strContent='\n'.join(map(str,lstFolds))
f1.write(strContent)
f1.close()

f1=open(fpFoldDetailsTime,'w')
strContent='\n'.join(map(str,lstFolds))
f1.write(strContent)
f1.close()





