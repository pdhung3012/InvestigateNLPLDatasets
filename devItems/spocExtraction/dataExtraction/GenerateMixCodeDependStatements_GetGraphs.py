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
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render

strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '

def generateGraph(jsonObject,strFatherLabel,arrCodes,idChange,isBlueColor,graph):
    startLine=jsonObject['startLine']
    startOffset=jsonObject['startOffset']
    endLine=jsonObject['endLine']
    endOffset=jsonObject['endOffset']
    strPosition='{}-{}-{}-{}'.format(startLine,startOffset,endLine,endOffset)
    strId=str(jsonObject['id'])
    strLabel='{}\n{}\n{}'.format(strId,strPosition,jsonObject['type'])
    # strLabel = '{}\n{}'.format(strId, jsonObject['type'])

    if isBlueColor and strId!=idChange:
        graph.add_node(strLabel, color='blue')
    else:
        graph.add_node(strLabel, color='red')

    if 'children' in jsonObject.keys():
        lstChildren=jsonObject['children']
        for i in range(0,len(lstChildren)):
            if strId == idChange:
                # print('id and idchange {} {}'.format(strId, idChange))
                isBlueColor = False
            strChildLabel=generateGraph(lstChildren[i],strLabel,arrCodes,idChange, isBlueColor, graph)
            if strLabel!=strChildLabel:
                graph.add_edge(strLabel,strChildLabel,color='black')
    else:
        strTerminalLabel='-2\n{}\n{}'.format(strPosition,getTerminalValue(startLine,startOffset,endLine,endOffset,arrCodes))
        graph.add_node(strTerminalLabel, color='yellow')
        graph.add_edge(strLabel, strTerminalLabel, color='black')

    return strLabel



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

def walkAndFindErrorInsideObject(jsonObject):
    isHavingError=False
    try:
        if jsonObject['type']=='ERROR':
            isHavingError=True
        elif 'children' in jsonObject.keys():
            lstChildren=jsonObject['children']
            for i in range(0,len(lstChildren)):
                isHavingError=walkAndFindErrorInsideObject(lstChildren[i])
                if isHavingError:
                    break
    except:
        traceback.print_exc()
    return isHavingError

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
            isHavingError=False
            if len(lstPossibleStatements) == 1:
                selectItem['singleRoot']=True
                isHavingError=walkAndFindErrorInsideObject(selectItem)
            else:
                # for j in range(1, len(lstPossibleStatements)):
                #     candItem = lstPossibleStatements[j]
                #     isHavingError = walkAndFindErrorInsideObject(selectItem)
                #     if isHavingError:
                #         break
                #     if candItem['startLine'] < selectItem['startLine'] and candItem['endLine'] > selectItem['endLine']:
                #         selectItem = candItem
                #     elif candItem['startLine'] == selectItem['startLine'] and candItem['endLine'] == selectItem[
                #         'endLine']:
                #         if (candItem['endOffset'] - candItem['startOffset']) > (
                #                 selectItem['endOffset'] - selectItem['startOffset']):
                #             selectItem = candItem
                # selectItem['singleRoot'] = False
                lstPopKeys.append(item)

            # mainStmt = '{}-{}-{}-{}-{}'.format(selectItem['type'], selectItem['startLine'], selectItem['startOffset'],
            #                                    selectItem['endLine'], selectItem['endOffset'])
            dictLinesAndElements[item]['mainStmt'] = selectItem
            selectItem['isReplaceable'] = True

            if isHavingError:
                lstPopKeys.append(item)
            elif (selectItem['startLine']-selectedTup[0]<2) or (selectedTup[1] -selectItem['endLine']<2):
                lstPopKeys.append(item)
            elif selectItem['startLine']==selectItem['endLine'] and (selectItem['endOffset']-selectItem['startOffset']<=3):
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

