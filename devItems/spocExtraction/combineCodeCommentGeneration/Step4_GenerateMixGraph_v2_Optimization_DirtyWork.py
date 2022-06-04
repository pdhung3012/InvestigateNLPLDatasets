import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser
from Util_LibForGraphExtractionFromRawCode import getJsonDict,getTerminalValue
import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render
import copy

strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '

def revertBackWordFromPOS(strInput):
    strOutput=strInput.replace('_MODULO_','%')
    return strOutput

def removeAllNodesAsSingleChild(jsonMix):
    pass
    # if 'children' in jsonMix.keys():
    #     lstChildren = jsonMix['children']
    #     if len(lstChildren)==1 and ('isNLRootNode' not in lstChildren[0].keys() or lstChildren[0]['isNLRootNode']==False):
    #         # print('gp to here')
    #         if 'children' in lstChildren[0].keys():
    #             jsonMix['children']=lstChildren[0]['children']
    #     else:
    #         for item in lstChildren:
    #             removeAllNodesAsSingleChild(item)


def getMixJsonDictAndIndent(jsonASTClone,jsonPartPOS,lineReplace,indentInCode,dictIndentOfNL):
    try:
        # print(lineReplace)
        jsonASTClone['levelInAST']=indentInCode
        if 'children' in jsonASTClone.keys():
            lstChildren=jsonASTClone['children']
            indentInCode=indentInCode+1
            for i in range(0,len(lstChildren)):
                itemChild=lstChildren[i]
                if itemChild['startLine']==itemChild['endLine'] and itemChild['endLine']==lineReplace :
                    jsonPartPOS['id']=str(itemChild['id'])
                    jsonPartPOS['isNLRootNode']=True
                    jsonPartPOS['startLine'] = itemChild['startLine']
                    jsonPartPOS['startOffset'] = itemChild['startOffset']
                    jsonPartPOS['endLine'] = itemChild['endLine']
                    jsonPartPOS['endOffset'] = itemChild['endOffset']
                    jsonPartPOS['levelInAST'] = indentInCode
                    jsonASTClone['children'][i]=jsonPartPOS
                    dictIndentOfNL['nlIndentInAST']=indentInCode
                    # print('dict here {}'.format(dictIndentOfNL))
                    # input('aaa ')
                    # print('{} aaabbbb {} aaabbbb {}'.format(itemChild['startLine'], itemChild['endLine'], lineReplace))
                    # print('go here aaa')
                else:
                    getMixJsonDictAndIndent(itemChild,jsonPartPOS,lineReplace,indentInCode,dictIndentOfNL)
    except:
        traceback.print_exc()
def getLeafNodesFromJSon(jsonMix,lstLeafNodes):
    if 'children' not in jsonMix.keys() or len(jsonMix['children'])==0:
        lstLeafNodes.append(jsonMix)
    else:
        lstChildren = jsonMix['children']
        for i in range(0, len(lstChildren)):
            itemChild = lstChildren[i]
            getLeafNodesFromJSon(itemChild,lstLeafNodes)

def traverseAndKeepOnlyLevel(jsonMix,currentLevel,levelKeepInPOSTree):

    if currentLevel>=levelKeepInPOSTree:
        lstLeafs=[]
        getLeafNodesFromJSon(jsonMix,lstLeafs)
        jsonMix['children']=lstLeafs

    elif 'children' in jsonMix.keys():
        lstChildren = jsonMix['children']
        currentLevel=currentLevel+1
        for i in range(0, len(lstChildren)):
            itemChild = lstChildren[i]
            traverseAndKeepOnlyLevel(itemChild,currentLevel,levelKeepInPOSTree)
