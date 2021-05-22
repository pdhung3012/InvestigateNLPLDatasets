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

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

strConstError='Error_Val'
strConstSplitWord=' ABA '
distanceOfCPPFile=33



def getListOfFeatures(arrPseudoCodes,arrLabels,indexOfPseudoCodes):
    txtCurrentPS=arrPseudoCodes[indexOfPseudoCodes-1]
    arrCurrentPS=txtCurrentPS.split(' ')
    score1=len(arrCurrentPS)
    lstScores=[]
    lstScores.append(score1)
    if 'function' in arrCurrentPS:
        score2=1
    else:
        score2=0
    lstScores.append(score2)
    if 'nan' in arrCurrentPS:
        score3=1
    else:
        score3=0
    lstScores.append(score3)
    score4=len(txtCurrentPS)
    lstScores.append(score4)
    score5=indexOfPseudoCodes
    lstScores.append(score5)
    score6=len(arrPseudoCodes)-indexOfPseudoCodes
    lstScores.append(score6)
    score7=indexOfPseudoCodes

    indexScore7=indexOfPseudoCodes-1
    while indexScore7>0:
        strItem=arrPseudoCodes[indexScore7-1].strip()
        if strItem.lower().startswith('for') or strItem.lower().startswith('iterate'):
            break
        indexScore7=indexScore7-1
    score7=indexOfPseudoCodes-indexScore7
    lstScores.append(score7)

    score8 = indexOfPseudoCodes
    indexScore8 = indexOfPseudoCodes - 1
    while indexScore8 > 0:
        strItem = arrPseudoCodes[indexScore8 - 1].strip()
        if strItem.lower().startswith('return'):
            break
        indexScore8 = indexScore8 - 1
    score8 = indexOfPseudoCodes= indexScore8
    lstScores.append(score8)

    if 'return' in arrCurrentPS or  'returns' in arrCurrentPS:
        score9 = 1
    else:
        score9 = 0
    lstScores.append(score9)

    return lstScores