def checkAppearInImplementation(dictLiterals,strPseudo,strCode):
    strPseudoSplit=''
    strCodeSplit=''
    strTokSplit=''
    strCodeTokSplit = ''
    try:
        # print('code {}'.format(strCode))
        arrPseudos=strPseudo.split()
        arrCodes=strCode.split()
        lstTokCode=[]
        for itemCode in arrCodes:
            # print('itemCode {}'.format(itemCode))
            arrCodeSplit=re.findall(strRegexCamelCases, itemCode)
            if len(arrCodeSplit)==0:
                arrCodeSplit=[itemCode]
            # print('arr {}'.format(arrCodeSplit))
            for item in arrCodeSplit:
                # print('abc {}'.format(item))
                lstTokCode.append(item.lower())
        setTokCode=set(lstTokCode)
        lstTokPseudo=[]
        numAppear=0
        numDisappear=0
        for itemPseudo in arrPseudos:
            isAppear = False
            if itemPseudo.startswith('SpecialLiteral_'):
                # print('itemPseudo {}'.format(itemPseudo))
                # input('I love')
                valItem=dictLiterals[itemPseudo]
                # print('val {}\nstr {}'.format(valItem,strCode))
                if valItem in strCode:
                    isAppear=True
                else:
                    isAppear=False
            else:
                arrPseudoSplit = re.findall(strRegexCamelCases, itemPseudo)
                if len(arrPseudoSplit)==0:
                    arrPseudoSplit=[itemPseudo]
                isAppear=False
                for item in arrPseudoSplit:
                    strItLower=item.lower()
                    if not strItLower in setTokCode:
                        isAppear=False
                        break
                    else:
                        isAppear=True
            if isAppear:
                numAppear=numAppear+1
                lstTokPseudo.append(itemPseudo+'#1')
            else:
                numDisappear=numDisappear+1
                lstTokPseudo.append(itemPseudo + '#0')
        strPseudoSplit=' '.join(arrPseudos)
        strCodeSplit=' '.join(arrCodes)
        strTokSplit=' '.join(lstTokPseudo)
        strCodeTokSplit=' '.join(lstTokCode)
    except:
        traceback.print_exc()
    percent=0
    if (numAppear+numDisappear)!=0:
        percent=numAppear*1.0/(numAppear+numDisappear)
    else:
        percent=0
    return strCodeSplit,strCodeTokSplit,strPseudoSplit,strTokSplit,numAppear,numDisappear,percent

