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

distanceLine=33
regexInteger=r'^[-+]?([1-9]\d*|0)$'
re_int=re.compile(regexInteger)
regexFloat=r"""(?x)
   ^
      [+-]?\ *      # first, match an optional sign *and space*
      (             # then match integers or f.p. mantissas:
          \d+       # start out with a ...
          (
              \.\d* # mantissa of the form a.b or a.
          )?        # ? takes care of integers of the form a
         |\.\d+     # mantissa of the form .b
      )
      ([eE][+-]?\d+)?  # finally, optionally match an exponent
   $"""
re_float = re.compile(regexFloat)
# re_float = re.compile("""(?x)
#    ^
#       [+-]?\ *      # first, match an optional sign *and space*
#       (             # then match integers or f.p. mantissas:
#           \d+       # start out with a ...
#           (
#               \.\d* # mantissa of the form a.b or a.
#           )?        # ? takes care of integers of the form a
#          |\.\d+     # mantissa of the form .b
#       )
#       ([eE][+-]?\d+)?  # finally, optionally match an exponent
#    $""")

def preprocessStr(strInput,dictLiterals,dictReverseALs):

    indexOfQuotes=0
    indexLoop=0
    prevElement=''
    lstItemAbt=[]
    lstReplaceStringTuple=[]
    lstStringTotal=[]
    isInQuote=False
    lenBefore=len(dictLiterals.keys())
    for element in strInput:
        if indexLoop>0:
            prevElement=strInput[indexLoop-1]
        if element =='"' and not prevElement =='\\':
            indexOfQuotes = indexOfQuotes + 1

            if indexOfQuotes%2==0:
                isInQuote=False
                lstItemAbt.append('"')
                strItem=''.join(lstItemAbt)
                # print(strItem)
                lenDict=len(dictReverseALs.keys())+1

                if not strItem in dictReverseALs:
                    strId = 'SpecialLiteral_String_{}'.format(lenDict)
                    dictReverseALs[strItem]=strId
                else:
                    strId=dictReverseALs[strItem]
                # if not strId in dictLiterals.keys():
                dictLiterals[strId]=strItem
                lstStringTotal.append(strId)
                # itemTuple=(strId,strItem)
                # print('oke {}'.format(strItem))
                # lstReplaceStringTuple.append(itemTuple)
            else:
                lstItemAbt = []
                lstItemAbt.append('"')
                isInQuote = True
        elif not isInQuote:
            lstStringTotal.append(element)
        else:
            lstItemAbt.append(element)
    lenAfter = len(dictLiterals.keys())
    strOutput=''.join(lstStringTotal)

    arrTokens = strOutput.split()
    lstStringTotal = []
    for token in arrTokens:
        isMatch = re_float.match(token)
        if isMatch:
            lstStringTotal.append(token)
        else:
            newToken=token.replace('.',' . ')
            lstStringTotal.append(newToken)
    strOutput = ' '.join(lstStringTotal)


    # if(lenAfter>lenBefore):
    #     print(strOutput)
    # strOutput=strInput
    # if len(lstReplaceStringTuple)>0:
    #     print('list {}'.format(lstReplaceStringTuple))
    #     for itTu in lstReplaceStringTuple:
    #         endIdx=len(str(itTu[1]))-1
    #         strNoQuote=str(itTu[1])[1:endIdx]
    #         strLiteral='{}{}{}{}{}'.format(chr(92),'"',strNoQuote,chr(92),'"')
    #         strOutput=strOutput.replace(strLiteral,str(itTu[0]))
    #         print('{} aaa {}'.format(strOutput, strLiteral))
    # print(strOutput)
    strOutput=strOutput.replace('[',' [ ').replace(']',' ] ').replace('{',' { ').replace('}',' } ').replace('(',' ( ').replace(')',' ) ')
    # print('Out format {}'.format(strOutput))

    arrTokens=strOutput.split()
    lstStringTotal=[]
    for token in arrTokens:
        isMatch=re_int.match(token)
        if isMatch:
            strNum=token
            lenDict = len(dictReverseALs.keys()) + 1

            if not strNum in dictReverseALs:
                strId = 'SpecialLiteral_IntLong_{}'.format(lenDict)
                dictReverseALs[strNum] = strId
            else:
                strId = dictReverseALs[strNum]
            # print('Num {}'.format(strNum))
            dictLiterals[strId] = strNum
            lstStringTotal.append(strId)
        else:
            lstStringTotal.append(token)
    strOutput=' '.join(lstStringTotal)

    arrTokens = strOutput.split()
    lstStringTotal = []
    for token in arrTokens:
        isMatch = re_float.match(token)
        if isMatch:
            strNum = token
            lenDict = len(dictReverseALs.keys()) + 1

            if not strNum in dictReverseALs:
                strId = 'SpecialLiteral_FloatDouble_{}'.format(lenDict)
                dictReverseALs[strNum] = strId
            else:
                strId = dictReverseALs[strNum]
            # print('Float {}'.format(strNum))
            dictLiterals[strId] = strNum
            lstStringTotal.append(strId)
        else:
            lstStringTotal.append(token)
    strOutput = ' '.join(lstStringTotal)
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







def extractVariableAndLiteral(fpPseudoCode,fpPSPreprocess,fopAST,fpVarInfo,dictAbstractLiterals,dictReverseALs):
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
            strPre=preprocessStr(strStripItem,dictAbstractLiterals,dictReverseALs)
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
fpDictLiterals=fopData+'ps_preprocess_dictLiterals.txt'

dictAbstractLiterals={}
dictReverseALs={}
extractVariableAndLiteral(fpPseudoCodeTrain,fpPSPreprocessTrain,fopASTTrain,fpVarInfoTrain,dictAbstractLiterals,dictReverseALs)
extractVariableAndLiteral(fpPseudoCodeTestP,fpPSPreprocessTestP,fopASTTestP,fpVarInfoTestP,dictAbstractLiterals,dictReverseALs)
extractVariableAndLiteral(fpPseudoCodeTestW,fpPSPreprocessTestW,fopASTTestW,fpVarInfoTestW,dictAbstractLiterals,dictReverseALs)

lstStr=[]
for key in dictAbstractLiterals.keys():
    strItem='{}\t{}'.format(key,dictAbstractLiterals[key])
    lstStr.append(strItem)

f1=open(fpDictLiterals,'w')
f1.write('\n'.join(lstStr))
f1.close()



# lstFiles=sorted(glob.glob(fopASTTrain+ "*_code.cpp"))
# for i in range(0,len(lstFiles)):

