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


def jaccardSimilarity(sourceSentence,targetSentence):
    list1=sourceSentence.lower().split()
    list2=targetSentence.lower().split()
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union


import re


def camel_case_split(str):
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)

def percentageOfOverlap(sourceSentence,targetSentence):
    listSource=sourceSentence.split()
    listTarget=targetSentence.split()
    setOfWordInTarget=[]
    for item in listTarget:
        # print(item)
        setOfWordInTarget.append(item.lower())
        if not item.startswith('SpecialLiteral'):
            arrSubItem = camel_case_split(item)
            # print(arrSubItem)
            for subword in arrSubItem:
                setOfWordInTarget.append(subword.lower())
    countAppear=0
    countDisappear=0
    lstOut=[]
    for item in listSource:
        if item in setOfWordInTarget:
            countAppear=countAppear+1

            lstOut.append(item+'#1')
        else:
            countDisappear=countDisappear+1
            lstOut.append(item + '#0')
    percentage=countAppear*1.0/(countAppear+countDisappear)
    percentageLevel=int(percentage*100//10+1)
    if percentage==100:
        percentageLevel=1
    return percentageLevel,percentage,countAppear,countDisappear,lstOut

def getIdentifierTag(source,lstIdentifiersInCode):
    arrSource=source.split()
    lstOutput=[]
    countIdentifier=0
    for item in arrSource:
        if item in lstIdentifiersInCode:
            lstOutput.append(item+'#1')
            countIdentifier=countIdentifier+1
        else:
            lstOutput.append(item+'#0')

    return lstOutput,countIdentifier

fopStanfordCoreNLP='/home/hungphd/git/dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fopSortedBySimScore=fopInputAfterTranslation+'sortBySimilarityScore/'
fopFilterSortedBySimScore=fopSortedBySimScore+'filterByPOS/'
fopStep3Filer=fopRoot+'step3_filter_pos/'
createDirIfNotExist(fopFilterSortedBySimScore)
fpFilterSortedLocation=fopFilterSortedBySimScore+'location.txt'
fpFilterSortedSource=fopFilterSortedBySimScore+'source.txt'
fpFilterSortedTarget=fopFilterSortedBySimScore+'target.txt'
fpFilterSortedPred=fopFilterSortedBySimScore+'pred.txt'
fpFilterSortedIdentifierLog=fopFilterSortedBySimScore+'identifier_log.txt'
fpFilterSortedLabelOverlapDetection=fopFilterSortedBySimScore+'label.p1.overlap.txt'
fpFilterSortedLabelIdentifierDetection=fopFilterSortedBySimScore+'label.p2.identifierDetection.txt'
fpFilterSortedLabelJaccard=fopFilterSortedBySimScore+'label.p3.jaccardSimilarity.txt'




f1=open(fpFilterSortedSource,'r')
arrSources=f1.read().strip().split('\n')
f1.close()
f1=open(fpFilterSortedLocation,'r')
arrLocs=f1.read().strip().split('\n')
f1.close()
f1=open(fpFilterSortedTarget,'r')
arrTargets=f1.read().strip().split('\n')
f1.close()
f1=open(fpFilterSortedPred,'r')
arrPreds=f1.read().strip().split('\n')
f1.close()
f1=open(fpFilterSortedIdentifierLog,'r')
arrIdenLogs=f1.read().strip().split('\n')
f1.close()

lstNewLocs=[]
lstNewSources=[]
lstNewTargets=[]
lstNewPreds=[]
lstNewIdens=[]
lstNewPOS_NLTKs=[]
lstNewPOS_Stanfords=[]


lstLbl1=[]
lstLbl2=[]
lstLbl3=[]
for i in range(0,len(arrSources)):
    itemSource=arrSources[i]
    itemPred=arrPreds[i]
    itemTarget=arrTargets[i]
    itemIdentiferInCode=arrIdenLogs[i]
    lstIdenLogs=ast.literal_eval(itemIdentiferInCode.split('\t')[3])


    lstOutputIdens, countIdentifier=getIdentifierTag(itemSource,lstIdenLogs)
    strLbl1='{}\t{}'.format(' '.join(lstOutputIdens),countIdentifier)
    strLbl3=jaccardSimilarity(itemSource, itemTarget)
    percentageLevel, percentage, countAppear, countDisappear, lstWordOverlap=percentageOfOverlap(itemSource,itemTarget)
    strLbl2='{}\t{}\t{}\t{}\t{}'.format(percentageLevel,percentage,countAppear,countAppear+countDisappear,' '.join(lstWordOverlap))
    lstLbl1.append(strLbl1)
    lstLbl2.append(strLbl2)
    lstLbl3.append(str(strLbl3))

f1=open(fpFilterSortedLabelOverlapDetection,'w')
f1.write('\n'.join(lstLbl2))
f1.close()
f1=open(fpFilterSortedLabelIdentifierDetection,'w')
f1.write('\n'.join(lstLbl1))
f1.close()
f1=open(fpFilterSortedLabelJaccard,'w')
f1.write('\n'.join(lstLbl3))
f1.close()






























