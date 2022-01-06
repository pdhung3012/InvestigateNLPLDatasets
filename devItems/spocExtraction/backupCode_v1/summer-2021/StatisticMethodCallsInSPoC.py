from nltk.parse import stanford
from nltk.tree import Tree
import json
import os
import sys
import glob
# os.environ['STANFORD_PARSER'] = '../../../dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
# os.environ['STANFORD_MODELS'] = '../../../dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult,getGraphDependencyFromText
import re
import operator

def getJsonValueCatchError(jsonObj,listKeys):
    strValue='Error_Val'
    try:
        obj=jsonObj
        for item in listKeys:
            obj=obj[item]
        strValue=obj
    except:
        strValue = 'Error_Val'
        # print('error here')
    return strValue


def traverseJsonObject(jsonObject,dictSum,lstSwapSig):
    strName = getJsonValueCatchError(jsonObject, ['referencedDecl', 'name'])
    strKind = getJsonValueCatchError(jsonObject, ['referencedDecl', 'kind'])
    strQualType = getJsonValueCatchError(jsonObject, ['referencedDecl','type', 'qualType'])
    if strKind =="FunctionDecl":
        arrAfterParen=strQualType.split('(')
        if len(arrAfterParen)>=2:
            listParams=arrAfterParen[1].strip().replace(')','').split(',')
        setParam=set(listParams)
        dictSum['methodRef'] = dictSum['methodRef'] + 1
        if(len(setParam)<len(listParams)):
            isMethodST=True
            dictSum['methodRefSwappable']=dictSum['methodRefSwappable']+1
            lstSwapSig.append('{}\t{}'.format(strName,strQualType))

    if 'inner' in jsonObject:
        arr=jsonObject['inner']
        for item in arr:
            traverseJsonObject(item,dictSum,lstSwapSig)


def calculateMethodCallsAndSameTypeMC(fopAST,dictCountMethodCalls,fpLogMethodCount,fpLogMethodSignature):
    lstFiles = sorted(glob.glob(fopAST + "*_code.cpp"))
    dictCountMethodCalls = {}
    dictCountMethodCalls['methodRefSwappable'] = 0
    dictCountMethodCalls['methodRef'] = 0
    dictCountMethodCalls['countMethods'] = len(lstFiles)
    f1 = open(fpLogMethodSignature, 'w')
    f1.write('')
    f1.close()
    lstSwapSig=[]

    for i in range(0, len(lstFiles)):
        fpItem = lstFiles[i]
        fileNameItem = os.path.basename(lstFiles[i])
        f1 = open(fpItem, 'r')
        strJson = f1.read()
        f1.close()
        jsonObject = json.loads(strJson)
        print('{}\t{}'.format(i,fileNameItem))
        dictLines = {}
        traverseJsonObject(jsonObject, dictCountMethodCalls,lstSwapSig)
        # lstStr = [fileNameItem]
        # print('{}\t{}\t{}'.format(i, fpItem, len(dictLines.keys())))
        # for key in sorted(dictLines.keys()):
        #     lstItem = dictLines[key]
        #     strItem = '{}\t{}'.format(key, ','.join(lstItem))
        #     lstStr.append(strItem)
        # lstStr.append('\n\n\n')
    setSwapSig=set(lstSwapSig)
    sorted(setSwapSig)
    percentageOfMethodSwappable=dictCountMethodCalls['methodRefSwappable']*1.0/dictCountMethodCalls['methodRef']
    ratioMSPerProgram = dictCountMethodCalls['methodRefSwappable'] * 1.0 / dictCountMethodCalls['countMethods']
    strLogInfo='{}\t{}\t{}\t{}\t{}\t{}\n'.format(fopAST,dictCountMethodCalls['methodRefSwappable'],dictCountMethodCalls['methodRef'],dictCountMethodCalls['countMethods'],percentageOfMethodSwappable,ratioMSPerProgram)
    f1=open(fpLogMethodCount,'a')
    f1.write(strLogInfo)
    f1.close()
    f1 = open(fpLogMethodSignature, 'w')
    f1.write('\n'.join(list(setSwapSig)))
    f1.close()

    print('finish')

fopData='../../../dataPapers/textInSPOC/'
fopASTTrain=fopData+'trainASTForC/'
fopASTTestP=fopData+'testPASTForC/'
fopASTTestW=fopData+'testWASTForC/'
fpLogMethodCount=fopData+'logMethodRefCount.txt'
fpLogMethodSignatureTrain=fopData+'logMethodRefSignature_Train.txt'
fpLogMethodSignatureTestP=fopData+'logMethodRefSignature_TestP.txt'
fpLogMethodSignatureTestW=fopData+'logMethodRefSignature_TestW.txt'

dictCountMethodCalls = {}
f1=open(fpLogMethodCount,'w')
strLogInfo='{}\t{}\t{}\t{}\t{}\t{}\n'.format('fopAST','numMethodRefSwappable','numMethodRef','numPrograms','ratioSwappableMethodRefPerMethodRed','ratioSwappableMethodPerProgram')
f1.write(strLogInfo)
f1.close()


calculateMethodCallsAndSameTypeMC(fopASTTestP,dictCountMethodCalls,fpLogMethodCount,fpLogMethodSignatureTestP)
calculateMethodCallsAndSameTypeMC(fopASTTestW,dictCountMethodCalls,fpLogMethodCount,fpLogMethodSignatureTestW)
calculateMethodCallsAndSameTypeMC(fopASTTrain,dictCountMethodCalls,fpLogMethodCount,fpLogMethodSignatureTrain)
