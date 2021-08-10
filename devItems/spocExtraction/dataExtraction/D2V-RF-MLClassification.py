import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import pygraphviz as pgv
import pylab,traceback
from pyparsing import OneOrMore, nestedExpr
import  gzip,json
import ast
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from sklearn.metrics import classification_report
from sklearn.metrics import cohen_kappa_score
from langdetect import detect
from sklearn.metrics import confusion_matrix
import langid



fopRoot='/home/hungphd/git/dataPapers/textInSPOC/mixCode_v2/step6/'
fpTrainText=fopRoot+'train.text.txt'
fpTestPText=fopRoot+'testP.text.txt'
fpTestWText=fopRoot+'testW.text.txt'
fpTrainLabel=fopRoot+'train.label.txt'
fpTestPLabel=fopRoot+'testP.label.txt'
fpTestWLabel=fopRoot+'testW.label.txt'

fopD2VRF=fopRoot+'result-d2v-rf/'
createDirIfNotExist(fopD2VRF)
fpOutModel=fopD2VRF+'model.d2v'
fpOutResultDetail=fopD2VRF+'resultDetail.txt'
fpOutResultSummary=fopD2VRF+'resultSummary.txt'

X_Train = []
key_Train = []
X_TestP = []
key_TestP = []
X_TestW = []
key_TestW = []
y_Train=[]
y_TestP=[]
y_TestW=[]
lstAllText = []

f1 = open(fpTrainText, 'r')
arrItems = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTrainLabel, 'r')
arrLabels = f1.read().strip().split('\n')
f1.close()


for i in range(0, len(arrItems)):
    item = arrItems[i]
    arrTabs = item.split('\t')
    key_Train.append(arrTabs[0])
    X_Train.append(arrTabs[1])
    arrLabelTabs = arrLabels[i].split('\t')
    y_Train.append(arrLabelTabs[1])
    lstAllText.append(arrTabs[1])

f1 = open(fpTestPText, 'r')
arrItems = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestPLabel, 'r')
arrLabels = f1.read().strip().split('\n')
f1.close()

for i in range(0, len(arrItems)):
    item = arrItems[i]
    arrTabs = item.split('\t')
    key_TestP.append(arrTabs[0])
    X_TestP.append(arrTabs[1])
    arrLabelTabs = arrLabels[i].split('\t')
    y_TestP.append(arrLabelTabs[1])
    lstAllText.append(arrTabs[1])

f1 = open(fpTestWText, 'r')
arrItems = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestWLabel, 'r')
arrLabels = f1.read().strip().split('\n')
f1.close()

for i in range(0, len(arrItems)):
    item = arrItems[i]
    arrTabs = item.split('\t')
    key_TestW.append(arrTabs[0])
    X_TestW.append(arrTabs[1])
    arrLabelTabs = arrLabels[i].split('\t')
    y_TestW.append(arrLabelTabs[1])
    lstAllText.append(arrTabs[1])


tagged_data = [TaggedDocument(words=word_tokenize(_d), tags=[str(i)]) for i, _d in enumerate(lstAllText)]
max_epochs = 5
vec_size = 100
alpha = 0.025

model = Doc2Vec(vector_size=vec_size,
                alpha=alpha,
                min_alpha=0.00025,
                min_count=1,
                dm=0)

model.build_vocab(tagged_data)

for epoch in range(max_epochs):
    # print('iteration {0}'.format(epoch))
    model.train(tagged_data,
                total_examples=model.corpus_count,
                epochs=model.epochs)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha
    print('End epoch{}'.format(epoch))
model.save(fpOutModel)
# model = Doc2Vec.load(fpOutModel)

d2v_all = []
dictWords = {}
# lstAllText=[]
vec_train=[]
vec_testP=[]
vec_testW=[]
for i in range(0, len(X_Train)):
    # lstAllText.append(X_Train[i])
    x_data = word_tokenize(X_Train[i])
    v1 = model.infer_vector(x_data)
    vec_train.append(v1)
    # d2v_all.append('{}\t{}'.format(key_Train[i], ' '.join(map(str, v1))))

for i in range(0, len(X_TestP)):
    # lstAllText.append(X_TestP[i])
    x_data = word_tokenize(X_TestP[i])
    v1 = model.infer_vector(x_data)
    vec_testP.append(v1)
    # d2v_all.append('{}\t{}'.format(key_TestP[i], ' '.join(map(str, v1))))

for i in range(0, len(X_TestW)):
    # lstAllText.append(X_TestW[i])
    x_data = word_tokenize(X_TestW[i])
    v1 = model.infer_vector(x_data)
    vec_testW.append(v1)
    # d2v_all.append('{}\t{}'.format(key_TestW[i], ' '.join(map(str, v1))))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support as score
import time
import numpy as np

rf = RandomForestClassifier(n_estimators=150, max_depth=None, n_jobs=-1,random_state = 42)
print('go here')
start = time.time()
rf_model = rf.fit(vec_train, y_Train)
# filename4 = fop+arrConfigs[idx]+ '_mlmodel.bin'
end = time.time()
fit_time = (end - start)
print('end train {}'.format(fit_time))
start = time.time()
y_predP = rf_model.predict(vec_testP)
end = time.time()
pred_time = (end - start)
print('end testP {}'.format(pred_time))


f1=open(fpOutResultDetail,'w')
precision, recall, fscore, train_support = score(y_TestP, y_predP)
accuracyP=np.round((y_predP==y_TestP).sum()/len(y_predP), 3)
f1.write('TestP\nFit time: {} / Predict time: {} ---- Precision: {} / Recall: {} / Accuracy: {}\n'.format(
    np.round(fit_time, 3), np.round(pred_time, 3), np.round(precision, 3), np.round(recall, 3), accuracyP))
f1.write('{}\n'.format(confusion_matrix(y_TestP, y_predP)))
f1.write('{}\n'.format(classification_report(y_TestP, y_predP)))
f1.write('Cohen Kappa{}\n\n\n'.format(cohen_kappa_score(y_TestP, y_predP, weights="quadratic")))

start = time.time()
y_predW = rf_model.predict(vec_testW)
end = time.time()
pred_time = (end - start)
print('end testW {}'.format(pred_time))
precision, recall, fscore, train_support = score(y_TestW, y_predW)
accuracyW=np.round((y_predW==y_TestW).sum()/len(y_predW), 3)
f1.write('TestW\nFit time: {} / Predict time: {} ---- Precision: {} / Recall: {} / Accuracy: {}\n'.format(
    np.round(fit_time, 3), np.round(pred_time, 3), np.round(precision, 3), np.round(recall, 3), accuracyW))
f1.write('{}\n'.format(confusion_matrix(y_TestW, y_predW)))
f1.write('{}\n'.format(classification_report(y_TestW, y_predW)))
f1.write('Cohen Kappa {}\n\n\n'.format(cohen_kappa_score(y_TestW, y_predW, weights="quadratic")))
f1.close()

f1=open(fpOutResultSummary,'w')
f1.write('D2v-RF\t{}\t{}'.format(accuracyP,accuracyW))
f1.close()