def removeNodeWithSpecificIndentLevel(jsonMix,dictIndentOfNL,levelKeepInPOSTree):
    indentInCode=jsonMix['levelInAST']
    if indentInCode>=dictIndentOfNL['nlIndentInAST'] and 'children' in jsonMix.keys():
        if ('isNLRootNode' not in jsonMix.keys() or jsonMix['isNLRootNode']==False):
            lstLeafNodes=[]
            getLeafNodesFromJSon(jsonMix,lstLeafNodes)
            jsonMix['children']=lstLeafNodes
        else:
            currentLevel=1
            traverseAndKeepOnlyLevel(jsonMix,currentLevel,levelKeepInPOSTree)
    elif 'children' in jsonMix.keys():
        lstChildren = jsonMix['children']
        for i in range(0, len(lstChildren)):
            removeNodeWithSpecificIndentLevel(lstChildren[i],dictIndentOfNL,levelKeepInPOSTree)


def generateGraph(jsonObject,strFatherLabel,arrCodes,idChange,isBlueColor,graph):
    startLine=jsonObject['startLine']
    startOffset=jsonObject['startOffset']
    endLine=jsonObject['endLine']
    endOffset=jsonObject['endOffset']
    if startLine==endLine:
        strPosition='Line {}'.format(startLine+1)
    else:
        strPosition='Lines [{} - {}]'.format(startLine+1,endLine+1)
    # strPosition='{}-{}-{}-{}'.format(startLine,startOffset,endLine,endOffset)
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
        strTerminalLabel='{}\n{}'.format(strPosition,getTerminalValue(startLine,startOffset,endLine,endOffset,arrCodes))
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

