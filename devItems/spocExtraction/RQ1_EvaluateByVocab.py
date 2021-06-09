from nltk.parse import stanford
from nltk.tree import Tree
import json
import os
import sys
import glob
# os.environ['STANFORD_PARSER'] = '../../../dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
# os.environ['STANFORD_MODELS'] = '../../../dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult,getGraphDependencyFromText
import re
import operator

distanceInRange=33



def evaluateDetectVarByVocabulary(fpPSPreprocessTestP,fpPSPreprocessTestW,fpVarInfoTrain,fpVarInfoTestP,fpVarInfoTestW,fpResultTestP,fpResultTestW,fpResultDetailsTotal,fpDictLiterals,fpDictVarsInTraining):
    f1 = open(fpPSPreprocessTestP, 'r')
    strPseudoCodes = f1.read()
    arrPseudoCodes = strPseudoCodes.strip().split('\n')
    f1.close()
    dictPseudoCodesTestP = {}
    currentKey = ''
    for i in range(0, len(arrPseudoCodes)):
        strStripItem = arrPseudoCodes[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_text.txt'):
            strKey = strStripItem.replace('_text.txt', '')
            lstItem = []
            dictPseudoCodesTestP[strKey] = lstItem
            currentKey = strKey
        elif currentKey in dictPseudoCodesTestP.keys():
            lstItem = dictPseudoCodesTestP[currentKey]
            lstItem.append(strStripItem)

    f1 = open(fpPSPreprocessTestW, 'r')
    strPseudoCodes = f1.read()
    arrPseudoCodes = strPseudoCodes.strip().split('\n')
    f1.close()
    dictPseudoCodesTestW = {}
    currentKey = ''
    for i in range(0, len(arrPseudoCodes)):
        strStripItem = arrPseudoCodes[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_text.txt'):
            strKey = strStripItem.replace('_text.txt', '')
            lstItem = []
            dictPseudoCodesTestW[strKey] = lstItem
            currentKey = strKey
        elif currentKey in dictPseudoCodesTestW.keys():
            lstItem = dictPseudoCodesTestW[currentKey]
            lstItem.append(strStripItem)

    f1 = open(fpVarInfoTrain, 'r')
    strVarInfo = f1.read()
    arrVarInfo = strVarInfo.strip().split('\n')
    f1.close()
    currentKey = ''
    dictVarsInTraining={}
    setOfVarsInTraining=[]
    dictCountVarsInTraining={}
    for i in range(0, len(arrVarInfo)):
        strStripItem = arrVarInfo[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_code.cpp'):
            strKey = strStripItem.replace('_code.cpp', '')
            dictLineAndVar={}
            dictVarsInTraining[strKey] = dictLineAndVar
            currentKey = strKey
            # print('go here')
        elif currentKey in dictVarsInTraining.keys():
            dictLineAndVar = dictVarsInTraining[currentKey]
            arrStripItem=strStripItem.split('\t')
            if (len(arrStripItem)>=3):
                # print('go here')
                if not arrStripItem[1].endswith('Literal'):
                    if not arrStripItem[0] in dictLineAndVar.keys():
                        dictLineAndVar[arrStripItem[0]]=[]
                    else:
                        setOfVarsInTraining.append(arrStripItem[2])
                        if not arrStripItem[2] in dictCountVarsInTraining.keys():
                            dictCountVarsInTraining[arrStripItem[2]]=1
                        else:
                            dictCountVarsInTraining[arrStripItem[2]] =dictCountVarsInTraining[arrStripItem[2]]+ 1
                        dictLineAndVar[arrStripItem[0]].append(arrStripItem[2])
    setOfVarsInTraining=set(setOfVarsInTraining)
    print('train var info {} {}'.format(len(dictVarsInTraining.keys()),len(setOfVarsInTraining)))

    listSorted=sorted(dictCountVarsInTraining.items(), key=operator.itemgetter(1),reverse=True)
    lstStr=[]
    for key in listSorted:
        strItem='{}\t{}'.format(key,dictCountVarsInTraining[key])
        lstStr.append(strItem)

    f1=open(fpDictVarsInTraining,'w')
    f1.write('\n'.join(lstStr))
    f1.close()


    f1 = open(fpVarInfoTestP, 'r')
    strVarInfo = f1.read()
    arrVarInfo = strVarInfo.strip().split('\n')
    f1.close()
    currentKey = ''
    dictVarsInTestP={}
    for i in range(0, len(arrVarInfo)):
        strStripItem = arrVarInfo[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_code.cpp'):
            strKey = strStripItem.replace('_code.cpp', '')
            dictLineAndVar={}
            dictVarsInTestP[strKey] = dictLineAndVar
            currentKey = strKey
        elif currentKey in dictVarsInTestP.keys():
            dictLineAndVar = dictVarsInTestP[currentKey]
            arrStripItem=strStripItem.split('\t')
            if (len(arrStripItem)>=3):
                if not arrStripItem[1].endswith('Literal'):
                    if not arrStripItem[0] in dictLineAndVar.keys():
                        dictLineAndVar[arrStripItem[0]]=[]
                    else:
                        dictLineAndVar[arrStripItem[0]].append(arrStripItem[2])

    f1 = open(fpVarInfoTestW, 'r')
    strVarInfo = f1.read()
    arrVarInfo = strVarInfo.strip().split('\n')
    f1.close()
    currentKey = ''
    dictVarsInTestW={}
    for i in range(0, len(arrVarInfo)):
        strStripItem = arrVarInfo[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_code.cpp'):
            strKey = strStripItem.replace('_code.cpp', '')
            dictLineAndVar={}
            dictVarsInTestW[strKey] = dictLineAndVar
            currentKey = strKey
        elif currentKey in dictVarsInTestW.keys():
            dictLineAndVar = dictVarsInTestW[currentKey]
            arrStripItem=strStripItem.split('\t')
            if (len(arrStripItem)>=3):
                if not arrStripItem[1].endswith('Literal'):
                    if not arrStripItem[0] in dictLineAndVar.keys():
                        dictLineAndVar[arrStripItem[0]]=[]
                    else:
                        dictLineAndVar[arrStripItem[0]].append(arrStripItem[2])


    f1 = open(fpResultDetailsTotal, 'w')
    f1.write('')
    f1.close()

#    evaluate TestP
    lstKeysTest=dictPseudoCodesTestP.keys()
    dictResultForTest={}
    for key in lstKeysTest:
        arrPseudoCodes=dictPseudoCodesTestP[key]
        if not key in dictVarsInTestP.keys():
            continue
        dictVarInfoItems=dictVarsInTestP[key]
        lstResultItem=[]
        print(key)
        for indexPSLine in range(len(arrPseudoCodes)):
            strPSLine=arrPseudoCodes[indexPSLine]
            arrPSTokens=strPSLine.split()

#            list of expected varName in code
            strIndexInRealFile=str((indexPSLine+34))

            if strIndexInRealFile in dictVarInfoItems.keys():
                setVarInCode=set(dictVarInfoItems[strIndexInRealFile])
                setExpectedVarInPS=[]
                numTP = 0
                numTN = 0
                numFP = 0
                numFN = 0
                listTP=[]
                listFP = []
                listTN = []
                listFN = []
                for idxToken in range(len(arrPSTokens)):
                    token = arrPSTokens[idxToken]

                    if token in setVarInCode:
                        setExpectedVarInPS.append(token)

                    if token in setVarInCode and token in setOfVarsInTraining:
                        numTP = numTP + 1
                        listTP.append(token)
                    elif (not token in setVarInCode) and (token in setOfVarsInTraining):
                        numFP = numFP + 1
                        listFP.append(token)
                    elif (token in setVarInCode) and (not token in setOfVarsInTraining):
                        numFN = numFN + 1
                        listFN.append(token)
                    else:
                        numTN = numTN + 1
                        listTN.append(token)
                        # setExpectedVarInPS.append(token)
                        # countExpectedVars=countExpectedVars+1
                        # if token in setOfVarsInTraining:
                        #     numDetectCorrectVars=numDetectCorrectVars+1
                        #     setPredictedVarInPS.append(token)
                strExpectedVarsInPS = str(list(set(setExpectedVarInPS)))
                strSetOfVarsInTraining = str(list(setVarInCode))
                strTP = str(listTP)
                strFP = str(listFP)
                strTN = str(listTN)
                strFN = str(listFN)
                prec = 0
                rec = 0
                if (numTP + numFP) > 0:
                    prec = numTP * 1.0 / (numTP + numFP)
                if (numTP + numFN) > 0:
                    rec = numTP * 1.0 / (numTP + numFN)
                strLineItem = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format((indexPSLine + 1), numTP,
                                                                                          numFP, numTN, numFN, prec,
                                                                                          rec, strExpectedVarsInPS,
                                                                                          strSetOfVarsInTraining, strTP,
                                                                                          strFP, strTN, strFN)
                lstResultItem.append(strLineItem)
        dictResultForTest[key]=lstResultItem


    numTotalTP = 0
    numTotalTN = 0
    numTotalFP = 0
    numTotalFN = 0
    f1 = open(fpResultTestP, 'w')
    f1.write('')
    f1.close()
    for key in dictResultForTest.keys():
        strHead=key+'_text.txt'
        lstItem=[]
        lstItem.append(strHead)
        # print(strHead)

        lstVal=dictResultForTest[key]
        for val in lstVal:
            lstItem.append(val)
            arrVal=val.split('\t')
            if len(arrVal)>=5:
                numTotalTP=numTotalTP+int(arrVal[1])
                numTotalFP=numTotalFP+int(arrVal[2])
                numTotalTN = numTotalTN + int(arrVal[3])
                numTotalFN = numTotalFN + int(arrVal[4])

        lstItem.append('\n\n\n')
        f1 = open(fpResultTestP, 'a')
        f1.write('\n'.join(lstItem))
        f1.close()

    prec=numTotalTP*1.0/(numTotalTP+numTotalFP)
    rec=numTotalTP*1.0/(numTotalTP+numTotalFN)
    strTestResult='TestP accuracy (prec/rec/TP/FP/TN/FN): {}\t{}\t{}\t{}\t{}\t{}\n'.format(prec,rec,numTotalTP,numTotalFP,numTotalTN,numTotalFN)
    f1=open(fpResultDetailsTotal,'a')
    f1.write(strTestResult)
    f1.close()

#    evaluate TestW
    lstKeysTest=dictPseudoCodesTestW.keys()
    dictResultForTest={}
    for key in lstKeysTest:
        arrPseudoCodes=dictPseudoCodesTestW[key]
        if not key in dictVarsInTestW.keys():
            continue
        dictVarInfoItems=dictVarsInTestW[key]
        lstResultItem=[]
        print(key)
        for indexPSLine in range(len(arrPseudoCodes)):
            strPSLine=arrPseudoCodes[indexPSLine]
            arrPSTokens=strPSLine.split()

#            list of expected varName in code
            strIndexInRealFile=str((indexPSLine+34))

            if strIndexInRealFile in dictVarInfoItems.keys():
                setVarInCode=set(dictVarInfoItems[strIndexInRealFile])
                setExpectedVarInPS=[]
                numTP = 0
                numTN = 0
                numFP = 0
                numFN = 0
                listTP=[]
                listFP = []
                listTN = []
                listFN = []
                for idxToken in range(len(arrPSTokens)):
                    token = arrPSTokens[idxToken]

                    if token in setVarInCode:
                        setExpectedVarInPS.append(token)

                    if token in setVarInCode and token in setOfVarsInTraining:
                        numTP = numTP + 1
                        listTP.append(token)
                    elif (not token in setVarInCode) and (token in setOfVarsInTraining):
                        numFP = numFP + 1
                        listFP.append(token)
                    elif (token in setVarInCode) and (not token in setOfVarsInTraining):
                        numFN = numFN + 1
                        listFN.append(token)
                    else:
                        numTN = numTN + 1
                        listTN.append(token)
                        # setExpectedVarInPS.append(token)
                        # countExpectedVars=countExpectedVars+1
                        # if token in setOfVarsInTraining:
                        #     numDetectCorrectVars=numDetectCorrectVars+1
                        #     setPredictedVarInPS.append(token)
                strExpectedVarsInPS = str(list(set(setExpectedVarInPS)))
                strSetOfVarsInTraining = str(list(setVarInCode))
                strTP = str(listTP)
                strFP = str(listFP)
                strTN = str(listTN)
                strFN = str(listFN)
                prec=0
                rec=0
                if (numTP + numFP)>0:
                    prec = numTP * 1.0 / (numTP + numFP)
                if (numTP + numFN)>0:
                    rec = numTP * 1.0 / (numTP + numFN)
                strLineItem = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format((indexPSLine + 1), numTP, numFP, numTN, numFN,prec,rec,strExpectedVarsInPS,strSetOfVarsInTraining,strTP,strFP,strTN,strFN)
                lstResultItem.append(strLineItem)
        dictResultForTest[key]=lstResultItem

    numTotalTP = 0
    numTotalTN = 0
    numTotalFP = 0
    numTotalFN = 0
    f1 = open(fpResultTestW, 'w')
    f1.write('')
    f1.close()
    for key in dictResultForTest.keys():
        strHead = key + '_text.txt'
        lstItem = []
        lstItem.append(strHead)
        # print(strHead)

        lstVal = dictResultForTest[key]
        for val in lstVal:
            lstItem.append(val)
            arrVal = val.split('\t')
            if len(arrVal) >= 5:
                numTotalTP = numTotalTP + int(arrVal[1])
                numTotalFP = numTotalFP + int(arrVal[2])
                numTotalTN = numTotalTN + int(arrVal[3])
                numTotalFN = numTotalFN + int(arrVal[4])

        lstItem.append('\n\n\n')
        f1 = open(fpResultTestW, 'a')
        f1.write('\n'.join(lstItem))
        f1.close()

    prec = numTotalTP * 1.0 / (numTotalTP + numTotalFP)
    rec = numTotalTP * 1.0 / (numTotalTP + numTotalFN)
    strTestResult = 'TestW accuracy (prec/rec/TP/FP/TN/FN): {}\t{}\t{}\t{}\t{}\t{}\n'.format(prec, rec, numTotalTP,
                                                                                                 numTotalFP, numTotalTN,
                                                                                                 numTotalFN)
    f1 = open(fpResultDetailsTotal, 'a')
    f1.write(strTestResult)
    f1.close()


fopData='../../../dataPapers/textInSPOC/'
fpPSPreprocessTrain=fopData+'ps_preprocess_Train.txt'
fpPSPreprocessTestP=fopData+'ps_preprocess_TestP.txt'
fpPSPreprocessTestW=fopData+'ps_preprocess_TestW.txt'
fopVarInfo=fopData+'varInfo/'
createDirIfNotExist(fopVarInfo)
fpVarInfoTrain=fopVarInfo+ 'varInfo_Train.txt'
fpVarInfoTestP=fopVarInfo+ 'varInfo_TestP.txt'
fpVarInfoTestW=fopVarInfo+ 'varInfo_TestW.txt'
fpDictLiterals=fopData+'ps_preprocess_dictLiterals.txt'
fpDictVars=fopData+'ps_preprocess_dictVars.txt'
fpResultTestP=fopData+'rq1_result_TestP.txt'
fpResultTestW=fopData+'rq1_result_TestW.txt'
fpResultDetailsTotal=fopData+'rq1_result_details.txt'


evaluateDetectVarByVocabulary(fpPSPreprocessTestP,fpPSPreprocessTestW,fpVarInfoTrain,fpVarInfoTestP,fpVarInfoTestW,fpResultTestP,fpResultTestW,fpResultDetailsTotal,fpDictLiterals,fpDictVars)
#