def prepareTrainingDataAndLabel(fpPseudoCodeData,fpFuncDeclData,fpCodeData,fpCSVData,fpTxtData):
    f1=open(fpPseudoCodeData,'r')
    arrPseudos=f1.read().split('\n')
    f1.close()
    dictPseudoCode = {}
    txtName=''
    for i in range(0,len(arrPseudos)):
        itemStrip=arrPseudos[i].strip()
        if itemStrip.endswith('_text.txt'):
            txtName=itemStrip.replace('_text.txt','')
            lstContent=[]
            dictPseudoCode[txtName]=lstContent
        else:
            dictPseudoCode[txtName].append(arrPseudos[i])

    f1 = open(fpCodeData, 'r')
    arrCodes = f1.read().split('\n')
    f1.close()
    dictCode = {}
    txtName = ''
    for i in range(0, len(arrCodes)):
        itemStrip = arrCodes[i].strip()
        if itemStrip.endswith('_text.txt'):
            txtName = itemStrip.replace('_text.txt', '')
            lstContent = []
            dictCode[txtName] = lstContent
        else:
            dictCode[txtName].append(arrCodes[i])

    f1 = open(fpFuncDeclData, 'r')
    arrFuncDecl = f1.read().split('\n')
    f1.close()
    dictLabelFuncDecl={}
    txtName = ''



    for i in range(0, len(arrFuncDecl)):
        itemStrip = arrFuncDecl[i].strip()
        if itemStrip.endswith('_code.cpp'):
            txtName = itemStrip.replace('_code.cpp', '')
            lstContent = []
            dictLabelFuncDecl[txtName] = lstContent
        else:
            dictLabelFuncDecl[txtName].append(arrFuncDecl[i])
    f1 = open(fpTxtData,'w')
    f1.write('')
    f1.close()

    for key in dictLabelFuncDecl.keys():
        lstFuncDel=dictLabelFuncDecl[key]
        lstNewLabel=[]
        arrPseudoCodeItem = '\n'.join(dictPseudoCode[key]).strip().split('\n')
        arrCodeItem = '\n'.join(dictCode[key]).strip().split('\n')
        # print(lstFuncDel)
        for i in range(0,len(lstFuncDel)):
            strItem=lstFuncDel[i].strip()
            arrItem=strItem.split('\t')
            # print('here {}'.format(strItem))
            if(len(arrItem)>=2):

                if '-' in arrItem[0] and arrItem[1].startswith('FunctionDecl'):
                    beginLine=int(arrItem[0].split('-')[0])-distanceOfCPPFile
                    endLine = int(arrItem[0].split('-')[1])-distanceOfCPPFile
                    if beginLine > len(arrPseudoCodeItem) or endLine > len(arrPseudoCodeItem):
                        continue
                    strPSLine = arrPseudoCodeItem[beginLine - 1]
                    strCodeLine = arrCodeItem[beginLine - 1]
                    strBeginLbl = '{}\t{}\t{}\t{}'.format('FuncDecl_Begin',beginLine,strPSLine,strCodeLine )
                    lstNewLabel.append(strBeginLbl)
                    if beginLine !=endLine:
                        strPSLine = arrPseudoCodeItem[endLine - 1]
                        strCodeLine = arrCodeItem[endLine - 1]
                        strEndLbl = '{}\t{}\t{}\t{}'.format('FuncDecl_End',endLine,strPSLine,strCodeLine )
                        lstNewLabel.append(strEndLbl)
                elif '-' not in arrItem[0]:

                    beginLine = int(arrItem[0]) - distanceOfCPPFile
                    if beginLine > len(arrPseudoCodeItem):
                        continue
                    strPSLine = arrPseudoCodeItem[beginLine - 1]
                    strCodeLine = arrCodeItem[beginLine - 1]

                    strBeginLbl = '{}\t{}\t{}\t{}'.format('OtherStatement',beginLine,strPSLine,strCodeLine )
                    lstNewLabel.append(strBeginLbl)
        dictLabelFuncDecl[key]=lstNewLabel

        dictSingleStmt = {}
        for oldI in range(0, len(lstNewLabel)):
            i = len(lstNewLabel) - 1 - oldI
            numLine = int(lstNewLabel[i].split('\t')[1])
            if numLine not in dictSingleStmt:
                # print(numLine)
                # print(lstNewLabel[i])
                dictSingleStmt[numLine] = lstNewLabel[i]

        lstAdd = []
        for keyLine in sorted(dictSingleStmt.keys()):
            lstAdd.append(dictSingleStmt[keyLine])

        # dictLabelFuncDecl[key]=lstNewLabel
        # strNewLabel='\n'.join(lstNewLabel)
        strNewLabel = '\n'.join(lstAdd)
        strWriteToFile = '\n'.join([key + '_code.txt', strNewLabel, '\n\n\n'])
        f1 = open(fpTxtData, 'a')
        f1.write(strWriteToFile)
        f1.close()

    csv = open(fpCSVData, 'w')
    indexKey=0
    indexCsv=0
    for key in dictPseudoCode.keys():

        lstPseudoCodeItem=dictPseudoCode[key]
        lstPseudoCodeItem='\n'.join(lstPseudoCodeItem).strip().split('\n')
        if key in dictLabelFuncDecl.keys():

            indexKey=indexKey+1
            arrStmt=dictLabelFuncDecl[key]
            # print(arrStmt)
            for i in range(0,len(arrStmt)):
                lineCheck=int(arrStmt[i].split('\t')[1])
                lblCheck=arrStmt[i].split('\t')[0]
                lstFeaturesItems=getListOfFeatures(arrPseudos,arrStmt,lineCheck)
                # print('{}\t{}'.format(key,lstFeaturesItems))
                if i==0 and indexKey==1:
                    lenFeats=len(lstFeaturesItems)

                    columnTitleRow = "no,programid,line,score,"
                    for i2 in range(0, lenFeats):
                        item = 'feature-' + str(i2 + + 1)
                        columnTitleRow = ''.join([columnTitleRow, item])
                        if i2 != lenFeats - 1:
                            columnTitleRow = ''.join([columnTitleRow, ","])
                    columnTitleRow = ''.join([columnTitleRow, "\n"])
                    # print(columnTitleRow)
                    csv.write(columnTitleRow)

                # vectori = X[i]
                strFeati = ','.join(map(str,lstFeaturesItems))
                indexCsv = indexCsv + 1
                row = ''.join([str(indexCsv), ',', str(key), ',', str(lineCheck), ',', str(lblCheck), ',',strFeati,'\n'])
                csv.write(row)
    csv.close()

