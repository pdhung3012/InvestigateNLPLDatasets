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
strEndLine=' ENDLINE'
strEndFileChar='_EF_'
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
strSplitCharacterForNodeEdge = '_ABAZ_'

import numpy as np



fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep5EmbeddingModels=fopRoot+'embeddingModels/'
fopStep3V2=fopRoot+'step3_v2/'
fpLogError=fopStep3V2+'log_error.txt'
fopInputStep6Incons=fopRoot+'step6_Incons/lstm/'
fopTrainTestInfo=fopRoot+''
lstEmbeddingInput=['incons-rnn-lstm']

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

createDirIfNotExist(fopInputStep6Incons)
lstResult=['EmbedModel\tRoot\tprecision\trecall\tfscore\tacc\ttrain time\tpredict time']
fpOverallResult=fopInputStep6Incons+'result_overall.txt'
f1=open(fpOverallResult,'w')
f1.write('\n'.join(lstResult)+'\n')
f1.close()


fpTextInfo=fopInputStep6Incons+'text.txt'
fpEmbLabelInfo=fopInputStep6Incons+'emb.txt'
f1=open(fpEmbLabelInfo,'r')
arrEmb=f1.read().strip().split('\n')
f1.close()
f1=open(fpTextInfo,'r')
arrText=f1.read().strip().split('\n')
f1.close()

lstPRTextTrain=['label,text']
lstPRTextValid = ['label,text']
lstPRTextTest = ['label,text']

for i in range(0, len(arrEmb)):
    arrItemTabTrainTest = arrEmb[i].split('\t')
    # print('{} {}'.format(len(arrProgramRootEmb),i))
    labelItem = arrItemTabTrainTest[1]
    strTextPR=arrText[i]
    # print(arrText[i].re)
    if strTextPR.strip()=='':
        print('go here')
        continue

    if arrItemTabTrainTest[0]=='train':
        lstPRTextTrain.append('{},{}'.format(labelItem,strTextPR))
    elif arrItemTabTrainTest[0]=='valid':
        lstPRTextValid.append('{},{}'.format(labelItem,strTextPR))
    else:
        lstPRTextTest.append('{},{}'.format(labelItem,strTextPR))

# lstPRTextTrain=lstPRTextTrain[0:len(lstPRTextTrain)-2]
# lstPRTextValid=lstPRTextValid[0:1000]
# lstPRTextTest=lstPRTextTest[0:1000]

fopContextPR=fopInputStep6Incons
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






