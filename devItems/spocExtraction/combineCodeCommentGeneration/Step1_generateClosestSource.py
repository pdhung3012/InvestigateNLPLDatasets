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
fpSortedLocation=fopSortedBySimScore+'location.txt'
fpSortedSource=fopSortedBySimScore+'source.txt'
fpSortedTarget=fopSortedBySimScore+'target.txt'
fpSortedPred=fopSortedBySimScore+'pred.txt'
fpSortedIdentifiers=fopSortedBySimScore+'identifier_log.txt'
fpSortedDetails=fopSortedBySimScore+'sortedDetails.txt'
fopSortedPOSStanford=fopSortedBySimScore+'pos_stanford/'
fopSortedPOSNLTK=fopSortedBySimScore+'pos_nltk/'
createDirIfNotExist(fopSortedPOSStanford)
createDirIfNotExist(fopSortedPOSNLTK)
fopFilterSortedBySimScore=fopSortedBySimScore+'filterByPOS/'
fopStep3Filer=fopRoot+'step3_filter_pos/'
createDirIfNotExist(fopFilterSortedBySimScore)
fpFilterSortedLocation=fopFilterSortedBySimScore+'location.txt'
fpFilterSortedSource=fopFilterSortedBySimScore+'source.txt'
fpFilterSortedTarget=fopFilterSortedBySimScore+'target.txt'
fpFilterSortedPred=fopFilterSortedBySimScore+'pred.txt'
fpFilterSortedSortDetails=fopFilterSortedBySimScore+'sortedDetails.txt'
fpFilterSortedIdentifier=fopFilterSortedBySimScore+'identifier_log.txt'
fpFilterSortedPOSNLTK=fopFilterSortedBySimScore+'pos_nltk.txt'
fpFilterSortedPOSStanford=fopFilterSortedBySimScore+'pos_stanford.txt'



lstFpTextPOSNLTK=sorted(glob.glob(fopSortedPOSNLTK+'*.text.txt'))
lstFpTextPOSStanford=sorted(glob.glob(fopSortedPOSStanford+'*.text.txt'))

dictNLTKAlreadyAppeared={}
for i in range(0,len(lstFpTextPOSNLTK)):
    fpItemText=lstFpTextPOSNLTK[i]
    fpItemPOS=fpItemText.replace('.text.txt','.pos.txt')
    nameItem=os.path.basename(fpItemText).replace('.text.txt','')

    f1=open(fpItemText,'r')
    arrItemText=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpItemPOS, 'r')
    arrItemPOS = f1.read().strip().split('\n')
    f1.close()

    for j in range(0,len(arrItemText)):
        linePOS=arrItemPOS[j]
        lineText=arrItemText[j]
        if linePOS!='{}':
            dictNLTKAlreadyAppeared[lineText]=linePOS

dictStanfordAlreadyAppeared={}
for i in range(0,len(lstFpTextPOSStanford)):
    fpItemText=lstFpTextPOSStanford[i]
    fpItemPOS=fpItemText.replace('.text.txt','.pos.txt')
    nameItem=os.path.basename(fpItemText).replace('.text.txt','')

    f1=open(fpItemText,'r')
    arrItemText=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpItemPOS, 'r')
    arrItemPOS = f1.read().strip().split('\n')
    f1.close()

    for j in range(0,len(arrItemText)):
        linePOS=arrItemPOS[j]
        lineText=arrItemText[j]
        if linePOS!='{}':
            dictStanfordAlreadyAppeared[lineText]=linePOS

f1=open(fpSortedSource,'r')
arrSources=f1.read().strip().split('\n')
f1.close()
f1=open(fpSortedLocation,'r')
arrLocs=f1.read().strip().split('\n')
f1.close()
f1=open(fpSortedTarget,'r')
arrTargets=f1.read().strip().split('\n')
f1.close()
f1=open(fpSortedPred,'r')
arrPreds=f1.read().strip().split('\n')
f1.close()
f1=open(fpSortedIdentifiers,'r')
arrIdens=f1.read().strip().split('\n')
f1.close()
f1=open(fpSortedDetails,'r')
arrSortDetails=f1.read().strip().split('\n')
f1.close()

lstNewLocs=[]
lstNewSources=[]
lstNewTargets=[]
lstNewPreds=[]
lstNewIdens=[]
lstNewPOS_NLTKs=[]
lstNewPOS_Stanfords=[]
lstNewSortDetails=[]

for i in range(0,len(arrSources)):
    itemSource=arrSources[i]
    itemTarget = arrTargets[i]
    itemLocation = arrLocs[i]
    itemPred = arrPreds[i]
    itemIden=arrIdens[i]
    itemDetails=arrSortDetails[i]
    if itemSource in dictNLTKAlreadyAppeared.keys() and itemSource in dictStanfordAlreadyAppeared.keys():
        lstNewLocs.append(itemLocation)
        lstNewSources.append(itemSource)
        lstNewTargets.append(itemTarget)
        lstNewPreds.append(itemPred)
        lstNewIdens.append(itemIden)
        lstNewPOS_NLTKs.append(dictNLTKAlreadyAppeared[itemSource])
        lstNewPOS_Stanfords.append(dictStanfordAlreadyAppeared[itemSource])
        lstNewSortDetails.append(itemDetails)

f1=open(fpFilterSortedSource,'w')
f1.write('\n'.join(lstNewSources))
f1.close()
f1=open(fpFilterSortedLocation,'w')
f1.write('\n'.join(lstNewLocs))
f1.close()
f1=open(fpFilterSortedTarget,'w')
f1.write('\n'.join(lstNewTargets))
f1.close()
f1=open(fpFilterSortedPred,'w')
f1.write('\n'.join(lstNewPreds))
f1.close()
f1=open(fpFilterSortedIdentifier,'w')
f1.write('\n'.join(lstNewIdens))
f1.close()
f1=open(fpFilterSortedPOSNLTK,'w')
f1.write('\n'.join(lstNewPOS_NLTKs))
f1.close()
f1=open(fpFilterSortedPOSStanford,'w')
f1.write('\n'.join(lstNewPOS_Stanfords))
f1.close()
f1=open(fpFilterSortedSortDetails,'w')
f1.write('\n'.join(lstNewSortDetails))
f1.close()






