def runMLAlgm(fpTrain,fpTestP,fpTestW,fopResultML):
    classifier= RandomForestClassifier()
    df_train = pd.read_csv(fpTrain)
    train_label = df_train['score']
    train_data = df_train.drop(['no', 'score','programid','line'], axis=1)
    df_testP = pd.read_csv(fpTestP)
    testP_label = df_train['score']
    testP_data = df_train.drop(['no', 'score', 'programid', 'line'], axis=1)
    df_testW = pd.read_csv(fpTestW)
    testW_label = df_train['score']
    testW_data = df_train.drop(['no', 'score', 'programid', 'line'], axis=1)

    filePredictTestP = ''.join([fopResultML, 'predictResult_TestP', '.txt'])
    filePredictTestW = ''.join([fopResultML, 'predictResult_TestW', '.txt'])
    print("********", "\n", "Results with: ", str(classifier))
    classifier.fit(train_data,train_label)

    predictedTestP = classifier.predict(testP_data)
    predictedTestW = classifier.predict(testW_data)
    weightAvgTestP = precision_score(testP_label, predictedTestP, average='weighted') * 100
    weightAvgTestW = precision_score(testW_label, predictedTestW, average='weighted') * 100

    np.savetxt(filePredictTestP, predictedTestP, fmt='%s', delimiter=',')
    np.savetxt(filePredictTestW, predictedTestW, fmt='%s', delimiter=',')
    o2 = open(fopResultML + 'report.txt', 'w')
    o2.write('Result for ' + str(classifier) + '\n')
    quadraticKappaScoreTestP=cohen_kappa_score(testP_label, predictedTestP,weights='quadratic')
    quadraticKappaScoreTestW = cohen_kappa_score(testW_label, predictedTestW, weights='quadratic')
    o2.write('TestP\nTotal accuracy: {}\nQuadratic kappa score: {}\n\n'.format(weightAvgTestP,quadraticKappaScoreTestP))
    o2.write('Confusion matrix:\n')
    o2.write(str(confusion_matrix(testP_label, predictedTestP)) + '\n')
    o2.write(str(classification_report(testP_label, predictedTestP)) + '\n\n\n')

    o2.write('TestW\nTotal accuracy: {}\nQuadratic kappa score: {}\n\n'.format(weightAvgTestW,quadraticKappaScoreTestW))
    o2.write('Confusion matrix:\n')
    o2.write(str(confusion_matrix(testW_label, predictedTestW)) + '\n')
    o2.write(str(classification_report(testW_label, predictedTestW)) + '\n\n\n')
    o2.close()


fopData='../../../dataPapers/'
fopTextSPOC=fopData+'textInSPOC/'
fpPseudoCodeData=fopTextSPOC+'combinePseudoCode.txt'
fpFuncDeclData=fopTextSPOC+'statementLabelFromCode.txt'
fpCodeData=fopTextSPOC+'combineProgram.txt'
fpCsvData=fopTextSPOC+'funcDecl_train.csv'
fpTxtData=fopTextSPOC+'funcDeclLabel_train.txt'

fpPseudoCodeDataTestP=fopTextSPOC+'combinePseudoCode_TestP.txt'
fpFuncDeclDataTestP=fopTextSPOC+'statementLabelFromCode_TestP.txt'
fpCodeDataTestP=fopTextSPOC+'combineProgram_TestP.txt'
fpCsvDataTestP=fopTextSPOC+'funcDecl_testP.csv'
fpTxtDataTestP=fopTextSPOC+'funcDeclLabel_testP.txt'

fpPseudoCodeDataTestW=fopTextSPOC+'combinePseudoCode_TestW.txt'
fpFuncDeclDataTestW=fopTextSPOC+'statementLabelFromCode_TestW.txt'
fpCodeDataTestW=fopTextSPOC+'combineProgram_TestW.txt'
fpCsvDataTestW=fopTextSPOC+'funcDecl_testW.csv'
fpTxtDataTestW=fopTextSPOC+'funcDeclLabel_testW.txt'

fopMLResult=fopTextSPOC+'MLResults/fundecl_v1/'
createDirIfNotExist(fopMLResult)

prepareTrainingDataAndLabel(fpPseudoCodeData,fpFuncDeclData,fpCodeData,fpCsvData,fpTxtData)
prepareTrainingDataAndLabel(fpPseudoCodeDataTestP,fpFuncDeclDataTestP,fpCodeDataTestP,fpCsvDataTestP,fpTxtDataTestP)
prepareTrainingDataAndLabel(fpPseudoCodeDataTestW,fpFuncDeclDataTestW,fpCodeDataTestW,fpCsvDataTestW,fpTxtDataTestW)
runMLAlgm(fpCsvData,fpCsvDataTestP,fpCsvDataTestW,fopMLResult)














