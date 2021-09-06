import glob
import sys, os
import operator,traceback
import shutil
import json
# 10_819A_45107109_code
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser
from LibForGraphExtractionFromRawCode import getJsonDict
import ast
import re

def exportListOfLineTerminal(jsonObject,dictLine,arrCodes):
    try:
        startLine = jsonObject['startLine']
        startOffset = jsonObject['startOffset']
        endLine = jsonObject['endLine']
        endOffset = jsonObject['endOffset']
        strType = jsonObject['type']

        if strType.endswith('literal') and startLine==endLine:
            strContent=arrCodes[startLine][startOffset:endOffset]
            if startLine not in dictLine.keys():
                dictLine[startLine]=[]
            dictLine[startLine].append(strContent)
                # if strType=='char_literal':
                #     print('check char literal {}\n{}\n{}--{}--{}'.format(arrCodes[startLine],strContent,startLine,startOffset,endOffset))
        elif 'children' in jsonObject.keys():
            children=jsonObject['children']
            for i in range(0,len(children)):
                exportListOfLineTerminal(children[i],dictLine,arrCodes)
        else:
            # startLine=jsonObject['startLine']
            # startOffset = jsonObject['startOffset']
            # endLine = jsonObject['endLine']
            # endOffset = jsonObject['endOffset']
            # strType=jsonObject['type']
            # print(strType)
            # if strType == 'char_literal':
            #     print('{}---{}'.format(startLine,endLine))

            if startLine==endLine:
                strContent=arrCodes[startLine][startOffset:endOffset]
                if startLine not in dictLine.keys():
                    dictLine[startLine]=[]
                dictLine[startLine].append(strContent)
                # if strType=='char_literal':
                #     print('check char literal {}\n{}\n{}--{}--{}'.format(arrCodes[startLine],strContent,startLine,startOffset,endOffset))

            else:
                for i in range(startLine,endLine+1):
                    if i!= endLine:
                        strLine=arrCodes[i]
                        strContent=strLine[startOffset:]
                    else:
                        strLine=arrCodes[i]
                        strContent = strLine[0: endOffset]
                    if i not in dictLine.keys():
                        dictLine[i] = []
                    dictLine[i].append(strContent)
    except:
        traceback.print_exc()

def preprocessTextIsnt(strInput):
    strOutput=strInput
    try:
        strOutput=strOutput.replace(" isn ' t "," isn't ").replace(" isn '"," isn't ").replace(" isn  ' "," isn't ")
    except:
        traceback.print_exc()
    return strOutput

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


def preprocessStrLogLiteral(strInput,dictLiterals,dictReverseALs):

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
    strOutput=strOutput.replace('=',' = ').replace('+',' + ').replace('-',' - ').replace('*',' * ').replace('/',' / ').replace('[',' [ ').replace(']',' ] ').replace('{',' { ').replace('}',' } ').replace('(',' ( ').replace(')',' ) ')
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


fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2_pseudo/'
fopASTFile=fopRoot+'step3_pseudo_treesitter/'
fopTokASTFile=fopRoot+'step2_pseudo_tokenize/'
fpLogSuccessAndFailed=fopRoot+'log_step2_pseudo_tok.txt'
fpPseudoAll=fopRoot+'step2_pseudo_all.txt'
fpDictLiteral=fopRoot+'step2_dictLiterals_all.txt'
fpDictRvLiteral=fopRoot+'step2_dictRvLiterals_all.txt'
createDirIfNotExist(fopTokASTFile)
f1 = open(fpLogSuccessAndFailed, 'w')
f1.write('')
f1.close()

f1 = open(fpPseudoAll, 'w')
f1.write('')
f1.close()

dictLiterals={}
dictReverseALs={}