def generateMixVersionsAndLabels(jsonObject,dictLinesAndElements,dictLabelStatistics,dictLiterals,arrCodes,arrPseudos,fopCodeVersion,fonameItemAST,idCode,fopAllocateByMainStmt,fopAllocateByNumOfStmts):
    try:
        isOK=False
        indexVersion=0
        fpItemPseudo=fopCodeVersion+'_a_pseudo.txt'
        fpItemCode=fopCodeVersion+'_a_code.cpp'
        fpItemGraphText = fopCodeVersion + '_a_graph.dot'
        fpItemGraphPng = fopCodeVersion + '_a_graph.png'
        f1=open(fpItemPseudo,'w')
        f1.write('\n'.join(arrPseudos))
        f1.close()
        f1=open(fpItemCode,'w')
        f1.write('\n'.join(arrCodes))
        f1.close()
        if 'test' in fopCodeVersion:
            graph = pgv.AGraph(directed=True)
            isBlueColor = True
            idChange = '-1'
            generateGraph(jsonObject,'',arrCodes, idChange, isBlueColor, graph)
            graph.write(fpItemGraphText)
            # graph.layout()
            # graph.draw(fpItemGraphPng)
            # (graphPydot,) = pydot.graph_from_dot_file(fpItemGraphText)
            # graphPydot.write_png(fpItemGraphPng)
            # check_call(['dot', '-Tpng', fpItemGraphText, '-o', fpItemGraphPng])
            # render('dot', 'png', fpItemGraphText)

        for keyItem in dictLinesAndElements.keys():
            valItem=dictLinesAndElements[keyItem]
            indexVersion=indexVersion+1
            fnIndexVersion='v_{}'.format(indexVersion)
            fpItemVersionCode=fopCodeVersion+fnIndexVersion+'_mix.cpp'
            fpItemVersionLabel = fopCodeVersion + fnIndexVersion + '_label.txt'
            mainStmt = valItem['mainStmt']
            startLineMainStmt=mainStmt['startLine']
            endLineMainStmt = mainStmt['endLine']

            lstPseudoLines=range(startLineMainStmt-distanceHeader,endLineMainStmt-distanceHeader+1)
            lstStrPseudoLines=[]
            lstStrCodeLines = []
            for it in lstPseudoLines:
                lstStrPseudoLines.append(arrPseudos[it])
                lstStrCodeLines.append(arrCodes[it+distanceHeader])

            strTotalComment='// '+' , then '.join(lstStrPseudoLines)
            strTotalCode=' '.join(lstStrCodeLines)
            strCodeSplit,strCodeTokSplit,strPseudoSplit,strTokSplit,numAppear,numDisappear,percent=checkAppearInImplementation(dictLiterals,strTotalComment,strTotalCode)

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
                        strLineAdd='{}{}'.format(''.join(lstStrs),strTotalComment)
                    else:
                        strLineAdd = '{}{}'.format(''.join(lstStrs), '//')
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

            if strMainStatement not in dictLabelStatistics['mainStmt'].keys():
                dictLabelStatistics['mainStmt'][strMainStatement]=1
            else:
                dictLabelStatistics['mainStmt'][strMainStatement] =dictLabelStatistics['mainStmt'][strMainStatement] + 1

            if numOfStatements not in dictLabelStatistics['numOfStatements'].keys():
                dictLabelStatistics['numOfStatements'][numOfStatements]=1
            else:
                dictLabelStatistics['numOfStatements'][numOfStatements] =dictLabelStatistics['numOfStatements'][numOfStatements] + 1


            f1=open(fpItemVersionLabel,'w')
            strLbl='{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\t{}\t{}'.format(strMainStatement,strPosition,numOfLine,numOfStatements,strBelowStatements,strDictToString, strCodeSplit,strCodeTokSplit,strPseudoSplit,strTokSplit,numAppear,numDisappear,percent)
            f1.write(strLbl)
            f1.close()


            if 'test' in fopCodeVersion:
                graph = pgv.AGraph(directed=True)
                isBlueColor = True
                idChange = str(mainStmt['id'])
                generateGraph(jsonObject,'',arrCodes, idChange, isBlueColor, graph)
                graph.write(fopCodeVersion+fnIndexVersion+'_graph.dot')
                # graph.layout(prog='dot')
                # graph.draw(fopCodeVersion+fnIndexVersion+'_graph.png')


            fopItemAllMainStmt=fopAllocateByMainStmt+strMainStatement+'/'+fonameItemAST+'/'+idCode+'/'
            createDirIfNotExist(fopItemAllMainStmt)
            fopItemAllNumOfStmts = fopAllocateByNumOfStmts + str(numOfStatements) + '/' + fonameItemAST + '/' + idCode + '/'
            createDirIfNotExist(fopItemAllNumOfStmts)
            # if os.path.isdir(fopItemAllMainStmt):
            #     shutil.rmtree(fopItemAllMainStmt)
            # if os.path.isdir(fopItemAllNumOfStmts):
            #     shutil.rmtree(fopItemAllNumOfStmts)
            shutil.copy(fopCodeVersion+fnIndexVersion+'_mix.cpp', fopItemAllMainStmt+fnIndexVersion+'_mix.cpp')
            shutil.copy(fopCodeVersion+fnIndexVersion+ '_label.txt', fopItemAllMainStmt+fnIndexVersion+ '_label.txt')
            shutil.copy(fopCodeVersion+fnIndexVersion+'_mix.cpp', fopItemAllNumOfStmts+fnIndexVersion+'_mix.cpp')
            shutil.copy(fopCodeVersion + fnIndexVersion + '_label.txt',fopItemAllNumOfStmts + fnIndexVersion + '_label.txt')
            if 'test' in fopCodeVersion:
                shutil.copy(fopCodeVersion + fnIndexVersion + '_graph.dot',
                            fopItemAllNumOfStmts + fnIndexVersion + '_graph.dot')
            #     shutil.copy(fopCodeVersion + fnIndexVersion + '_graph.png',
            #                 fopItemAllNumOfStmts + fnIndexVersion + '_graph.png')
    except:
        traceback.print_exc()

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2_tokenize/'
fopPseudoFile=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopLabels=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopMixVersion=fopRoot+'step4_mixCode/'
fopAllocateByMainStmt=fopRoot+'step4_mainStmt/'
fopAllocateByNumOfStmts=fopRoot+'step4_numOfStatements/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
createDirIfNotExist(fopMixVersion)
createDirIfNotExist(fopAllocateByMainStmt)
createDirIfNotExist(fopAllocateByNumOfStmts)

