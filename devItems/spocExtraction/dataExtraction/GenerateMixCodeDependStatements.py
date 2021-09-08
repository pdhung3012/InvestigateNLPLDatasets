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
from LibForGraphExtractionFromRawCode import getJsonDict,getTerminalValue
import ast
import re

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '

def walkJsonAndGetIndent(jsonObject,dictLinesAndElements,indent):
    try:
        # if indent not in dictIndents.keys():
        #     dictIndents[indent]=[]
        jsonObject['indent']=indent
        # dictIndents[indent].append(jsonObject)

        startLine=jsonObject['startLine']
        endLine=jsonObject['endLine']
        strLineOffset='{}-{}'.format(startLine,endLine)
        if strLineOffset not in dictLinesAndElements.keys():
            dictLinesAndElements[strLineOffset]={}
            dictLinesAndElements[strLineOffset]['children']=[jsonObject]
        else:
            dictLinesAndElements[strLineOffset]['children'].append(jsonObject)

        if 'children' in jsonObject.keys():
            lstChildren=jsonObject['children']
            indentChild=indent+1
            for i in range(0,len(lstChildren)):
                walkJsonAndGetIndent(lstChildren[i],dictLinesAndElements,indentChild)
    except:
        traceback.print_exc()

def findReplaceableStatements(dictLinesAndElements,lstTupFunctionDeclarations):
    try:
        # find tuples of method declarations
        for i in range(0,len(dictLinesAndElements.keys)):
            item=dictLinesAndElements.keys()[i]
            if item['type']=='function_definition':
                startLine=item['startLine']
                endLine=item['endLine']
                tup=(startLine,endLine)
                lstTupFunctionDeclarations.append(tup)


        for item in dictLinesAndElements.keys():
            arrStartEnd=item.split('-')
            startLine=int(arrStartEnd[0])
            endLine=int(arrStartEnd[1])
            isInFD=False
            selectedTup=None
            for tup in lstTupFunctionDeclarations:
                if startLine>tup[0] and endLine<tup[1]:
                    isInFD=True
                    selectedTup=tup
                    break

            if not isInFD:
                dictLinesAndElements.pop(item, None)
                continue

            dictLinesAndElements[item]['scopeOfMethods']=selectedTup
            lstChildren = dictLinesAndElements[item]['children']
            dictIndentElements = {}
            for j in range(0, len(lstChildren)):
                itemEleJ = lstChildren[j]
                indIndent = itemEleJ['indent']
                if indIndent not in dictIndentElements.keys():
                    dictIndentElements[indIndent] = [itemEleJ]
                else:
                    dictIndentElements[indIndent].append(itemEleJ)
            dictLinesAndElements[item]['sortedElementsByIndents'] = dictIndentElements
            # main sstatement is the node that is closest to the root. If there are 2 or more nodes in the same deep, we calculate
            indentDeepest = sorted(dictLinesAndElements[item]['sortedElementsByIndents'].keys())[0]
            lstPossibleStatements = dictLinesAndElements[item]['sortedElementsByIndents'][indentDeepest]
            # mainStmt = ''
            if len(lstPossibleStatements) == 1:
                selectItem = lstPossibleStatements[0]
                selectItem['singleRoot']=True

            else:
                selectItem = lstPossibleStatements[0]
                selectItem['singleRoot'] = False
                for j in range(1, len(lstPossibleStatements)):
                    candItem = selectItem[j]
                    if candItem['startLine'] < selectItem['startLine'] and candItem['endLine'] > selectItem['endLine']:
                        selectItem = candItem
                    elif candItem['startLine'] == selectItem['startLine'] and candItem['endLine'] == selectItem[
                        'endLine']:
                        if (candItem['endOffset'] - candItem['startOffset']) > (
                                selectItem['endOffset'] - selectItem['startOffset']):
                            selectItem = candItem
            # mainStmt = '{}-{}-{}-{}-{}'.format(selectItem['type'], selectItem['startLine'], selectItem['startOffset'],
            #                                    selectItem['endLine'], selectItem['endOffset'])
            dictLinesAndElements[item]['mainStmt'] = selectItem
            selectItem['isReplaceable'] = True

            if (selectItem['startLine']-selectedTup[0]>1) and (selectedTup[1] -selectItem['endLine']>1):
                dictLinesAndElements.pop(item,None)

        #  select the indent with most isReplaceable items
        dictIndentAndStatements={}
        for i in range(0,len(dictLinesAndElements.keys)):
            key=dictLinesAndElements.keys()[i]
            mainStmt=dictLinesAndElements[key]['mainStmt']
            indent=mainStmt['indent']
            if indent not in dictIndentAndStatements.keys():
                dictIndentAndStatements[indent]=1
            else:
                dictIndentAndStatements[indent]=dictIndentAndStatements[indent]+1
        dictIndentAndStatements = dict(sorted(dictIndentAndStatements.items(), key=operator.itemgetter(1), reverse=True))
        highestIndent=dictIndentAndStatements.keys()[0]
        for i in range(0,len(dictLinesAndElements.keys)):
            key=dictLinesAndElements.keys()[i]
            mainStmt = dictIndentAndStatements[key]['mainStmt']
            indent = mainStmt['indent']
            if indent!=highestIndent:
                dictLinesAndElements.pop(key,None)
    except:
        traceback.print_exc()

def generateMixVersionsAndLabels(dictLinesAndElements,arrCodes,arrPseudos,fopMixVersion,fonameTrainTest,idCode):
    try:
        isOK=False
    except:
        traceback.print_exc()

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2_tokenize/'
fopPseudoFile=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopLabels=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopMixVersion=fopRoot+'step4_genMixCodePseudocode/'
createDirIfNotExist(fopMixVersion)

lstFpDictASTs=glob.glob(fopTreeSitterFile+'**/*_code_ast.txt',recursive=True)
distanceHeader=33

for i in range(0,len(lstFpDictASTs)):
    fpItemAST=lstFpDictASTs[i]
    fnItemAST=os.path.basename(fpItemAST)
    fopItemAST=os.path.dirname(fpItemAST)
    fonameItemAST=os.path.basename(fopItemAST)
    try:
        idCode=fnItemAST.replace('_code_ast.txt','')
        fpItemPseudo=fopPseudoFile+fonameItemAST+'/'+idCode+'_text.txt'
        fpItemCode = fopCodeFile + fonameItemAST+'/' + idCode + '_code.cpp'
        f1=open(fpItemPseudo,'r')
        arrPseudos=f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemCode, 'r')
        arrCodes = f1.read().strip().split('\n')
        f1.close()
        f1=open(fpItemAST,'r')
        strASTContent=f1.read().strip().split('\n')[1]
        jsonObject = ast.literal_eval(strASTContent)
        dictLinesAndElements={}
        indent=1
        lstTupFunctionDeclarations=[]
        walkJsonAndGetIndent(jsonObject,dictLinesAndElements,indent)
        findReplaceableStatements(dictLinesAndElements, lstTupFunctionDeclarations)
        print('dict {}'.format(dictLinesAndElements))
        generateMixVersionsAndLabels(dictLinesAndElements,arrCodes,arrPseudos,fopMixVersion,fonameItemASTidCode)



    except:
        traceback.print_exc()