def generateGraphForMixCode(jsonObject,arrCodes,strRootProgramId,isInNLNodes,dictGraphIndexContext,dictAcceptableIdsForVersions):
    strValue='EMPTY'
    isAbstract = False
    strType='ASTNode'
    strLabelInClassification=''
    strId='-1'

    if 'isNLRootNode' in jsonObject.keys():
        isInNLNodes=True

    if not isInNLNodes:
        startLine = jsonObject['startLine']
        startOffset = jsonObject['startOffset']
        endLine = jsonObject['endLine']
        endOffset = jsonObject['endOffset']
        strId = str(jsonObject['id'])
        strPosition = '{}-{}-{}-{}'.format(startLine, startOffset, endLine, endOffset)
        if startLine == endLine:
            strPosition = 'Line {}[{}:{}]'.format(startLine + 1, startOffset + 1, endOffset + 1)
        else:
            strPosition = 'Line {}[{}:] to {}[:{}]'.format(startLine + 1, startOffset + 1, endLine + 1,
                                                           endOffset + 1)
        if strId=='1':
            strType='ProgramRoot'
            isAbstract = True
            strValue='ProgramRoot_'+strRootProgramId
        else:
            strType='ASTNode'

        if not 'children' in jsonObject.keys():
            strValue=jsonObject['type']+'\n'+getTerminalValue(startLine, startOffset, endLine, endOffset,
                                                                arrCodes)
        else:
            strValue=jsonObject['type']
        strLabel = '{}\n{}\n{}'.format(strType, strPosition,strValue)
        # if strValue!='':
        #     strLabel = '{}\n{}\n{}\n{}'.format(strType, strPosition,strValue)
    else:
        strRealLabel=revertBackWordFromPOS(jsonObject['label'])
        if 'isNLRootNode' in jsonObject.keys():
            strType = 'NLRoot'
            startLine = jsonObject['startLine']
            startOffset = jsonObject['startOffset']
            endLine = jsonObject['endLine']
            endOffset = jsonObject['endOffset']
            strPosition = '{}-{}-{}-{}'.format(startLine, startOffset, endLine, endOffset)
            if startLine == endLine:
                strPosition = 'Line {}[{}:{}]'.format(startLine + 1, startOffset + 1, endOffset + 1)
            else:
                strPosition = 'Line {}[{}:] to {}[:{}]'.format(startLine + 1, startOffset + 1, endLine + 1,
                                                                   endOffset + 1)

            strLabel = '{}\n{}\n{}'.format(strType,strPosition, strRealLabel)
        else:
            strType='NLNode'
            strLabel = '{}\n{}'.format(strType, strRealLabel)
        # if 'children' in jsonObject.keys():
        #     strValue = jsonObject['tag']
        #     if strValue == 'S1' or strValue == 'Paragraph':
        #         strValue = 'NLRoot_' + strRootProgramId
        #         # print('tagg {}'.format(strValue))
        # else:
        #     strValue = jsonObject['value']
    # strLabel = '{}\n{}'.format(strId, jsonObject['type'])

    # strLabel = '{}\n{}\n{}'.format(strId,strPosition,strType)
    # print('current label value {}'.format(strValue))
    if isInNLNodes:
        for numContext in dictGraphIndexContext.keys():
            graphId = dictGraphIndexContext[numContext]
            strRealType=strLabel.split('\n')[0]
            if strRealType=='NLRoot':
                graphId.add_node(strLabel,style='filled',fillcolor='lightpink', color='red')
            else:
                graphId.add_node(strLabel, color='red')
    else:
        for numContext in dictGraphIndexContext.keys():
            # print('accept lbl here {}\n{}'.format(strId, dictAcceptableIdsForVersions[numContext]))
            if int(strId) in dictAcceptableIdsForVersions[numContext]:
                # print('accept lbl here {} {}'.format(strId,strLabel))
                graphId = dictGraphIndexContext[numContext]
                strRealType = strLabel.split('\n')[0]
                if strRealType == 'ProgramRoot':
                    graphId.add_node(strLabel, style='filled', fillcolor='lightblue1', color='blue')
                else:
                    graphId.add_node(strLabel, color='blue')



    if 'children' in jsonObject.keys():
        lstChildren = jsonObject['children']
        for i in range(0, len(lstChildren)):
            strChildLabel = generateGraphForMixCode(lstChildren[i],arrCodes,strRootProgramId,isInNLNodes,dictGraphIndexContext,dictAcceptableIdsForVersions)

            if not isInNLNodes:
                strChildId=lstChildren[i]['id']
                for numContext in dictGraphIndexContext.keys():
                    if int(strId) in dictAcceptableIdsForVersions[numContext] and int(strChildId) in dictAcceptableIdsForVersions[numContext]:
                        graphId = dictGraphIndexContext[numContext]
                        graphId.add_edge(strLabel, strChildLabel, color='black')
            else:
                for numContext in dictGraphIndexContext.keys():
                    graphId = dictGraphIndexContext[numContext]
                    graphId.add_edge(strLabel, strChildLabel, color='black')



    # else:
    #     strTerminalLabel = '\n{}\n{}'.format(strPosition,
    #                                            getTerminalValue(startLine, startOffset, endLine, endOffset,
    #                                                             arrCodes))
    #     graph.add_node(strTerminalLabel, color='yellow')
    #     graph.add_edge(strLabel, strTerminalLabel, color='black')

    return strLabel

def getFatherRelationship(jsonAll,dictOfFatherIdMainAST):
    strId=''
    if 'id' in jsonAll.keys():
        strId=jsonAll['id']

    if 'children' in jsonAll.keys() and 'isNLRootNode' not in jsonAll.keys():
        lstChildren=jsonAll['children']
        for i in range(0,len(lstChildren)):
            itemChild=lstChildren[i]
            dictOfFatherIdMainAST[itemChild['id']]=strId
            getFatherRelationship(itemChild,dictOfFatherIdMainAST)

