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

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fopFilterSortedBySimScore=fopInputAfterTranslation+'sortBySimilarityScore/filterByPOS/'

fopSplit=fopInputAfterTranslation+'sortBySimilarityScore/trainValidTest/'
fpTrainValidTestIndex=fopSplit+'trainValidTest.index.txt'
fopTrain=fopSplit+'train/'
fopValid=fopSplit+'valid/'
fopTest=fopSplit+'test/'
createDirIfNotExist(fopTrain)
createDirIfNotExist(fopValid)
createDirIfNotExist(fopTest)

lstFpInput=glob.glob(fopFilterSortedBySimScore+'*.txt')

dictFolderContent={}
dictNewContent={}
for i in range(0,len(lstFpInput)):
    fpItem=lstFpInput[i]
    nameItem=os.path.basename(fpItem)
    f1=open(fpItem,'r')
    arrContent=f1.read().strip().split('\n')
    f1.close()
    dictFolderContent[nameItem]=arrContent
    dictNewContent[nameItem]=[[],[],[]]


fnLocation='location.txt'
dictTrainTestPTestW={}
prevFolder=''
for i in range(0,len(dictFolderContent[fnLocation])):
    arrContentLoc=dictFolderContent[fnLocation]
    arrTabs=arrContentLoc[i].split('\t')
    if arrTabs[1]!=prevFolder:
        if arrTabs[1] not in dictTrainTestPTestW.keys():
            dictTrainTestPTestW[arrTabs[1]]=[i,-1]
            if prevFolder!='':
                dictTrainTestPTestW[prevFolder][1]=i-1
    elif i==len(arrContentLoc)-1:
        dictTrainTestPTestW[arrTabs[1]][1]=i
    prevFolder=arrTabs[1]
print(dictTrainTestPTestW)

# {'train': [0, 28340], 'testW': [28341, 31506], 'testP': [31507, 37729]}
validRange=[31507,34808]
testRange=[28341,31506]
lstTVTStr=['train','valid','test']
lstIndex=[]
for i in range(0,len(dictFolderContent[fnLocation])):
    arrContentLoc=dictFolderContent[fnLocation]
    indexTrainValidTest=0
    if i in range(validRange[0],validRange[1]+1):
        indexTrainValidTest=1
    elif i in range(testRange[0],testRange[1]+1):
        indexTrainValidTest=2
    for key in dictFolderContent.keys():
        val=dictFolderContent[key][i]
        dictNewContent[key][indexTrainValidTest].append(val)
    lstIndex.append('{}\t{}'.format(lstTVTStr[indexTrainValidTest],arrContentLoc[i]))

f1=open(fpTrainValidTestIndex,'w')
f1.write('\n'.join(lstIndex))
f1.close()

print(dictTrainTestPTestW)
for key in dictNewContent.keys():
    fpItemTrain=fopTrain+key
    lstVal=dictNewContent[key][0]
    f1=open(fpItemTrain,'w')
    f1.write('\n'.join(lstVal))
    f1.close()
    fpItemValid=fopValid+key
    lstVal=dictNewContent[key][1]
    f1=open(fpItemValid,'w')
    f1.write('\n'.join(lstVal))
    f1.close()
    fpItemTest=fopTest+key
    lstVal=dictNewContent[key][2]
    f1=open(fpItemTest,'w')
    f1.write('\n'.join(lstVal))
    f1.close()








