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

def preprocessText(strInput):
    strOutput=strInput
    try:
        strOutput=strOutput.replace("isn '","insn't")
    except:
        traceback.print_exc()
    return strOutput

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2_pseudo/'
fopASTFile=fopRoot+'step3_pseudo_treesitter/'
fopTokASTFile=fopRoot+'step2_pseudo_tokenize/'
fpLogSuccessAndFailed=fopRoot+'log_step2_pseudo_tok.txt'
fpPseudoAll=fopRoot+'step2_pseudo_all.txt'
createDirIfNotExist(fopTokASTFile)
f1 = open(fpLogSuccessAndFailed, 'w')
f1.write('')
f1.close()

f1 = open(fpPseudoAll, 'w')
f1.write('')
f1.close()


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
            if j in dictLine.keys():
                strCodeContent=' '.join(dictLine[j])
                lstAddString.append(strCodeContent)
            else:
                lstDisappear.append(str(j))
            strNewCodeContent=''.join(lstAddString)
            strNewCodeContent=preprocessText(strNewCodeContent)
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




