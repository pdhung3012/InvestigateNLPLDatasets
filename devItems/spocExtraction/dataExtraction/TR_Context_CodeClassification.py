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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support as score
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA


fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopMixDataAndLabel=fopRoot+'step5_data_mixCode/'
fopResultMLs=fopRoot+'step6_resultMLs/'

fpTrainLocation=fopMixDataAndLabel+'train.location.txt'
fpTestPLocation=fopMixDataAndLabel+'testP.location.txt'
fpTestWLocation=fopMixDataAndLabel+'testW.location.txt'
fpTrainText=fopMixDataAndLabel+'train.input.pseudo.txt'
fpTestPText=fopMixDataAndLabel+'testP.input.pseudo.txt'
fpTestWText=fopMixDataAndLabel+'testW.input.pseudo.txt'
fpTrainPrefix=fopMixDataAndLabel+'train.input.prefix.txt'
fpTestPPrefix=fopMixDataAndLabel+'testP.input.prefix.txt'
fpTestWPrefix=fopMixDataAndLabel+'testW.input.prefix.txt'
fpTrainPostfix=fopMixDataAndLabel+'train.input.postfix.txt'
fpTestPPostfix=fopMixDataAndLabel+'testP.input.postfix.txt'
fpTestWPostfix=fopMixDataAndLabel+'testW.input.postfix.txt'
fpTrainLabel=fopMixDataAndLabel+'train.label.codeClass.txt'
fpTestPLabel=fopMixDataAndLabel+'testP.label.codeClass.txt'
fpTestWLabel=fopMixDataAndLabel+'testW.label.codeClass.txt'

fopD2VRF=fopResultMLs+'pseudoAndContext-tfidf-lda/'
createDirIfNotExist(fopD2VRF)
# fpOutModel=fopD2VRF+'model.d2v'
fpOutResultDetail=fopD2VRF+'resultDetail.txt'
fpOutResultSummary=fopD2VRF+'resultSummary.txt'
fpOutResultTestP=fopD2VRF+'resultTestP.txt'
fpOutResultTestW=fopD2VRF+'resultTestW.txt'

X_Train = []
key_Train = []
X_TestP = []
key_TestP = []
X_TestW = []
key_TestW = []
y_Train=[]
y_TestP=[]
y_TestW=[]
l_Train=[]
l_TestP=[]
l_TestW=[]
lstAllText = []

f1 = open(fpTrainText, 'r')
arrItems = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTrainPrefix, 'r')
arrTrainPrefixes = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTrainPostfix, 'r')
arrTrainPostfixes = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTrainLabel, 'r')
arrLabels = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTrainLocation, 'r')
arrLocations = f1.read().strip().split('\n')
f1.close()


for i in range(0, len(arrItems)):
    item = arrItems[i]
    X_Train.append(item)
    y_Train.append(arrLabels[i])
    l_Train.append(arrLocations[i])
    lstAllText.append(item)

f1 = open(fpTestPText, 'r')
arrItems = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestPPrefix, 'r')
arrTestPPrefixes = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestPPostfix, 'r')
arrTestPPostfixes = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestPLabel, 'r')
arrLabels = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestPLocation, 'r')
arrLocations = f1.read().strip().split('\n')
f1.close()

for i in range(0, len(arrItems)):
    item = arrItems[i]
    X_TestP.append(item)
    y_TestP.append(arrLabels[i])
    l_TestP.append(arrLocations[i])
    lstAllText.append(item)

f1 = open(fpTestWText, 'r')
arrItems = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestWPrefix, 'r')
arrTestWPrefixes = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestWPostfix, 'r')
arrTestWPostfixes = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestWLabel, 'r')
arrLabels = f1.read().strip().split('\n')
f1.close()
f1 = open(fpTestWLocation, 'r')
arrLocations = f1.read().strip().split('\n')
f1.close()


