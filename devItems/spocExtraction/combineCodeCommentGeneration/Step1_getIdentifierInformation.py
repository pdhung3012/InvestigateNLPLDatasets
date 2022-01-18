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


def getLstFunctionDecl(jsonObject,lstFunctionDecl):
    # print(jsonObject)
    if str(jsonObject['type'])=='function_definition':
        # print('go he')
        lstFunctionDecl.append(jsonObject)
    if 'children' in jsonObject.keys():
        lstChildren=jsonObject['children']
        for i in range(0,len(lstChildren)):
            getLstFunctionDecl(lstChildren[i],lstFunctionDecl)

def getTerminalValue(startPointLine,startPointOffset,endPointLine,endPointOffset,arrCodes):
    lstStr=[]
    if startPointLine==endPointLine:
        return arrCodes[startPointLine][startPointOffset:endPointOffset]
    for i in range(startPointLine,endPointLine+1):

        if i==startPointLine:
            strAdd=arrCodes[i][startPointOffset:]
            lstStr.append(strAdd)
        elif i==endPointLine:
            strAdd = arrCodes[i][:endPointOffset]
            lstStr.append(strAdd)
        else:
            strAdd = arrCodes[i]
            lstStr.append(strAdd)
    strReturn='\n'.join(lstStr)
    return strReturn


def getIdentifier(jsonObject,arrCodes,dictIdentifiers):
    if str(jsonObject['type'])=='identifier':
        # print('go he')
        strIdenName=getTerminalValue(int(jsonObject['startLine']),int(jsonObject['startOffset']),int(jsonObject['endLine']),int(jsonObject['endOffset']),arrCodes)
        jsonObject['identifierValue']=strIdenName
        startLine=int(jsonObject['startLine'])
        if not startLine in dictIdentifiers.keys():
            dictIdentifiers[startLine]=[jsonObject]
        else:
            dictIdentifiers[startLine].append(jsonObject)
    if 'children' in jsonObject.keys():
        lstChildren=jsonObject['children']
        for i in range(0,len(lstChildren)):
            getIdentifier(lstChildren[i],arrCodes,dictIdentifiers)


fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fopInputASTTreeSitter=fopRoot+'step3_treesitter_tokenize/'
fopInputRealCPPFile=fopRoot+'step2_tokenize/'
fopInputSortBySimilarityScore=fopInputAfterTranslation+'sortBySimilarityScore/'

fpCacheTreeSitter=fopInputSortBySimilarityScore+'cache_step3_treesitter.txt'
fpIdentifierLog=fopInputSortBySimilarityScore+'identifier_log.txt'
fpLocations=fopInputSortBySimilarityScore+'location.txt'

f1=open(fpLocations,'r')
arrLocs=f1.read().strip().split('\n')
f1.close()

f1=open(fpIdentifierLog,'w')
f1.write('')
f1.close()

lstAllIdens=[]

prevProgramNameAndTrain=''
strFileAndFolder='AAAA'
dictIdentifiers={}
for i in range(0,len(arrLocs)):
    try:
        arrTabItem=arrLocs[i].split('\t')
        strTrainTestName = arrTabItem[1]
        strProgramName = arrTabItem[0]
        strFileAndFolder=strProgramName+'\t'+strTrainTestName
        lineOfPseudocode=int(arrTabItem[2])+32
        fpItemCodeAST=fopInputASTTreeSitter+strTrainTestName+'/'+strProgramName+'_code_ast.txt'
        fpItemCodeFile = fopInputRealCPPFile + strTrainTestName + '/' + strProgramName + '_code.cpp'



        if prevProgramNameAndTrain!=strFileAndFolder:
            dictIdentifiers = {}
            f1 = open(fpItemCodeFile, 'r')
            arrCodeFile = f1.read().strip().split('\n')
            f1.close()
            f1 = open(fpItemCodeAST, 'r')
            strAST = f1.read().strip().split('\n')[1]
            jsonItem = ast.literal_eval(strAST)

            getIdentifier(jsonItem,arrCodeFile,dictIdentifiers)

        lstItemIdens = []
        if lineOfPseudocode in dictIdentifiers.keys():
            for item in dictIdentifiers[lineOfPseudocode]:
                lstItemIdens.append(item['identifierValue'])

        lstAllIdens.append('{}\t{}\t{}'.format(strFileAndFolder,lineOfPseudocode,str(lstItemIdens)))

        if (i+1)%100==0 or i==len(arrLocs)-1:
            if len(lstAllIdens)>0:
                f1=open(fpIdentifierLog,'a')
                f1.write('\n'.join(map(str,lstAllIdens))+'\n')
                f1.close()
                lstAllIdens=[]
                print('end {} {}'.format(i,strFileAndFolder))
    except:
        traceback.print_exc()
    prevProgramNameAndTrain=strTrainTestName































