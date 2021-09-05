import glob
import sys, os
import operator,traceback
import shutil
import json

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser
from LibForGraphExtractionFromMixCode import getJsonDict
import ast

def exportListOfLineTerminal(jsonObject,dictLine,arrCodes):
    try:
        if 'children' in jsonObject.keys():
            children=jsonObject['children']
            for i in range(0,len(children)):
                exportListOfLineTerminal(children[i],dictLine,arrCodes)
        else:
            startLine=jsonObject['startLine']
            startOffset = jsonObject['startOffset']
            endLine = jsonObject['endLine']
            endOffset = jsonObject['endOffset']

            if startLine==endLine:
                strContent=arrCodes[startLine][startOffset:endOffset]
                if startLine not in dictLine.keys():
                    dictLine[startLine]=[]
                dictLine[startLine].append(strContent)
            else:
                for i in range(startLine,endLine):
                    if i!= endLine:
                        strLine=arrCodes[i]
                        strContent=strLine.substring(startOffset,len(strLine))
                    else:
                        strLine=arrCodes[i]
                        strContent = strLine[0: endOffset]
                    if i not in dictLine.keys():
                        dictLine[i] = []
                    dictLine[i].append(strContent)
    except:
        traceback.print_exc()

fopRoot='../../../../dataPapers/textInSPOC/correctCodeJson/'
fopCodeFile=fopRoot+'step2/'
fopASTFile=fopRoot+'step3_treesitter/'
fopTokASTFile=fopRoot+'step3_tokenize/'
fpLogSuccessAndFailed=fopRoot+'log_step3_tok.txt'
createDirIfNotExist(fopTokASTFile)
f1 = open(fpLogSuccessAndFailed, 'w')
f1.write('')
f1.close()

lstFpCodes=glob.glob(fopCodeFile+'**/*_code.cpp',recursive=True)
for i in range(0,len(lstFpCodes)):
    fnItemCode=os.path.basename(lstFpCodes[i])
    fopItemCode=os.path.dirname(lstFpCodes[i])+'/'
    fnItemAST=fnItemCode.replace('.cpp','_ast.txt')
    fopItemAST=fopItemCode.replace('step2','step3_treesitter')
    fpItemAST=fopItemAST+fnItemAST
    fopItemTokASTFile=fopItemCode.replace('step2','step3_tokenize')
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
        lstAddString = []
        # print('dict line {}'.format(dictLine))
        for j in range(0,len(arrCodes)):
            strItemLine=arrCodes[j]
            numTabs=0
            if j<33:
                lstNewCodes.append(strItemLine)
                continue

            for k in range(0,len(strItemLine)):
                if strItemLine[k]=='t':
                    numTabs=numTabs+1
                    lstAddString.append('\t')
                else:
                    break
            if j in dictLine.keys():
                strCodeContent=' '.join(dictLine[j])
                lstAddString.append(strCodeContent)
            else:
                lstDisappear.append(str(j))
            lstNewCodes.append(''.join(lstAddString))

        strLineLog=''
        if len(lstDisappear)==0:
            strLineLog='OK'
        else:
            strLineLog='{}\t{}'.format('Fail',' '.join(lstDisappear))

        print('{}\t{}\t{}\t{}'.format(i,fopItemAST,fnItemAST,strLineLog))
        f1=open(fopItemTokASTFile+fnItemAST,'w')
        f1.write('\n'.join(lstNewCodes))
        f1.close()
        f1 = open(fpLogSuccessAndFailed, 'a')
        f1.write(strLineLog+'\n')
        f1.close()
    except:
        traceback.print_exc()




