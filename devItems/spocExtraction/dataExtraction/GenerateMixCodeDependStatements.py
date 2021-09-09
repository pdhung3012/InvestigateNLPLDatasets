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
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '

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
        for item in dictLinesAndElements.keys():
            if dictLinesAndElements[item]['children'][0]['type']=='function_definition':
                obj=dictLinesAndElements[item]['children'][0]
                startLine=obj['startLine']
                endLine=obj['endLine']
                tup=(startLine,endLine)
                # print('go here')
                lstTupFunctionDeclarations.append(tup)

        lstPopKeys=[]
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
                # dictLinesAndElements.pop(item, None)
                lstPopKeys.append(item)
                continue
            else:
                dictLinesAndElements[item]['scopeOfMethods']=selectedTup

        for key in lstPopKeys:
            dictLinesAndElements.pop(key, None)
        lstPopKeys=[]
        print('dict after check method scope {}'.format(len(dictLinesAndElements)))

        for item in dictLinesAndElements.keys():
            selectedTup=dictLinesAndElements[item]['scopeOfMethods']
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
            selectItem = lstPossibleStatements[0]
            if len(lstPossibleStatements) == 1:
                selectItem['singleRoot']=True
            else:
                for j in range(1, len(lstPossibleStatements)):
                    candItem = lstPossibleStatements[j]
                    if candItem['startLine'] < selectItem['startLine'] and candItem['endLine'] > selectItem['endLine']:
                        selectItem = candItem
                    elif candItem['startLine'] == selectItem['startLine'] and candItem['endLine'] == selectItem[
                        'endLine']:
                        if (candItem['endOffset'] - candItem['startOffset']) > (
                                selectItem['endOffset'] - selectItem['startOffset']):
                            selectItem = candItem
                selectItem['singleRoot'] = False

            # mainStmt = '{}-{}-{}-{}-{}'.format(selectItem['type'], selectItem['startLine'], selectItem['startOffset'],
            #                                    selectItem['endLine'], selectItem['endOffset'])
            dictLinesAndElements[item]['mainStmt'] = selectItem
            selectItem['isReplaceable'] = True

            if (selectItem['startLine']-selectedTup[0]<2) or (selectedTup[1] -selectItem['endLine']<2):
                lstPopKeys.append(item)

        for key in lstPopKeys:
            dictLinesAndElements.pop(key, None)
        lstPopKeys=[]
        print('dict after check replaceable {}'.format(len(dictLinesAndElements)))

        #  select the indent with most isReplaceable items
        dictIndentAndStatements={}
        for key in dictLinesAndElements.keys():
            mainStmt=dictLinesAndElements[key]['mainStmt']
            indent=mainStmt['indent']
            if indent not in dictIndentAndStatements.keys():
                dictIndentAndStatements[indent]=1
            else:
                dictIndentAndStatements[indent]=dictIndentAndStatements[indent]+1
        dictIndentAndStatements = dict(sorted(dictIndentAndStatements.items(), key=operator.itemgetter(1), reverse=True))
        print('indent {}'.format(dictIndentAndStatements))
        if len(dictIndentAndStatements.keys())>0:
            for key in lstPopKeys:
                dictLinesAndElements.pop(key,None)
            highestIndent=list(dictIndentAndStatements.keys())[0]
            for key in dictLinesAndElements.keys():
                mainStmt = dictLinesAndElements[key]['mainStmt']
                indent = mainStmt['indent']
                if indent!=highestIndent:
                    lstPopKeys.append(key)
                    # dictLinesAndElements.pop(key,None)
        for key in lstPopKeys:
            dictLinesAndElements.pop(key,None)
        lstPopKeys=[]
        print('dict after indent selection {}'.format(len(dictLinesAndElements)))
    except:
        traceback.print_exc()

