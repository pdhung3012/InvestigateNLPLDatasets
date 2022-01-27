import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser
from Util_LibForGraphExtractionFromRawCode import getJsonDict,getTerminalValue
import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render
import copy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer,TfidfTransformer
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support as score
import time
from sklearn.metrics import classification_report
from sklearn.metrics import cohen_kappa_score
from langdetect import detect
from sklearn.metrics import confusion_matrix
import langid
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support as score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, \
    recall_score, confusion_matrix, classification_report, \
    accuracy_score, f1_score



strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar='_EL_'
strEndFileChar='_EF_'
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
strSplitCharacterForNodeEdge = '_ABAZ_'

import numpy as np



fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep5EmbeddingModels=fopRoot+'embeddingModels/'
fopStep3V2=fopRoot+'step3_v2/'
fpLogError=fopStep3V2+'log_error.txt'
fopStep6ResultBaseline=fopRoot+'step6_resultBaseline/'
fopTrainTestInfo=fopRoot+''
lstEmbeddingInput=['rnn-lstm']

lstFpInput=glob.glob(fopStep3V2+'*.txt')

f1=open(fpLogError,'r')
arrErrorLogs=f1.read().strip().split('\n')
f1.close()
setErrorLogs=set(arrErrorLogs)

dictFolderContent={}
# dictNewContent={}
for i in range(0,len(lstFpInput)):
    fpItem=lstFpInput[i]
    nameItem=os.path.basename(fpItem)
    f1=open(fpItem,'r')
    arrContent=f1.read().strip().split('\n')
    f1.close()
    dictFolderContent[nameItem]=arrContent
    # dictNewContent[nameItem]=[[],[],[]]
fnLocation='location.txt'
fnSource='source.txt'
fnLabelOverlap='label.p1.overlap.txt'
fnTrainIndex='trainValidTest.index.txt'

createDirIfNotExist(fopStep6ResultBaseline)
lstResult=['EmbedModel\tRoot\tprecision\trecall\tfscore\tacc\ttrain time\tpredict time']
fpOverallResult=fopStep6ResultBaseline+'result_overall.txt'
f1=open(fpOverallResult,'w')
f1.write('\n'.join(lstResult)+'\n')
f1.close()
for embedModel in lstEmbeddingInput:

    fpEmbedTextProgramRoot=fopStep5EmbeddingModels+'d2v/ProgramRoot.textForEmb.txt'
    fpEmbedTextNLRoot = fopStep5EmbeddingModels  + 'd2v/NLRoot.textForEmb.txt'

    f1=open(fpEmbedTextProgramRoot,'r')
    arrProgramRootText=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpEmbedTextNLRoot, 'r')
    arrNLRootText = f1.read().strip().split('\n')
    f1.close()

    lstPRTextTrain=['label,text']
    lstPRTextValid = ['label,text']
    lstPRTextTest = ['label,text']
    lstNLRTextTrain=['label,text']
    lstNLRTextValid = ['label,text']
    lstNLRTextTest = ['label,text']

    for i in range(0,len(dictFolderContent[fnTrainIndex])):
        arrItemTabTrainTest=dictFolderContent[fnTrainIndex][i].split('\t')
        # print('{} {}'.format(len(arrProgramRootEmb),i))
        strLoc=dictFolderContent[fnLocation][i]
        if strLoc in setErrorLogs:
            continue
        labelItem=dictFolderContent[fnLabelOverlap][i].split('\t')[0]
        strTextPR=arrProgramRootText[i].replace(',',' COMMA ')
        strTextNLR = arrNLRootText[i].replace(',', ' COMMA ')
        if arrItemTabTrainTest[0]=='train':
            lstPRTextTrain.append('{},{}'.format(labelItem,strTextPR))
            lstNLRTextTrain.append('{},{}'.format(labelItem, strTextNLR))
        elif arrItemTabTrainTest[0]=='valid':
            lstPRTextValid.append('{},{}'.format(labelItem,strTextPR))
            lstNLRTextValid.append('{},{}'.format(labelItem, strTextNLR))
        else:
            lstPRTextTest.append('{},{}'.format(labelItem,strTextPR))
            lstNLRTextTest.append('{},{}'.format(labelItem, strTextNLR))

    fopContextPR=fopStep6ResultBaseline+embedModel+'/ProgramRoot/'
    createDirIfNotExist(fopContextPR)
    f1=open(fopContextPR+'train.label.p1.txt','w')
    f1.write('\n'.join(lstPRTextTrain))
    f1.close()
    f1 = open(fopContextPR + 'valid.label.p1.txt', 'w')
    f1.write('\n'.join(lstPRTextValid))
    f1.close()
    f1 = open(fopContextPR + 'test.label.p1.txt', 'w')
    f1.write('\n'.join(lstPRTextTest))
    f1.close()

    fopContextNLR = fopStep6ResultBaseline + embedModel + '/NLRoot/'
    createDirIfNotExist(fopContextNLR)
    f1=open(fopContextNLR+'train.label.p1.txt','w')
    f1.write('\n'.join(lstNLRTextTrain))
    f1.close()
    f1 = open(fopContextNLR + 'valid.label.p1.txt', 'w')
    f1.write('\n'.join(lstNLRTextValid))
    f1.close()
    f1 = open(fopContextNLR + 'test.label.p1.txt', 'w')
    f1.write('\n'.join(lstNLRTextTest))
    f1.close()





