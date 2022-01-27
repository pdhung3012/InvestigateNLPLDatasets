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
def getVector(model,strInput):
    vectorItem = model.transform([strInput]).toarray()[0]
    strVector = ' '.join(map(str, vectorItem))
    return strVector

def runMLModelAndSaveSummary(X_train,y_train,X_test,y_test,fopItemSummary):

    fpLog=fopItemSummary+'log.txt'
    fpOutResultDetail=fopItemSummary+'resultDetails.txt'
    fpPredict=fopItemSummary+'predict.txt'
    fpTest = fopItemSummary + 'test.txt'
    sys.stdout=(open(fpLog,'w'))
    rf = RandomForestClassifier(n_estimators=150, max_depth=None, n_jobs=-1, random_state=42)
    start = time.time()
    rf_model = rf.fit(X_train, y_train)
    # filename4 = fop+arrConfigs[idx]+ '_mlmodel.bin'
    end = time.time()
    fit_time = (end - start)
    print('end train {}'.format(fit_time))
    start = time.time()
    y_pred = rf_model.predict(X_test)
    end = time.time()
    pred_time = (end - start)
    print('end testP {}'.format(pred_time))
    f1=open(fpPredict,'w')
    f1.write('\n'.join(y_pred))
    f1.close()
    f1 = open(fpTest, 'w')
    f1.write('\n'.join(y_test))
    f1.close()

    acc=accuracy_score(y_test,y_pred)
    f1 = open(fpOutResultDetail, 'w')
    precision= precision_score(y_test, y_pred,average='weighted')
    recall=recall_score(y_test,y_pred,average='weighted')
    fscore=f1_score(y_test,y_pred,average='weighted')
    f1.write('{}\n'.format(confusion_matrix(y_test, y_pred)))
    f1.write('{}\n'.format(classification_report(y_test, y_pred)))
    f1.write('Cohen Kappa{}\n\n\n'.format(cohen_kappa_score(y_test, y_pred, weights="quadratic")))
    f1.close()
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    return acc,precision,recall,fscore,fit_time,pred_time


fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep5EmbeddingModels=fopRoot+'embeddingModels/'
fopStep3V2=fopRoot+'step3_v2/'
fpLogError=fopStep3V2+'log_error.txt'
fopStep6ResultBaseline=fopRoot+'step6_resultBaseline/'
fopTrainTestInfo=fopRoot+''
lstEmbeddingInput=['tfidf','d2v','fasttext-cbow']

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

    fpEmbedVectorProgramRoot=fopStep5EmbeddingModels+embedModel+'/ProgramRoot.vectorForEmb.txt'
    fpEmbedVectorNLRoot = fopStep5EmbeddingModels + embedModel + '/NLRoot.vectorForEmb.txt'

    f1=open(fpEmbedVectorProgramRoot,'r')
    arrProgramRootEmb=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpEmbedVectorNLRoot, 'r')
    arrNLRootEmb = f1.read().strip().split('\n')
    f1.close()

    X_train_PR = []
    X_train_NLR = []
    y_train = []
    X_test_PR = []
    X_test_NLR = []
    y_test = []

    for i in range(0,len(dictFolderContent[fnTrainIndex])):
        arrItemTabTrainTest=dictFolderContent[fnTrainIndex][i].split('\t')
        # print('{} {}'.format(len(arrProgramRootEmb),i))
        strLoc=dictFolderContent[fnLocation][i]
        if strLoc in setErrorLogs:
            continue
        vectorItemPR=[float(i) for i in arrProgramRootEmb[i].split('\t')[3].split()]
        vectorItemNLR =[float(i) for i in arrNLRootEmb[i].split('\t')[3].split()]
        labelItem=dictFolderContent[fnLabelOverlap][i].split('\t')[0]
        if arrItemTabTrainTest[0]=='test':
            X_test_PR.append(vectorItemPR)
            X_test_NLR.append(vectorItemNLR)
            y_test.append(labelItem)
        else:
            X_train_PR.append(vectorItemPR)
            X_train_NLR.append(vectorItemNLR)
            y_train.append(labelItem)
    fopItemSummary=fopStep6ResultBaseline+embedModel+'/ProgramRoot/'
    createDirIfNotExist(fopItemSummary)
    acc,precision,recall,fscore,fit_time,pred_time=runMLModelAndSaveSummary(X_train_PR,y_train,X_test_PR,y_test,fopItemSummary)
    strAccPR='{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(embedModel,'ProgramRoot', precision,recall,fscore,acc,fit_time,pred_time)

    fopItemSummary = fopStep6ResultBaseline + embedModel + '/NLRoot/'
    createDirIfNotExist(fopItemSummary)
    acc,precision, recall, fscore,  fit_time, pred_time = runMLModelAndSaveSummary(X_train_NLR, y_train, X_test_NLR,
                                                                                   y_test, fopItemSummary)
    strAccNLR = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(embedModel, 'NLRoot', precision, recall, fscore, acc,
                                                       fit_time, pred_time)
    f1=open(fpOverallResult,'a')
    f1.write('\n'.join([strAccPR,strAccNLR])+'\n')
    f1.close()






