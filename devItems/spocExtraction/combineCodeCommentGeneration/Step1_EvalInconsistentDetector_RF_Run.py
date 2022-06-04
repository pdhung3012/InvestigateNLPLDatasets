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


def jaccardSimilarityList(list1,list2):
    # list1=sourceSentence.lower().split()
    # list2=targetSentence.lower().split()
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union


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


fopStanfordCoreNLP='/home/hungphd/git/dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputStep3V2=fopRoot+'step3_v2/'
fopFasttextEmb=fopRoot+'embeddingModels/fasttext-cbow/'
fopInputStep6Incons=fopRoot+'step6_Incons/fasttext-RF/'
createDirIfNotExist(fopInputStep6Incons)

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
fnTrainValidTest='trainValidTest.index.txt'
fnInconsistentSource='inconsistentSource.txt'

import fasttext
fpModelBin=fopFasttextEmb+'model.bin'
model = fasttext.FastText.load_model(fpModelBin)

fpTextInfo=fopInputStep6Incons+'text.txt'
fpEmbLabelInfo=fopInputStep6Incons+'embInconsistent.txt'

X_train_PR = []
X_train_NLR = []
y_train = []
X_test_PR = []
X_test_NLR = []
y_test = []

f1=open(fpEmbLabelInfo,'r')
arrEmb=f1.read().strip().split('\n')

for i in range(0, len(arrEmb)):
    arrItemTabTrainTest = arrEmb[i].split('\t')
    # print('{} {}'.format(len(arrProgramRootEmb),i))
    vectorItemPR = [float(i) for i in arrItemTabTrainTest[5].split()]
    labelItem = arrItemTabTrainTest[1]
    if arrItemTabTrainTest[0] == 'test':
        X_test_PR.append(vectorItemPR)
        y_test.append(labelItem)
    else:
        X_train_PR.append(vectorItemPR)
        y_train.append(labelItem)
fopItemSummary = fopInputStep6Incons+'acc/'
createDirIfNotExist(fopItemSummary)
acc, precision, recall, fscore, fit_time, pred_time = runMLModelAndSaveSummary(X_train_PR, y_train, X_test_PR, y_test,
                                                                               fopItemSummary)
strAccPR = '\t{}\t{}\t{}\t{}\t{}\t{}'.format( precision, recall, fscore, acc, fit_time,
                                                   pred_time)

fpOverallResult=fopItemSummary+'overall.txt'
f1 = open(fpOverallResult, 'a')
f1.write('\n'.join([strAccPR]) + '\n')
f1.close()

































