import glob
import sys, os
import operator,traceback
import shutil
import json
# 10_819A_45107109_code
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser
from LibForGraphExtractionFromRawCode import getJsonDict
import ast

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

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2/'
fopASTFile=fopRoot+'step3_treesitter/'
fopTokASTFile=fopRoot+'step2_tokenize/'
fpLogSuccessAndFailed=fopRoot+'log_step2_tok.txt'
fpLogDictCodeTokens=fopRoot+'log_step2_codeTok.txt'
createDirIfNotExist(fopTokASTFile)
f1 = open(fpLogSuccessAndFailed, 'w')
f1.write('')
f1.close()

lstFpCodes=glob.glob(fopCodeFile+'**/*_code.cpp',recursive=True)
dictCodeTokens={}
for i in range(0,len(lstFpCodes)):
    fnItemCode=os.path.basename(lstFpCodes[i])
    fopItemCode=os.path.dirname(lstFpCodes[i])+'/'
    fnItemAST=fnItemCode.replace('.cpp','_ast.txt')
    fopItemAST=fopItemCode.replace('step2','step3_treesitter')
    fpItemAST=fopItemAST+fnItemAST
    fopItemTokASTFile=fopItemCode.replace('step2','step2_tokenize')
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
            if j<33:
                lstNewCodes.append(strItemLine)
                continue
            lstAddString = []
            for k in range(0,len(strItemLine)):
                if strItemLine[k]=='\t':
                    numTabs=numTabs+1
                    lstAddString.append('\t')
                else:
                    break
            if j in dictLine.keys():
                strCodeContent=' '.join(dictLine[j])
                lstAddString.append(strCodeContent)
            else:
                lstDisappear.append(str(j))
            strNewCodeContent=''.join(lstAddString)

            arrCodeTokens=strNewCodeContent.split()
            for k in range(0,len(arrCodeTokens)):
                if arrCodeTokens[k] not in dictCodeTokens.keys():
                    dictCodeTokens[arrCodeTokens[k]]=0
                else:
                    dictCodeTokens[arrCodeTokens[k]]=dictCodeTokens[arrCodeTokens[k]]+1

            strStripExpected=strItemLine.strip().replace(' ','').replace('\t','')
            strStripTok = strNewCodeContent.strip().replace(' ', '').replace('\t', '')
            if strStripTok != strStripExpected:
                lstAbnormalLine.append(str(j))
            lstNewCodes.append(strNewCodeContent)

        strLineLog=''
        if len(lstDisappear)==0 and len(lstAbnormalLine)==0:
            strLineLog=fopItemTokASTFile+'\t'+fnItemCode+'\tOK'
        else:
            strLineLog='{}\t{}\t{}\tDisappear: {}\tAbnormal: {}'.format(fopItemTokASTFile,fnItemCode,'Fail',' '.join(lstDisappear),' '.join(lstAbnormalLine))

        print('{}\t{}'.format(i,strLineLog))
        f1=open(fopItemTokASTFile+fnItemCode,'w')
        f1.write('\n'.join(lstNewCodes))
        f1.close()
        f1 = open(fpLogSuccessAndFailed, 'a')
        f1.write(strLineLog+'\n')
        f1.close()
        if len(lstDisappear)==0 and len(lstAbnormalLine)==0:
            strLineLog=fopItemTokASTFile+'\t'+fnItemAST+'\tOK'
        # else:
        #     input('test ')
    except:
        traceback.print_exc()

lstStr=[]
for key in sorted(dictCodeTokens.keys()):
    lstStr.append('{}\t{}'.format(key,dictCodeTokens[key]))
f1=open(fpLogDictCodeTokens,'w')
f1.write('\n'.join(lstStr))
f1.close()


