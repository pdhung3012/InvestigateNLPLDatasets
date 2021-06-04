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

distanceLine=33

def preprocessStr(strInput):
    strOutput=strInput.replace('[',' [ ').replace(']',' ] ').replace('{',' { ').replace('}',' } ').replace('(',' ( ').replace(')',' ) ').replace('.',' . ')
    return strOutput

def findLineNumber(jsonObj):
    line=-1
    isGetLineInformation=False
    try:
        line=jsonObj['loc']['line']
        isGetLineInformation=True
    except:
        isGetLineInformation=False
    if not isGetLineInformation:
        try:
            line = jsonObj['range']['begin']['line']
            isGetLineInformation = True
        except:
            isGetLineInformation = False
    return line

def getProperty(jsonObj,key):
    isSuccess=False
    childObj=None
    try:
        childObj = jsonObj[key]
        isSuccess=True
    except:
        isSuccess=False
    return childObj

def parseContentOfTree(jsonObj,currentlineNumber,dictLines):
    newLineNumber=findLineNumber(jsonObj)
    if(newLineNumber>0):
        currentlineNumber=newLineNumber

    strKind=getProperty(jsonObj,'kind')
    itemTupleToAdd=()
    if (not strKind is None):
        if strKind.endswith('Literal'):
            itemTupleToAdd+=(strKind,)
            itemTupleToAdd+=(getProperty(jsonObj,'value'),)
            try:
                itemTupleToAdd += (jsonObj['type']['qualType'],)
            except:
                print('error get type of literal')
        elif strKind =='VarDecl':
            itemTupleToAdd += ( strKind,)
            itemTupleToAdd += ( getProperty(jsonObj, 'name'),)
            try:
                itemTupleToAdd += ( jsonObj['type']['qualType'],)
            except:
                print('error get type of varDecl')
        else:
            try:
                refObj=getProperty(jsonObj,'referencedDecl')
                if not str(refObj) =='None':
                    itemTupleToAdd += ('referencedDecl',)
                    itemTupleToAdd += (getProperty(refObj,'name'),)
                    itemTupleToAdd += (jsonObj['type']['qualType'],)
            except:
                isRunThrough=False
                # print('error get type of referencedDecl')

        if(len(itemTupleToAdd)>0):
            if not currentlineNumber in dictLines.keys():
                lstItem=[]
                dictLines[currentlineNumber]=lstItem
            dictLines[currentlineNumber].append(itemTupleToAdd)



    arrChildren=getProperty(jsonObj,'inner')
    if isinstance(arrChildren,list):
        for childObj in arrChildren:
            parseContentOfTree(childObj,currentlineNumber,dictLines)







def extractVariableAndLiteral(fpPseudoCode,fpPSPreprocess,fopAST,fpVarInfo):
    f1=open(fpPseudoCode,'r')
    strPseudoCodes=f1.read()
    arrPseudoCodes=strPseudoCodes.strip().split('\n')
    f1.close()

    lstPrePS=[]
    for i in range(0,len(arrPseudoCodes)):
        strStripItem=arrPseudoCodes[i].strip()
        if strStripItem.endswith('_text.txt'):
            lstPrePS.append(strStripItem)
        else:
            strPre=preprocessStr(strStripItem)
            lstPrePS.append(strPre)

    f1=open(fpPSPreprocess,'w')
    strPS='\n'.join(lstPrePS)
    f1.write(strPS)
    f1.close()

    f1=open(fpPSPreprocess,'r')
    strPseudoCodes=f1.read()
    arrPseudoCodes=strPseudoCodes.strip().split('\n')
    f1.close()
    dictPseudoCodes={}
    currentKey=''
    for i in range(0,len(arrPseudoCodes)):
        strStripItem=arrPseudoCodes[i].strip()
        # print(strStripItem)
        if strStripItem.endswith('_text.txt'):
            strKey=strStripItem.replace('_text.txt','')
            lstItem=[]
            dictPseudoCodes[strKey]=lstItem
            currentKey=strKey
        elif currentKey in dictPseudoCodes.keys():
            lstItem =dictPseudoCodes[currentKey]
            lstItem.append(strStripItem)

    f1=open(fpVarInfo,'w')
    f1.write('')
    f1.close()
    index=0
    for key in dictPseudoCodes.keys():
        fpJsonItem=fopAST+key+'_code.cpp'
        fnKey=key+'_code.cpp'
        index=index+1
        f1=open(fpJsonItem,'r')
        strJsonItem=f1.read()
        f1.close()
        jsonObj=json.loads(strJsonItem)
        dictLines={}
        currentLineNumber=-1
        parseContentOfTree(jsonObj, currentLineNumber, dictLines)

        lstItem=[]
        lstItem.append(fnKey)
        for k in sorted(dictLines.keys()):
            lstItemTuple=dictLines[k]

            for itemTuple in lstItemTuple:
                lstLineStr = []
                lstLineStr.append(str(k))
                for i in range(0,len(itemTuple)):
                    lstLineStr.append(str(itemTuple[i]))
                strItem='\t'.join(lstLineStr)
                lstItem.append(strItem)
        lstItem.append('\n\n\n')
        strAppend='\n'.join(lstItem)
        f1 = open(fpVarInfo, 'a')
        f1.write(strAppend)
        f1.close()

        print('{}\t{} dict {}'.format(index,fnKey,len(dictLines)))


fopData='../../../dataPapers/textInSPOC/'
fopASTTrain=fopData+'trainASTForC/'
fopASTTestP=fopData+'testPASTForC/'
fopASTTestW=fopData+'testWASTForC/'
fpPseudoCodeTrain=fopData+'combinePseudoCode.txt'
fpPseudoCodeTestP=fopData+'combinePseudoCode_TestP.txt'
fpPseudoCodeTestW=fopData+'combinePseudoCode_TestW.txt'
fpPSPreprocessTrain=fopData+'ps_preprocess_Train.txt'
fpPSPreprocessTestP=fopData+'ps_preprocess_TestP.txt'
fpPSPreprocessTestW=fopData+'ps_preprocess_TestW.txt'
fopVarInfo=fopData+'varInfo/'
createDirIfNotExist(fopVarInfo)
fpVarInfoTrain=fopVarInfo+ 'varInfo_Train.txt'
fpVarInfoTestP=fopVarInfo+ 'varInfo_TestP.txt'
fpVarInfoTestW=fopVarInfo+ 'varInfo_TestW.txt'

extractVariableAndLiteral(fpPseudoCodeTrain,fpPSPreprocessTrain,fopASTTrain,fpVarInfoTrain)
extractVariableAndLiteral(fpPseudoCodeTestP,fpPSPreprocessTestP,fopASTTestP,fpVarInfoTestP)
extractVariableAndLiteral(fpPseudoCodeTestW,fpPSPreprocessTestW,fopASTTestW,fpVarInfoTestW)


# lstFiles=sorted(glob.glob(fopASTTrain+ "*_code.cpp"))
# for i in range(0,len(lstFiles)):

