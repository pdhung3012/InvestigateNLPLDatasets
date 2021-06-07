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
distanceInRange=33

def evaluateDetectVarByVocabulary(fpPreprocessTest,fpVarInfoTrain,fpVarInfoTest,fpDictLiterals):
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
    for i in range(0, len(arrVarInfo)):
        strStripItem = arrVarInfo[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_text.txt'):
            strKey = strStripItem.replace('_text.txt', '')
            dictLineAndVar={}
            dictVarsInTraining[strKey] = dictLineAndVar
            currentKey = strKey
        elif currentKey in dictVarsInTraining.keys():
            dictLineAndVar = dictVarsInTraining[currentKey]
            arrStripItem=strStripItem.split('\t')
            if (len(arrStripItem)>=3):
                if not arrStripItem[1].endswith('Literal'):
                    if not arrStripItem[0] in dictLineAndVar.keys():
                        dictLineAndVar[arrStripItem[0]]=[]
                    else:
                        dictLineAndVar[arrStripItem[0]].append(arrStripItem[2])

    f1 = open(fpVarInfoTestP, 'r')
    strVarInfo = f1.read()
    arrVarInfo = strVarInfo.strip().split('\n')
    f1.close()
    currentKey = ''
    dictVarsInTestP={}
    for i in range(0, len(arrVarInfo)):
        strStripItem = arrVarInfo[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_text.txt'):
            strKey = strStripItem.replace('_text.txt', '')
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
        if strStripItem.endswith('_text.txt'):
            strKey = strStripItem.replace('_text.txt', '')
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



#    evaluate TestP