def generateMixVersionsAndLabels(dictLinesAndElements,arrCodes,arrPseudos,fopCodeVersion,fonameItemAST,idCode):
    try:
        isOK=False
        indexVersion=0
        fpItemPseudo=fopCodeVersion+'_a_pseudo.txt'
        fpItemCode=fopCodeVersion+'_a_code.cpp'
        f1=open(fpItemPseudo,'w')
        f1.write('\n'.join(arrPseudos))
        f1.close()
        f1=open(fpItemCode,'w')
        f1.write('\n'.join(arrCodes))
        f1.close()

        for keyItem in dictLinesAndElements.keys():
            valItem=dictLinesAndElements[keyItem]
            indexVersion=indexVersion+1
            fpItemVersionCode=fopCodeVersion+'v_{}'.format(indexVersion)+'_mix.cpp'
            fpItemVersionLabel = fopCodeVersion + 'v_{}'.format(indexVersion) + '_label.txt'
            mainStmt = valItem['mainStmt']
            startLineMainStmt=mainStmt['startLine']
            endLineMainStmt = mainStmt['endLine']

            lstPseudoLines=range(startLineMainStmt-distanceHeader,endLineMainStmt-distanceHeader+1)
            lstStrPseudoLines=[]
            for it in lstPseudoLines:
                lstStrPseudoLines.append(arrPseudos[it])

            strTotalComment='// '+' , then '.join(lstStrPseudoLines)

            lstMixCodes = []
            for i in range(0,len(arrCodes)):
                itemLine=arrCodes[i]
                numTabs=0
                strLineAdd=arrCodes[i]

                if (i-distanceHeader) in lstPseudoLines:
                    lstStrs = []
                    while(itemLine[numTabs]=='\t'):
                        numTabs=numTabs+1
                        lstStrs.append('\t')
                        if numTabs == len(itemLine):
                            break
                    if i == startLineMainStmt:
                        strLineAdd='{}{}'.format(lstStrs,strTotalComment)
                    else:
                        strLineAdd = '{}{}'.format(lstStrs, '//')
                lstMixCodes.append(strLineAdd)
            f1=open(fpItemVersionCode,'w')
            f1.write('\n'.join(lstMixCodes))
            f1.close()

            strMainStatement=mainStmt['type']
            strPosition='{}-{}-{}-{}'.format(mainStmt['startLine'],mainStmt['startOffset'],mainStmt['endLine'],mainStmt['endOffset'])
            numOfLine=endLineMainStmt-startLineMainStmt+1
            numOfStatements=0
            lstListOfBelowStatements=[]
            strDictToString=''
            if mainStmt['singleRoot']:
                numOfStatements=1
                lstListOfBelowStatements.append(mainStmt['type'])
                if 'children' in mainStmt.keys():
                    for child in mainStmt['children']:
                        if 'isReplaceable' in child.keys() and child['isReplaceable']:
                            strStmtChild=child['type']
                            numOfStatements=numOfStatements+1
                            lstListOfBelowStatements.append(strStmtChild)
                strDictToString=str(mainStmt)
            else:
                indentDeepest = sorted(dictLinesAndElements[keyItem]['sortedElementsByIndents'].keys())[0]
                lstPossibleStatements = dictLinesAndElements[keyItem]['sortedElementsByIndents'][indentDeepest]
                numOfStatements=len(lstPossibleStatements)
                for stmt in lstPossibleStatements:
                    lstListOfBelowStatements.append(stmt['type'])
                strDictToString =strSplitJson.join(map(str,lstPossibleStatements))
            strBelowStatements=strStmtSplit.join(lstListOfBelowStatements)

            f1=open(fpItemVersionLabel,'w')
            strLbl='{}\n{}\n{}\n{}\n{}\{}'.format(strMainStatement,strPosition,numOfLine,numOfStatements,strBelowStatements,strDictToString)
            f1.close()
    except:
        traceback.print_exc()

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2_tokenize/'
fopPseudoFile=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopLabels=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopMixVersion=fopRoot+'step4_mixCode/'
createDirIfNotExist(fopMixVersion)

lstFpDictASTs=glob.glob(fopTreeSitterFile+'**/*_code_ast.txt',recursive=True)
distanceHeader=33

if os.path.isdir(fopMixVersion):
    shutil.rmtree(fopMixVersion)

for i in range(0,len(lstFpDictASTs)):
    fpItemAST=lstFpDictASTs[i]
    fnItemAST=os.path.basename(fpItemAST)
    fopItemAST=os.path.dirname(fpItemAST)
    fonameItemAST=os.path.basename(fopItemAST)
    try:
        idCode=fnItemAST.replace('_code_ast.txt','')
        fpItemPseudo=fopPseudoFile+fonameItemAST+'/'+idCode+'_text.txt'
        fpItemCode = fopCodeFile + fonameItemAST+'/' + idCode + '_code.cpp'
        fopCodeVersion=fopMixVersion+fonameItemAST+'/'+idCode+'/'
        if os.path.isdir(fopCodeVersion):
            shutil.rmtree(fopCodeVersion)
        createDirIfNotExist(fopCodeVersion)
        fnLogOutput='a_logPrint.txt'
        fpCodeLogOutput=fopCodeVersion+fnLogOutput

        sys.stdout = open(fpCodeLogOutput, 'w')
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
        print('dict before {}'.format(len(dictLinesAndElements.keys())))
        findReplaceableStatements(dictLinesAndElements, lstTupFunctionDeclarations)
        print('dict after {}'.format(len(dictLinesAndElements.keys())))
        print('dict final content\n{}'.format(dictLinesAndElements))
        generateMixVersionsAndLabels(dictLinesAndElements,arrCodes,arrPseudos,fopCodeVersion,fonameItemAST,idCode)

        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print('end {}/{} {}'.format(i,len(lstFpDictASTs),fpCodeLogOutput))

    except:
        traceback.print_exc()