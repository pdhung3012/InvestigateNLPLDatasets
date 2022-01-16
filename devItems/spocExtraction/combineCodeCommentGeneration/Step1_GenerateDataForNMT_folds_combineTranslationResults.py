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
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fpTestLocExpected=fopInputStep2BeforeTranslation+'location.txt'
fpTestPredBeforeSort=fopInputAfterTranslation+'test.pred.unsorted.txt'
fpTestLocBeforeSort=fopInputAfterTranslation+'test.loc.unsorted.txt'
fpTestPredAfterSort=fopInputAfterTranslation+'pred.txt'
fpTestLocAfterSort=fopInputAfterTranslation+'pred.loc.txt'
createDirIfNotExist(fopInputAfterTranslation)
f1=open(fpTestLocBeforeSort,'w')
f1.write('')
f1.close()
f1=open(fpTestPredBeforeSort,'w')
f1.write('')
f1.close()

dictLocBefore={}

for i in range(1,11):
    nameFold='fold-{}'.format(i)
    fpFoldTestLocation=fopInputStep2Folds+nameFold+'/test.loc.txt'
    fpFoldTestPred = fopInputStep2Folds + nameFold + '/pred.txt'

    f1=open(fpFoldTestLocation,'r')
    arrFoldLocs=f1.read().strip().split('\n')
    f1.close()
    f1=open(fpFoldTestPred,'r')
    arrFoldPreds=f1.read().strip().split('\n')
    f1.close()

    for j in range(0,len(arrFoldLocs)):
        arrTabLoc=arrFoldLocs[j].strip().split('\t')
        strKey='{}\t{}\t{}'.format(arrTabLoc[1],arrTabLoc[2],arrTabLoc[3])
        dictLocBefore[strKey]=[arrTabLoc[0],arrFoldPreds[j].strip()]


    f1 = open(fpTestLocBeforeSort, 'a')
    f1.write('\n'.join(arrFoldLocs)+'\n')
    f1.close()
    f1 = open(fpTestPredBeforeSort, 'w')
    f1.write('\n'.join(arrFoldPreds)+'\n')
    f1.close()

f1=open(fpTestLocExpected,'r')
arrTestLocExpecteds=f1.read().strip().split('\n')
f1.close()

lstPredLocs=[]
lstPredTexts=[]
for i in range(0,len(arrTestLocExpecteds)):
    val=dictLocBefore[arrTestLocExpecteds[i]]
    lstPredLocs.append(val[0]+'\t'+arrTestLocExpecteds[i])
    lstPredTexts.append(val[1])

f1=open(fpTestLocAfterSort,'w')
f1.write('\n'.join(lstPredLocs))
f1.close()
f1=open(fpTestPredAfterSort,'w')
f1.write('\n'.join(lstPredTexts))
f1.close()






