lstFpCodes=glob.glob(fopCodeFile+'**/*_text.txt',recursive=True)
for i in range(0,len(lstFpCodes)):
    fnItemCode=os.path.basename(lstFpCodes[i])
    fopItemCode=os.path.dirname(lstFpCodes[i])+'/'
    fnItemAST=fnItemCode
    fopItemAST=fopItemCode.replace('step2_pseudo','step3_pseudo_treesitter')
    fpItemAST=fopItemAST+fnItemAST
    fopItemTokASTFile=fopItemCode.replace('step2_pseudo','step2_pseudo_tokenize')
    createDirIfNotExist(fopItemTokASTFile)
    isRunOK = False
    try:
        f1=open(lstFpCodes[i],'r')
        arrCodes=f1.read().strip().split('\n')
        f1.close()
        f1=open(fpItemAST,'r')
        arrLines=f1.read().strip().split('\n')
        f1.close()
        strJson=arrLines[1]
        jsonObject=ast.literal_eval(strJson)
        dictLine={}
        exportListOfLineTerminal(jsonObject, dictLine, arrCodes)
        # lstLineIndexes=sorted(dictLine.keys())
        lstDisappear=[]
        lstNewCodes=[]
        lstAbnormalLine=[]

        # print('dict line {}'.format(dictLine))
        for j in range(0,len(arrCodes)):
            strItemLine=arrCodes[j]
            numTabs=0
            # if j<33:
            #     lstNewCodes.append(strItemLine)
            #     continue
            lstAddString = []
            for k in range(0,len(strItemLine)):
                if strItemLine[k]=='\t':
                    numTabs=numTabs+1
                    lstAddString.append('\t')
                else:
                    break
            isLineOK=True
            if j in dictLine.keys():
                strCodeContent=' '.join(dictLine[j])
                lstAddString.append(strCodeContent)
            else:
                isLineOK=False
                lstDisappear.append(str(j))
            strNewCodeContent=''.join(lstAddString)
            strNewCodeContent=preprocessTextIsnt(strNewCodeContent)
            strStripExpected=strItemLine.strip().replace(' ','').replace('\t','')
            strStripTok = strNewCodeContent.strip().replace(' ', '').replace('\t', '')
            if strStripTok != strStripExpected:
                isLineOK=False
                lstAbnormalLine.append(str(j))
            strNewCodeContent=preprocessStrLogLiteral(strNewCodeContent,dictLiterals,dictReverseALs)
            lstNewCodes.append(strNewCodeContent)
            # if isLineOK:
            #     lstNewCodes.append(strNewCodeContent)
            # else:
            #     lstNewCodes.append(arrCodes[j])

        strLineLog=''
        if len(lstDisappear)==0 and len(lstAbnormalLine)==0:
            strLineLog=fopItemTokASTFile+'\t'+fnItemCode+'\tOK'
        else:
            strLineLog='{}\t{}\t{}\tDisappear: {}\tAbnormal: {}'.format(fopItemTokASTFile,fnItemCode,'Fail',' '.join(lstDisappear),' '.join(lstAbnormalLine))

        print('{}\t{}'.format(i,strLineLog))
        strAllNewCode='\n'.join(lstNewCodes)
        f1=open(fopItemTokASTFile+fnItemCode,'w')
        f1.write(strAllNewCode)
        f1.close()
        f1 = open(fpPseudoAll, 'a')
        f1.write('{}\n{}\n\n\n'.format(fopItemTokASTFile+fnItemCode,strAllNewCode))
        f1.close()
        f1 = open(fpLogSuccessAndFailed, 'a')
        f1.write(strLineLog+'\n')
        f1.close()
        # if len(lstDisappear)==0 and len(lstAbnormalLine)==0:
        #     strLineLog=fopItemTokASTFile+'\t'+fnItemAST+'\tOK'
        # else:
        #     input('test ')
    except:
        traceback.print_exc()

lstStr=[]
for key in dictLiterals.keys():
    strItem='{}\t{}'.format(key,dictLiterals[key])
    lstStr.append(strItem)

f1=open(fpDictLiteral,'w')
f1.write('\n'.join(lstStr))
f1.close()