def findAddableIdsForContext(jsonAll,dictOfFatherIdMainAST,dictAcceptableIdsForVersions,mixLine,dictAncestorToRoot):
    strId=''
    if 'id' in jsonAll.keys():
        strId=jsonAll['id']
    curStartLine=jsonAll['startLine']
    curEndLine=jsonAll['endLine']

    for numContext in dictAcceptableIdsForVersions.keys():
        originStart=mixLine-numContext
        originEnd=mixLine+numContext
        if curStartLine>=originStart and curEndLine<=originEnd:
            if strId not in dictAncestorToRoot.keys():
                indexId = strId
                lstAncestorIds = []
                lstAncestorIds.append(indexId)
                while (indexId in dictOfFatherIdMainAST.keys()):
                    indexId = dictOfFatherIdMainAST[indexId]
                    lstAncestorIds.append(indexId)
                dictAncestorToRoot[strId] = lstAncestorIds
            lstAncestorIds=dictAncestorToRoot[strId]
            dictAcceptableIdsForVersions[numContext].append(strId)
            for ancestorId in lstAncestorIds:
                dictAcceptableIdsForVersions[numContext].append(ancestorId)

    if 'children' in jsonAll.keys() and 'isNLRootNode' not in jsonAll.keys():
        lstChildren=jsonAll['children']
        for i in range(0,len(lstChildren)):
            itemChild=lstChildren[i]
            findAddableIdsForContext(itemChild, dictOfFatherIdMainAST, dictAcceptableIdsForVersions,
                                     mixLine, dictAncestorToRoot)

def getAllLeaveNodes(g):
    leafs = [x for x in g.nodes() if g.out_degree(x)==0 and g.in_degree(x)==1]
    return leafs

def augmentLeafNodes(graph):
    leafs=getAllLeaveNodes(graph)
    if(len(leafs)>1):
        nodeNLRoot=None
        for x in graph.nodes():
            strLabel=str(x).split('\n')[0]
            if strLabel=='NLRoot':
                nodeNLRoot=x
                break
        for i in range(0,len(leafs)-1):
            # print(leafs[i])
            strLabelI = str(leafs[i]).split('\n')[0]
            strLabelPlus = str(leafs[i+1]).split('\n')[0]
            if strLabelI=='ASTNode' and strLabelPlus=='ASTNode':
                graph.add_edge(leafs[i],leafs[i+1])
            elif strLabelI=='ASTNode' and strLabelPlus=='NLNode':
                graph.add_edge(leafs[i],nodeNLRoot)
            elif strLabelI=='NLNode' and strLabelPlus=='ASTNode':
                graph.add_edge(nodeNLRoot,leafs[i+1])

        # if not nodeNLRoot is None:
        #     for i in range(0, len(leafs)):
        #         strLabel = str(leafs[i]).split('\n')[1]
        #         if strLabel=='NLNode':
        #             graph.add_edge(leafs[i], nodeNLRoot)




fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep4NMT=fopRoot+'step4_NMT_dirty/'
fopStep3V2=fopRoot+'step3_v2/'
fopStep3TreesitterTokenize=fopRoot+'step3_treesitter_tokenize/'
fopStep2Tokenize=fopRoot+'step2_tokenize/'
fopStep2PseudoTokenize=fopRoot+'step2_pseudo_tokenize/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
createDirIfNotExist(fopStep4NMT)
fpErrorLog2=fopStep3V2+'error_log_2.txt'
f1=open(fpErrorLog2,'w')
f1.write('')
f1.close()