for i in range(0, len(arrItems)):
    item = arrItems[i]
    X_TestW.append(item)
    y_TestW.append(arrLabels[i])
    l_TestW.append(arrLocations[i])
    lstAllText.append(item)

vectorizer = TfidfVectorizer(ngram_range=(1, 4),max_features=1000)
model = vectorizer.fit(lstAllText)
# vec_total_all=model.transform(lstAllText).toarray()
vec_train_all=model.transform(X_Train).toarray()
vec_testP_all=model.transform(X_TestP).toarray()
vec_testW_all=model.transform(X_TestW).toarray()

arr_pre_all=arrTrainPrefixes+arrTestPPrefixes+arrTestWPrefixes
vectorizer = TfidfVectorizer(ngram_range=(1, 4),max_features=1000)
model = vectorizer.fit(arr_pre_all)
# vec_total_all=model.transform(lstAllText).toarray()
vec_train_pre=model.transform(arrTrainPrefixes).toarray()
vec_testP_pre=model.transform(arrTestPPrefixes).toarray()
vec_testW_pre=model.transform(arrTestWPrefixes).toarray()

arr_post_all=arrTrainPostfixes+arrTestPPostfixes+arrTestWPostfixes
vectorizer = TfidfVectorizer(ngram_range=(1, 4),max_features=1000)
model = vectorizer.fit(arr_post_all)
# vec_total_all=model.transform(lstAllText).toarray()
vec_train_post=model.transform(arrTrainPostfixes).toarray()
vec_testP_post=model.transform(arrTestPPostfixes).toarray()
vec_testW_post=model.transform(arrTestWPostfixes).toarray()


#pca = PCA(n_components=100)
print('prepare to fit transform')
# vec_train=vec_train_all
# vec_testP=vec_testP_all
# vec_testW=vec_testW_all
import numpy as np
vec_train= np.concatenate([vec_train_all,vec_train_pre,vec_train_post],axis=1)
vec_testP=np.concatenate([vec_testP_all,vec_testP_pre,vec_testP_post],axis=1)
vec_testW=np.concatenate([vec_testW_all,vec_testW_pre,vec_testW_post],axis=1)

print('end fit transform')

y_all=y_Train+y_TestP+y_TestW
lstSortedLabels=sorted(set(y_all))
dictSortedLbls={}
for i in range(0,len(lstSortedLabels)):
    dictSortedLbls[lstSortedLabels[i]]=i+1



# rf = RandomForestClassifier(n_estimators=150, max_depth=None, n_jobs=-1,random_state = 42)
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
rf=LinearDiscriminantAnalysis()
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

lstTups=[]
for i in range(0,len(y_TestP)):
    dist=abs(dictSortedLbls[y_TestP[i]]-dictSortedLbls[y_predP[i]])
    tup=(dist,y_TestP[i],y_predP[i],l_TestP[i])
    lstTups.append(tup)
lstTups.sort(reverse=True)

lstStrTup=[]
for tup in lstTups:
    strItem='{}\t{}\t{}\t{}'.format(tup[0],tup[1],tup[2],tup[3])
    lstStrTup.append(strItem)
f2=open(fpOutResultTestP,'w')
f2.write('\n'.join(lstStrTup))
f2.close()


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

lstTups=[]
for i in range(0,len(y_TestW)):
    dist=abs(dictSortedLbls[y_TestW[i]]-dictSortedLbls[y_predW[i]])
    tup=(dist,y_TestW[i],y_predW[i],l_TestW[i])
    lstTups.append(tup)
lstTups.sort(reverse=True)

lstStrTup=[]
for tup in lstTups:
    strItem='{}\t{}\t{}\t{}'.format(tup[0],tup[1],tup[2],tup[3])
    lstStrTup.append(strItem)
f2=open(fpOutResultTestW,'w')
f2.write('\n'.join(lstStrTup))
f2.close()

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
f1.write('BOW-RF\t{}\t{}'.format(accuracyP,accuracyW))
f1.close()