f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiterals={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiterals[arrTabs[0]]=strContent

# print('len dict {}'.format(len(dictLiterals.keys())))
# input('abc ')


lstFpDictASTs=glob.glob(fopTreeSitterFile+'**/*_code_ast.txt',recursive=True)
distanceHeader=33

dictLabelStatistics={}
dictLabelStatistics['mainStmt']={}
dictLabelStatistics['numOfStatements']={}
# if os.path.isdir(fopMixVersion):
#     shutil.rmtree(fopMixVersion)

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
        # if os.path.isdir(fopCodeVersion):
        #     shutil.rmtree(fopCodeVersion)
        createDirIfNotExist(fopCodeVersion)
        fnLogOutput='a_logPrint.txt'
        fpCodeLogOutput=fopCodeVersion+fnLogOutput
        fpCodeJsonOutput = fopCodeVersion + 'a_json.txt'

        # if 'train' not in fopCodeVersion:
        #     continue

        sys.stdout = open(fpCodeLogOutput, 'w')
        f1=open(fpItemPseudo,'r')
        arrPseudos=f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemCode, 'r')
        arrCodes = f1.read().strip().split('\n')
        f1.close()
        f1=open(fpItemAST,'r')
        strASTContent=f1.read().strip().split('\n')[1]
        f1.close()
        jsonObject = ast.literal_eval(strASTContent)
        f1=open(fpCodeJsonOutput,'w')
        f1.write(str(jsonObject))
        f1.close()
        dictLinesAndElements={}
        indent=1
        lstTupFunctionDeclarations=[]
        walkJsonAndGetIndent(jsonObject,dictLinesAndElements,indent)
        print('dict before {}'.format(len(dictLinesAndElements.keys())))
        findReplaceableStatements(dictLinesAndElements, lstTupFunctionDeclarations)
        print('dict after {}'.format(len(dictLinesAndElements.keys())))
        # print('dict final content\n{}'.format(dictLinesAndElements))
        generateMixVersionsAndLabels(jsonObject,dictLinesAndElements,dictLabelStatistics,dictLiterals,arrCodes,arrPseudos,fopCodeVersion,fonameItemAST,idCode,fopAllocateByMainStmt,fopAllocateByNumOfStmts)

        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print('end {}/{} {}'.format(i,len(lstFpDictASTs),fpCodeLogOutput))
        # if i==2000:
        #     break
    except:
        traceback.print_exc()

fpDictLblMainStmt=fopMixVersion+ 'labels_mainStmt.txt'
fpDictLblNumOfStatement=fopMixVersion+ 'labels_numOfStatement.txt'

dictSorted=dict(sorted(dictLabelStatistics['mainStmt'].items(), key=operator.itemgetter(1), reverse=True))
lstStr=[]
for key in dictSorted.keys():
    lstStr.append('{}\t{}'.format(key,dictSorted[key]))
f1=open(fpDictLblMainStmt,'w')
f1.write('\n'.join(lstStr))
f1.close()

dictSorted=dict(sorted(dictLabelStatistics['numOfStatements'].items(), key=operator.itemgetter(1), reverse=True))
lstStr=[]
for key in dictSorted.keys():
    lstStr.append('{}\t{}'.format(key,dictSorted[key]))
f1=open(fpDictLblNumOfStatement,'w')
f1.write('\n'.join(lstStr))
f1.close()