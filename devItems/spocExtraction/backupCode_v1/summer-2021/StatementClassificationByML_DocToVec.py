import glob
import sys, os
import operator
import clang.cindex
import json
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.model_selection import cross_val_score,cross_val_predict, StratifiedKFold
from sklearn.metrics import precision_score,cohen_kappa_score
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText


def runMLDoc2VecClassification(fopData, fpTrain, fpTestP, fpTestW, fopMLResult):
    createDirIfNotExist(fopMLResult)
    fpD2v=fopMLResult+'d2v.txt'
    f1=open(fpTrain,'r')
    strTrain=f1.read().strip()
    f1.close()
    f1 = open(fpTestP, 'r')
    strTestP = f1.read().strip()
    f1.close()
    f1 = open(fpTestW, 'r')
    strTestW = f1.read().strip()
    f1.close()

    arrTrain=strTrain.split('\n')
    arrTestP = strTestP.split('\n')
    arrTestW = strTestW.split('\n')

    corpusTrain=[]
    corpusTestP=[]
    corpusTestW=[]
    corpus=[]

    labelTrain = []
    labelTestP = []
    labelTestW = []

    for i in range(0,len(arrTrain)):
        if arrTrain[i].strip().endswith('code.txt'):
            continue
        arrItem=arrTrain[i].strip().split('\t')
        if(len(arrItem)<4):
            continue
        strPseudoCode=arrItem[2]
        strLabel=arrItem[0].replace(',','-')
        # print(strLabel)
        corpusTrain.append(strPseudoCode)
        corpus.append(strPseudoCode)
        labelTrain.append(strLabel)
    for i in range(0,len(arrTestP)):
        if arrTestP[i].strip().endswith('code.txt'):
            continue
        arrItem=arrTestP[i].strip().split('\t')
        if (len(arrItem) < 4):
            continue
        strPseudoCode=arrItem[2]
        strLabel=arrItem[0].replace(',','-')
        corpusTestP.append(strPseudoCode)
        corpus.append(strPseudoCode)
        labelTestP.append(strLabel)
    for i in range(0,len(arrTestW)):
        if arrTestW[i].strip().endswith('code.txt'):
            continue
        arrItem=arrTestW[i].strip().split('\t')
        if (len(arrItem) < 4):
            continue
        strPseudoCode=arrItem[2]
        strLabel=arrItem[0].replace(',','-')
        corpusTestW.append(strPseudoCode)
        corpus.append(strPseudoCode)
        labelTestW.append(strLabel)

    tagged_data = [TaggedDocument(words=word_tokenize(_d), tags=[str(i)]) for i, _d in enumerate(corpus)]

    max_epochs = 5
    vec_size = 20
    alpha = 0.025

    model = Doc2Vec(size=vec_size,
                    alpha=alpha,
                    min_alpha=0.00025,
                    min_count=1,
                    dm=0)

    model.build_vocab(tagged_data)

    for epoch in range(max_epochs):
        # print('iteration {0}'.format(epoch))
        model.train(tagged_data,
                    total_examples=model.corpus_count,
                    epochs=model.iter)
        # decrease the learning rate
        model.alpha -= 0.0002
        # fix the learning rate, no decay
        model.min_alpha = model.alpha
        print('End epoch{}'.format(epoch))

    model.save(fpD2v)

    XTrain = []
    XTestP = []
    XTestW = []

    for i in range(len(corpusTrain)):
        item = corpusTrain[i]
        x_data = word_tokenize(item)
        v1 = model.infer_vector(x_data)
        XTrain.append(v1)
    for i in range(len(corpusTestP)):
        item = corpusTestP[i]
        x_data = word_tokenize(item)
        v1 = model.infer_vector(x_data)
        XTestP.append(v1)
    for i in range(len(corpusTestW)):
        item = corpusTestW[i]
        x_data = word_tokenize(item)
        v1 = model.infer_vector(x_data)
        XTestW.append(v1)


    fpCSVTrain=fopMLResult+'train.csv'
    fpCSVTestP = fopMLResult + 'testP.csv'
    fpCSVTestW = fopMLResult + 'testW.csv'

    lenVector=len(XTrain[0])
    print('len vector{}'.format(lenVector))


    # columnTitleRow = "no,score,"
    lstItemTitle=[]
    lstItemTitle.append("no,score")
    for i in range(0, lenVector):
        item = 'feature-' + str(i + 1)
        lstItemTitle.append(item)
        # columnTitleRow = ','.join([columnTitleRow, item])
        # if i != lenVector - 1:
        #     columnTitleRow = ''.join([columnTitleRow, ","])
    # columnTitleRow = ''.join([columnTitleRow, "\n"])
    columnTitleRow=','.join(lstItemTitle)
    print(columnTitleRow)
    lstCsv = []
    lstCsv.append(columnTitleRow)
    # csv.write(columnTitleRow)
    # print(str(len(corpus)))

    print('size of train {}'.format(len(corpusTrain)))
    for i in range(0, len(corpusTrain)):
        vectori = XTrain[i]
        row = ''.join([str(i + 1), ',', str(labelTrain[i]), ','])
        strVector = ",".join(str(j) for j in vectori)
        row = ''.join([row, strVector])
        if i>=10 and i <=20:
            print(row)
        lstCsv.append(row)
        # print('line {}'.format(i))
        # csv.write(row)
    csv = open(fpCSVTrain, 'w')
    csv.write('\n'.join(lstCsv))
    csv.close()

    print('size of testP {}'.format(len(corpusTestP)))
    lstCsv = []
    lstCsv.append(columnTitleRow)
    for i in range(0, len(corpusTestP)):
        vectori = XTestP[i]
        row = ''.join([str(i + 1), ',', str(labelTestP[i]), ','])
        strVector = ",".join(str(j) for j in vectori)
        row = ''.join([row, strVector])
        lstCsv.append(row)
        # csv.write(row)
    csv = open(fpCSVTestP, 'w')
    csv.write('\n'.join(lstCsv))
    csv.close()

    print('size of testW {}'.format(len(corpusTestW)))
    lstCsv = []
    lstCsv.append(columnTitleRow)
    for i in range(0, len(corpusTestW)):
        vectori = XTestW[i]
        row = ''.join([str(i + 1), ',', str(labelTestW[i]), ','])
        strVector = ",".join(str(j) for j in vectori)
        row = ''.join([row, strVector])
        lstCsv.append(row)
        # csv.write(row)
    csv = open(fpCSVTestW, 'w')
    csv.write('\n'.join(lstCsv))
    csv.close()


    classifier = RandomForestClassifier()
    df_train = pd.read_csv(fpCSVTrain)
    train_label = df_train['score']
    train_data = df_train.drop(['no', 'score'], axis=1)
    df_testP = pd.read_csv(fpCSVTestP)
    testP_label = df_train['score']
    testP_data = df_train.drop(['no', 'score'], axis=1)
    df_testW = pd.read_csv(fpCSVTestW)
    testW_label = df_train['score']
    testW_data = df_train.drop(['no', 'score'], axis=1)

    filePredictTestP = ''.join([fopMLResult, 'predictResult_TestP', '.txt'])
    filePredictTestW = ''.join([fopMLResult, 'predictResult_TestW', '.txt'])
    print("********", "\n", "Results with: ", str(classifier))
    classifier.fit(train_data, train_label)

    predictedTestP = classifier.predict(testP_data)
    predictedTestW = classifier.predict(testW_data)
    weightAvgTestP = precision_score(testP_label, predictedTestP, average='weighted') * 100
    weightAvgTestW = precision_score(testW_label, predictedTestW, average='weighted') * 100

    np.savetxt(filePredictTestP, predictedTestP, fmt='%s', delimiter=',')
    np.savetxt(filePredictTestW, predictedTestW, fmt='%s', delimiter=',')
    o2 = open(fopMLResult + 'report.txt', 'w')
    o2.write('Result for ' + str(classifier) + '\n')
    quadraticKappaScoreTestP = cohen_kappa_score(testP_label, predictedTestP, weights='quadratic')
    quadraticKappaScoreTestW = cohen_kappa_score(testW_label, predictedTestW, weights='quadratic')
    o2.write(
        'TestP\nTotal accuracy: {}\nQuadratic kappa score: {}\n\n'.format(weightAvgTestP, quadraticKappaScoreTestP))
    o2.write('Confusion matrix:\n')
    o2.write(str(confusion_matrix(testP_label, predictedTestP)) + '\n')
    o2.write(str(classification_report(testP_label, predictedTestP)) + '\n\n\n')

    o2.write(
        'TestW\nTotal accuracy: {}\nQuadratic kappa score: {}\n\n'.format(weightAvgTestW, quadraticKappaScoreTestW))
    o2.write('Confusion matrix:\n')
    o2.write(str(confusion_matrix(testW_label, predictedTestW)) + '\n')
    o2.write(str(classification_report(testW_label, predictedTestW)) + '\n\n\n')
    o2.close()



fopData='../../../dataPapers/textInSPOC/'
fpTrain=fopData+'statementLbl_train.txt'
fpTestP=fopData+'statementLbl_testP.txt'
fpTestW=fopData+'statementLbl_testW.txt'
fopMLResult=fopData+'statementLbl_MLResult_doc2vec/'

runMLDoc2VecClassification(fopData, fpTrain, fpTestP, fpTestW, fopMLResult)
