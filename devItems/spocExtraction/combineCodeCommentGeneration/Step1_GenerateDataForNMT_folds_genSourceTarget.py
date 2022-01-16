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
dictFilterLocations={}
indexLoc=0
for loc in arrLocations:
    arrLocTabs=loc.split('\t')
    strLoc='{}\t{}'.format(arrLocTabs[0],arrLocTabs[1])
    if not strLoc in lstFilterLocations:
        lstFilterLocations.add(strLoc)
        dictFilterLocations[strLoc]=indexLoc
        indexLoc=indexLoc+1

fpFilterLocation=fopInputStep2Folds+'nameOfCodes.txt'
fpFoldDetails=fopInputStep2Folds+'foldDetails.txt'
f1=open(fpFilterLocation,'r')
arrFilterLocations=f1.read().strip().split('\n')
f1.close()

f1=open(fpFoldDetails,'r')
arrFoldDetails=f1.read().strip().split('\n')
f1.close()

import ast
lstFoldDetails=[]
lenTotal=0
for i in range(0,len(arrFoldDetails)):
    res = ast.literal_eval(arrFoldDetails[i])
    lenTotal=lenTotal+len(res)
    lstFoldDetails.append(res)
print(lenTotal)

dictIndexFoldItem={}
lstFilterLocations=list(lstFilterLocations)
for i in range(1,11):
    fopFoldItem=fopInputStep2Folds+'fold-{}/'.format(i)
    createDirIfNotExist(fopFoldItem)
    fpTrainSource=fopFoldItem+'train.source.txt'
    fpTrainTarget = fopFoldItem + 'train.target.txt'
    fpTrainLocation = fopFoldItem + 'train.loc.txt'
    fpValidSource = fopFoldItem + 'valid.source.txt'
    fpValidTarget = fopFoldItem + 'valid.target.txt'
    fpValidLocation = fopFoldItem + 'valid.loc.txt'
    fpTestSource = fopFoldItem + 'test.source.txt'
    fpTestTarget = fopFoldItem + 'test.target.txt'
    fpTestLocation = fopFoldItem + 'test.loc.txt'
    lstFpForFolds=[]
    lstFpForFolds.append(fpTrainLocation)
    lstFpForFolds.append(fpTrainSource)
    lstFpForFolds.append(fpTrainTarget)
    lstFpForFolds.append(fpValidLocation)
    lstFpForFolds.append(fpValidSource)
    lstFpForFolds.append(fpValidTarget)
    lstFpForFolds.append(fpTestLocation)
    lstFpForFolds.append(fpTestSource)
    lstFpForFolds.append(fpTestTarget)
    dictValueToAdd = {}

    for q in lstFpForFolds:
        # f1=open(q,'w')
        # f1.write('')
        # f1.close()
        dictValueToAdd[q]=[]

    indexTest=i-1
    indexValid=i
    if i==10:
        indexValid=0

    dictTest={}
    dictValid={}
    for idx in lstFoldDetails[indexValid]:
        dictValid[arrFilterLocations[idx]]=idx
    for idx in lstFoldDetails[indexTest]:
        dictTest[arrFilterLocations[idx]]=idx

    print('begin fold {}'.format(i))

    for j in range(0,len(arrLocations)):
        arrTabsLoc=arrLocations[j].split('\t')
        strJLoc='{}\t{}'.format(arrTabsLoc[0],arrTabsLoc[1])
        # print(len(lstFilterLocations))
        indexLoc=dictFilterLocations[strJLoc]
        if strJLoc in dictValid.keys():
            dictValueToAdd[fpValidLocation].append(str(indexLoc)+'\t'+arrLocations[j])
            dictValueToAdd[fpValidSource].append(arrSources[j])
            dictValueToAdd[fpValidTarget].append(arrTargets[j])

        #     f1=open(fpValidSource,'a')
        #     f1.write(arrSources[j]+'\n')
        #     f1.close()
        #     f1 = open(fpValidTarget, 'a')
        #     f1.write(arrTargets[j] + '\n')
        #     f1.close()
        #     f1 = open(fpValidLocation, 'a')
        #     f1.write(str(indexLoc)+'\t'+arrLocations[j] + '\n')
        #     f1.close()
        elif strJLoc in dictTest.keys():
            dictValueToAdd[fpTestLocation].append(str(indexLoc)+'\t'+arrLocations[j])
            dictValueToAdd[fpTestSource].append(arrSources[j])
            dictValueToAdd[fpTestTarget].append(arrTargets[j])
        #     f1=open(fpTestSource,'a')
        #     f1.write(arrSources[j]+'\n')
        #     f1.close()
        #     f1 = open(fpTestTarget, 'a')
        #     f1.write(arrTargets[j] + '\n')
        #     f1.close()
        #     f1 = open(fpTestLocation, 'a')
        #     f1.write(str(indexLoc)+'\t'+arrLocations[j] + '\n')
        #     f1.close()
        else:
            dictValueToAdd[fpTrainLocation].append(str(indexLoc) + '\t' + arrLocations[j])
            dictValueToAdd[fpTrainSource].append(arrSources[j])
            dictValueToAdd[fpTrainTarget].append(arrTargets[j])
        #     f1 = open(fpTrainSource, 'a')
        #     f1.write(arrSources[j] + '\n')
        #     f1.close()
        #     f1 = open(fpTrainTarget, 'a')
        #     f1.write(arrTargets[j] + '\n')
        #     f1.close()
        #     f1 = open(fpTrainLocation, 'a')
        #     f1.write(str(indexLoc)+'\t'+arrLocations[j] + '\n')
        #     f1.close()
    for key1 in dictValueToAdd.keys():
        val1=dictValueToAdd[key1]
        f1=open(key1,'w')
        f1.write('\n'.join(val1))
        f1.close()
    print('end fold {}'.format(i))














