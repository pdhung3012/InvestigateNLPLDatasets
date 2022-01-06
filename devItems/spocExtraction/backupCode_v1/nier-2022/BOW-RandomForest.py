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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support as score
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score


fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fpInputText=fopRoot+'embeddingModels/d2v/paragraph_text.txt'
fopOutputML=fopRoot+'resultMLs/bow/'
fpResultDetails=fopOutputML+'result_details.txt'
createDirIfNotExist(fopOutputML)

f1=open(fpInputText,'r')
arrText=f1.read().strip().split('\n')
f1.close()

trainIndex=0
lstAllData=[]
num_features=100

keyStartEnd=''
dictStartEnd={}
index=0
lstTuplesTrainTestValid=[]
arrText.reverse()
for i in range(1,len(arrText),2):
    try:
        arrItemTabs = arrText[i].split('\t')
        fpItem = arrItemTabs[0]
        arrFpItems = fpItem.split('/')
        strTrainTestValid = arrFpItems[len(arrFpItems) - 3]
        # print(strTrainTestValid)
        if keyStartEnd == '':
            dictStartEnd[strTrainTestValid] = [index, -1]
            keyStartEnd = strTrainTestValid
        elif keyStartEnd != strTrainTestValid:
            dictStartEnd[keyStartEnd][1] = index
            dictStartEnd[strTrainTestValid]= [index,-1]
            keyStartEnd=strTrainTestValid
        if i == len(arrText) - 1:
            dictStartEnd[strTrainTestValid][1] = index
        index = index + 1
        strItemContent = '\t'.join(arrItemTabs[4:])
        f1 = open(fpItem, 'r')
        arrLabels = f1.read().strip().split('\n')
        f1.close()
        strFirstLabel = arrLabels[0]
        strSecondLabel = arrLabels[2]
        arrPercent = arrLabels[10].split('\t')
        numAppear = int(arrPercent[0])
        numDisappear = int(arrPercent[1])
        strThirdLabel = int((numAppear * 100.0 / (numAppear + numDisappear)) // 10 + 1)
        if strThirdLabel > 10:
            strThirdLabel = 10
        strThirdLabel = str(strThirdLabel)
        lstItem = [strFirstLabel, strSecondLabel, strThirdLabel, strItemContent, arrItemTabs[0], strTrainTestValid]
        lstTuplesTrainTestValid.append(lstItem)
        if((i+1)%2000==0):
            print('end {}'.format(i))
    except:
        traceback.print_exc()
print('finish')
sys.stdout = open(fpResultDetails, 'w')


idxTrainStart=dictStartEnd['train'][0]
idxTrainEnd=dictStartEnd['train'][1]
idxTestPStart=dictStartEnd['testP'][0]
idxTestPEnd=dictStartEnd['testP'][1]
idxTestWStart=dictStartEnd['testW'][0]
idxTestWEnd=dictStartEnd['testW'][1]

print('train [{},{})\ntestP [{},{})\ntestW [{},{})'.format(idxTrainStart,idxTrainEnd,idxTestPStart,idxTestPEnd,idxTestWStart,idxTestWEnd))


vectorizer = TfidfVectorizer(ngram_range=(1, 4),max_features=num_features)
lstAllText=[i[3] for i in lstTuplesTrainTestValid]
y_problem_1=[i[0] for i in lstTuplesTrainTestValid]
y_problem_2=[i[1] for i in lstTuplesTrainTestValid]
y_problem_3=[i[2] for i in lstTuplesTrainTestValid]
model = vectorizer.fit(lstAllText)


X_Train=lstAllText[idxTrainStart:idxTrainEnd]
X_TestW=lstAllText[idxTestWStart:idxTestWEnd]

# vec_total_all=model.transform(lstAllText).toarray()
vec_train=model.transform(X_Train).toarray()
# vec_testP_all=model.transform(X_TestP).toarray()
vec_testW=model.transform(X_TestW).toarray()

y_Train_p1=y_problem_1[idxTrainStart:idxTrainEnd]
y_Train_p2=y_problem_2[idxTrainStart:idxTrainEnd]
y_Train_p3=y_problem_3[idxTrainStart:idxTrainEnd]
y_TestW_p1=y_problem_1[idxTestWStart:idxTestWEnd]
y_TestW_p2=y_problem_2[idxTestWStart:idxTestWEnd]
y_TestW_p3=y_problem_3[idxTestWStart:idxTestWEnd]


print('train [{},{})\ntestP [{},{})\ntestW [{},{})'.format(idxTrainStart,idxTrainEnd,idxTestPStart,idxTestPEnd,idxTestWStart,idxTestWEnd))

rf = RandomForestClassifier(n_estimators=150, max_depth=None, n_jobs=-1,random_state = 42)
print('problem 1:')
rf_model = rf.fit(vec_train, y_Train_p1)
pred_testW_p1 = rf_model.predict(vec_testW)
print('{}\n'.format(confusion_matrix(y_TestW_p1, pred_testW_p1)))
print('{}\n'.format(classification_report(y_TestW_p1, pred_testW_p1)))
acc_testw_p1=accuracy_score(y_TestW_p1, pred_testW_p1)

rf = RandomForestClassifier(n_estimators=150, max_depth=None, n_jobs=-1,random_state = 42)
print('problem 2:')
rf_model = rf.fit(vec_train, y_Train_p2)
pred_testW_p2 = rf_model.predict(vec_testW)
print('{}\n'.format(confusion_matrix(y_TestW_p2, pred_testW_p2)))
print('{}\n'.format(classification_report(y_TestW_p2, pred_testW_p2)))
acc_testw_p2=accuracy_score(y_TestW_p2, pred_testW_p2)

rf = RandomForestClassifier(n_estimators=150, max_depth=None, n_jobs=-1,random_state = 42)
print('problem 3:')
rf_model = rf.fit(vec_train, y_Train_p3)
pred_testW_p3 = rf_model.predict(vec_testW)
print('{}\n'.format(confusion_matrix(y_TestW_p3, pred_testW_p3)))
print('{}\n'.format(classification_report(y_TestW_p3, pred_testW_p3)))
acc_testw_p3=accuracy_score(y_TestW_p3, pred_testW_p3)

print('\n\nacc problem 1\t{}\nacc problem 2\t{}\nacc problem 3\t{}'.format(acc_testw_p1,acc_testw_p2,acc_testw_p3))


sys.stdout.close()
sys.stdout = sys.__stdout__
# [i[0] for i in a]