f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiterals={}
dictLiteralsReverse={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiterals[arrTabs[0]]=strContent
        dictLiteralsReverse[strContent]=arrTabs[0]


# sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
distanceHeader=33


lstFpInput=glob.glob(fopStep3V2+'*.txt')

dictFolderContent={}
# dictNewContent={}
for i in range(0,len(lstFpInput)):
    fpItem=lstFpInput[i]
    nameItem=os.path.basename(fpItem)
    f1=open(fpItem,'r')
    arrContent=f1.read().strip().split('\n')
    f1.close()
    dictFolderContent[nameItem]=arrContent
    # dictNewContent[nameItem]=[[],[],[]]
fnLocation='location.txt'
fnSource='source.txt'
fnPOSNLTK='pos_nltk.txt'
fnPOSStanford='pos_stanford.txt'

arrLocs=dictFolderContent[fnLocation]
arrSource=dictFolderContent[fnSource]
arrPOSNLTK=dictFolderContent[fnPOSNLTK]
arrPOSStanford=dictFolderContent[fnPOSStanford]

lstNumContexts=[1]
lstPOSType=[fnPOSStanford]
countNumMixCode=0

arrFinalCodes=None
arrFinalPseudocodes=None
arrJsonAST=None
jsonAll=None
dictOfFatherIdMainAST = {}
prevProgramId=''
for i in range(0,len(arrLocs)):
    # i != 54 and
    if(i!=54):
        continue
    arrTabLocs=arrLocs[i].split('\t')
    strTrainTestFolder=arrTabLocs[1]
    strRootProgramId=arrTabLocs[0]
    linePseudocodeProgram=int(arrTabLocs[2])
    lineInRealCode=linePseudocodeProgram-1+distanceHeader
    # print('line in real {}'.format(lineInRealCode))
    # input('aaa')
    fpItemAST=fopStep3TreesitterTokenize+strTrainTestFolder+'/'+strRootProgramId+'_code_ast.txt'
    fpItemCode = fopStep2Tokenize + strTrainTestFolder + '/' + strRootProgramId + '_code.cpp'
    fpItemFinalPseudocode = fopStep2PseudoTokenize+strTrainTestFolder+'/'+strRootProgramId + '_text.txt'
    fopOutputItem=fopStep4NMT+strTrainTestFolder+'__'+strRootProgramId+'__'+str(lineInRealCode+1)+'/'
    createDirIfNotExist(fopOutputItem)
    fpCodeLogOutput = fopOutputItem + 'a_logPrint.txt'
    fpOutMixCode = fopOutputItem + 'a_mixCode.cpp'
    fpOutExpectedCode = fopOutputItem + 'a_expectedCode.cpp'
    # sys.stdout = open(fpCodeLogOutput, 'w')

    if strRootProgramId!=prevProgramId:
        f1 = open(fpItemCode, 'r')
        arrFinalCodes = f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemFinalPseudocode, 'r')
        arrFinalPseudocodes = f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemAST, 'r')
        arrJsonAST = f1.read().strip().split('\n')
        f1.close()
        jsonAll = ast.literal_eval(arrJsonAST[1])
        dictOfFatherIdMainAST = {}
        getFatherRelationship(jsonAll, dictOfFatherIdMainAST)

    f1=open(fpOutExpectedCode,'w')
    f1.write('\n'.join(arrFinalCodes))
    f1.close()
    lstMix=arrFinalCodes.copy()
    lstMix[lineInRealCode]='// '+arrFinalPseudocodes[linePseudocodeProgram-1]
    f1=open(fpOutMixCode,'w')
    f1.write('\n'.join(lstMix))
    f1.close()

    for j in range(0,len(lstPOSType)):
        try:
            jsonPartPseudo = ast.literal_eval(dictFolderContent[lstPOSType[j]][i])
            jsonPartPseudo2 = ast.literal_eval(dictFolderContent[lstPOSType[j]][i])
            # print(jsonPartPseudo)
            jsonAll = ast.literal_eval(arrJsonAST[1])
            jsonMixClone = copy.deepcopy(jsonAll)
            jsonMixCloneFilter = copy.deepcopy(jsonAll)


            # print('line in real {}'.format(lineInRealCode))
            # input('bbb')
            indentInCode=1
            dictIndentOfNL={}
            getMixJsonDictAndIndent(jsonMixClone, jsonPartPseudo, lineInRealCode,indentInCode,dictIndentOfNL)
            getMixJsonDictAndIndent(jsonMixCloneFilter, jsonPartPseudo2, lineInRealCode, indentInCode, dictIndentOfNL)
            removeAllNodesAsSingleChild(jsonMixCloneFilter)
            levelOfPOSTreeKeep=3
            removeNodeWithSpecificIndentLevel(jsonMixCloneFilter,dictIndentOfNL, levelOfPOSTreeKeep)

            dictGraphIndexContext = {}
            dictGraphFilterIndexContext = {}
            dictAcceptableIdsForVersions = {}
            dictFilterAcceptableIdsForVersions = {}
            for idxLine in lstNumContexts:
                dictAcceptableIdsForVersions[idxLine] = []
                dictFilterAcceptableIdsForVersions[idxLine] = []
                graphIt = pgv.AGraph(directed=True)
                graphItFilter = pgv.AGraph(directed=True)
                dictGraphIndexContext[idxLine] = graphIt
                dictGraphFilterIndexContext[idxLine] = graphItFilter


            dictAncestorToRoot={}
            dictFilterAncestorToRoot = {}
            findAddableIdsForContext(jsonAll, dictOfFatherIdMainAST, dictAcceptableIdsForVersions, lineInRealCode, dictAncestorToRoot)
            findAddableIdsForContext(jsonAll, dictOfFatherIdMainAST, dictFilterAcceptableIdsForVersions, lineInRealCode,
                                     dictFilterAncestorToRoot)
            isInNLNode=False
            generateGraphForMixCode(jsonMixClone, arrFinalCodes, strRootProgramId, isInNLNode,
                                    dictGraphIndexContext, dictAcceptableIdsForVersions)
            isInNLNode = False
            generateGraphForMixCode(jsonMixCloneFilter, arrFinalCodes, strRootProgramId, isInNLNode,
                                    dictGraphFilterIndexContext, dictFilterAcceptableIdsForVersions)
            for keyGraph in dictGraphIndexContext.keys():
                graphIt = dictGraphIndexContext[keyGraph]
                graphItFilter=dictGraphFilterIndexContext[keyGraph]
                strConTextAndPOSType='graph_context_{}_pos_{}'.format(keyGraph,lstPOSType[j].replace('pos_','').replace('.txt',''))
                fpContextItemGraphText = fopOutputItem + strConTextAndPOSType + '.dot'
                fpContextItemGraphPng = fopOutputItem + strConTextAndPOSType + '.png'
                graphIt.write(fpContextItemGraphText)

                strFilterConTextAndPOSType = 'graphFilter_context_{}_pos_{}'.format(keyGraph,
                                                                        lstPOSType[j].replace('pos_', '').replace(
                                                                            '.txt', ''))
                fpFilterContextItemGraphText = fopOutputItem + strFilterConTextAndPOSType + '.dot'
                fpFilterContextItemGraphPng = fopOutputItem + strFilterConTextAndPOSType + '.png'
                graphItFilter.write(fpFilterContextItemGraphText)
                if i <=100:
                    graphIt.layout(prog='dot')
                    graphIt.draw(fpContextItemGraphPng)
                    graphItFilter.layout(prog='dot')
                    graphItFilter.draw(fpFilterContextItemGraphPng)


                augmentLeafNodes(graphItFilter)
                strFilterAddEdgesConTextAndPOSType = 'graphFilterAddEdges_context_{}_pos_{}'.format(keyGraph,
                                                                                    lstPOSType[j].replace('pos_',
                                                                                                          '').replace(
                                                                                        '.txt', ''))
                fpFilterAddEdgesContextItemGraphText = fopOutputItem + strFilterAddEdgesConTextAndPOSType + '.dot'
                fpFilterAddEdgesContextItemGraphPng = fopOutputItem + strFilterAddEdgesConTextAndPOSType + '.png'
                graphItFilter.write(fpFilterAddEdgesContextItemGraphText)

                if i <=100:
                    graphItFilter.layout(prog='dot')
                    graphItFilter.draw(fpFilterAddEdgesContextItemGraphPng)

        except:
            f1 = open(fpErrorLog2, 'a')
            f1.write(arrTabLocs[1]+'__'+arrTabLocs[0]+'__'+arrTabLocs[2]+'\n')
            f1.close()
            traceback.print_exc()
    # sys.stdout.close()
    # sys.stdout = sys.__stdout__
    prevProgramId=strRootProgramId
    # input('need check here ')
    print('end {}/{} {}'.format(i, len(arrLocs), fpItemAST))
    # if i >= 3:
    #     break

