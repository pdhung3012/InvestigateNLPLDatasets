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

def jaccardSimilarityList(list1,list2):
    # list1=sourceSentence.lower().split()
    # list2=targetSentence.lower().split()
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union


fopStanfordCoreNLP='/home/hungphd/git/dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputStep3V2=fopRoot+'step3_v2/'
createDirIfNotExist(fopInputStep3V2)



lstFpStep3V2=sorted(glob.glob(fopInputStep3V2+'*.txt'))
dictInputContent={}
for i in range(0,len(lstFpStep3V2)):
    fpItemStep3=lstFpStep3V2[i]
    fnItem=os.path.basename(fpItemStep3)
    f1=open(fpItemStep3,'r')
    arrContent=f1.read().strip().split('\n')
    f1.close()
    dictInputContent[fnItem]=arrContent

fnSource='source.txt'
fnTarget='target.txt'

lstInconsistent=[]
dictSimScore={}
f1=open(fopInputStep3V2+'inconsistentSource.txt','w')
f1.write('')
f1.close()

arrListSource=[]
arrSource=dictInputContent[fnSource]
arrTarget = dictInputContent[fnTarget]
for i in range(0,len(dictInputContent[fnSource])):
    list1=arrSource[i].lower().split()
    arrListSource.append(list1)

for i in range(0,len(dictInputContent[fnSource])):
    bestIncIndex=-1
    maxScore=-1


    for j in range(0,len(arrSource)):
        if i == j:
            continue
        strIJ='{}_{}'.format(i,j)
        strReverseIJ = '{}_{}'.format(j, i)
        simItem = jaccardSimilarityList(arrListSource[i], arrListSource[j])
        # if strIJ not in dictSimScore.keys():
        #     simItem=jaccardSimilarityList(arrListSource[i],arrListSource[j])
        #     dictSimScore[strReverseIJ]=simItem
        #     # dictSimScore[strIJ]=simItem
        # else:
        #     simItem=dictSimScore[strIJ]

        if simItem>maxScore and arrSource[i]!=arrSource[j] and arrTarget[i]!=arrTarget[j]:
            bestIncIndex=j
            maxScore=simItem

    strLine='{}{}{}{}{}{}{}'.format(bestIncIndex,strTabChar,maxScore,strTabChar,arrSource[bestIncIndex],strTabChar,arrTarget[bestIncIndex])
    lstInconsistent.append(strLine)

    if len(lstInconsistent)%1000==0 or i==len(arrSource)-1:
        print('begin {}'.format(i+1))
        f1=open(fopInputStep3V2+'inconsistentSource.txt','a')
        f1.write('\n'.join(lstInconsistent)+'\n')
        f1.close()
        lstInconsistent=[]
































