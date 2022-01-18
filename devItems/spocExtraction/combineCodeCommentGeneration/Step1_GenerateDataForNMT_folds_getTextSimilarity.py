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

def jaccard(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union

def checkLineOfCodeInsideFunctionDecl(lineInPseudocode,lstRanges):
    lineInSourceCode=lineInPseudocode+32
    result=False
    for item in lstRanges:
        if item[0]<lineInSourceCode and lineInSourceCode<item[1]:
            # print('check true')
            result=True
            break
    # if not result:
    #     print('check false')
    return result



fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fopInputSortBySimilarityScore=fopInputAfterTranslation+'sortBySimilarityScore/'
fpSourceAfterTrans=fopInputAfterTranslation+'source.txt'
fpTargetAfterTrans=fopInputAfterTranslation+'target.txt'
fpLocationAfterTrans=fopInputAfterTranslation+'location.txt'
fpPredAfterTrans=fopInputAfterTranslation+'pred.txt'

createDirIfNotExist(fopInputSortBySimilarityScore)
fpSortedSourceAfterTrans=fopInputSortBySimilarityScore+'source.txt'
fpSortedTargetAfterTrans=fopInputSortBySimilarityScore+'target.txt'
fpSortedLocationAfterTrans=fopInputSortBySimilarityScore+'location.txt'
fpSortedPredAfterTrans=fopInputSortBySimilarityScore+'pred.txt'
fpSortedDetailsAfterTrans=fopInputSortBySimilarityScore+'sortedDetails.txt'
fpFuncDeclInfo=fopInputSortBySimilarityScore+'function_declarations.txt'

f1=open(fpFuncDeclInfo,'r')
arrFuncDecls=f1.read().strip().split('\n')
f1.close()
dictFuncDecls={}
for item in arrFuncDecls:
    arrTabs=item.split('\t')
    strKey=arrTabs[0]+'\t'+arrTabs[1]
    lstVal=ast.literal_eval(arrTabs[2])
    dictFuncDecls[strKey]=lstVal


f1=open(fpLocationAfterTrans,'r')
arrLocations=f1.read().strip().split('\n')
f1.close()
f1=open(fpSourceAfterTrans,'r')
arrSources=f1.read().strip().split('\n')
f1.close()
f1=open(fpTargetAfterTrans,'r')
arrTarget=f1.read().strip().split('\n')
f1.close()
f1=open(fpPredAfterTrans,'r')
arrPreds=f1.read().strip().split('\n')
f1.close()

lstSortedLines=[]
lenStatements=5
scoreDistance=0.5
for i in range(0,len(arrLocations)):
    if arrTarget[i]=='' or arrPreds[i]=='' or arrSources[i]=='':
        continue
    if len(arrSources[i].split())<lenStatements or len(arrTarget[i].split())<lenStatements:
        continue
    scoreSim=jaccard(arrTarget[i].lower().split(),arrPreds[i].lower().split())
    if(scoreSim>scoreDistance):
        continue
    arrTabLoc=arrLocations[i].split('\t')
    strKeyLocation='{}\t{}'.format(arrTabLoc[0],arrTabLoc[1])
    lineInPseudo=int(arrTabLoc[2])
    lstRanges=dictFuncDecls[strKeyLocation]
    resultInFD=checkLineOfCodeInsideFunctionDecl(lineInPseudo,lstRanges)
    if not resultInFD:
        continue
    print('element {} {}'.format(i + 1,scoreSim))
    lenSource=len(arrSources[i].split())
    lstItem=[scoreSim,lenSource,arrLocations[i],arrSources[i],arrTarget[i],arrPreds[i]]
    lstSortedLines.append(lstItem)

# lstSortedLines = sorted(lstSortedLines, key=operator.itemgetter(0))
lstSoredLocations=[]
lstSoredSources=[]
lstSoredTargets=[]
lstSoredPreds=[]
lstSoredToFile=[]

for i in range(0,len(lstSortedLines)):
    itemLine=lstSortedLines[i]
    lstSoredLocations.append(itemLine[2])
    lstSoredSources.append(itemLine[3])
    lstSoredTargets.append(itemLine[4])
    lstSoredPreds.append(itemLine[5])
    strLine='{} AABBAA {} AABBAA {} AABBAA {} AABBAA {} AABBAA {}'.format(itemLine[0],itemLine[1],itemLine[2],itemLine[3],itemLine[4],itemLine[5])
    lstSoredToFile.append(strLine)

f1=open(fpSortedDetailsAfterTrans,'w')
f1.write('\n'.join(lstSoredToFile))
f1.close()
f1=open(fpSortedLocationAfterTrans,'w')
f1.write('\n'.join(lstSoredLocations))
f1.close()
f1=open(fpSortedSourceAfterTrans,'w')
f1.write('\n'.join(lstSoredSources))
f1.close()
f1=open(fpSortedTargetAfterTrans,'w')
f1.write('\n'.join(lstSoredTargets))
f1.close()
f1=open(fpSortedPredAfterTrans,'w')
f1.write('\n'.join(lstSoredPreds))
f1.close()


























