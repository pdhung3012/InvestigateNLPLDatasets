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
import copy

strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '

def getMixJsonDict(jsonASTClone,jsonPartCode,jsonPartPOS):
    try:
        if 'children' in jsonASTClone.keys():
            lstChildren=jsonASTClone['children']
            for i in range(0,len(lstChildren)):
                itemChild=lstChildren[i]
                if str(itemChild['id'])==str(jsonPartCode['id']):
                    jsonPartPOS['id']=str(itemChild['id'])
                    jsonPartPOS['isNLRootNode']=True
                    jsonASTClone['children'][i]=jsonPartPOS
                else:
                    getMixJsonDict(itemChild,jsonPartCode,jsonPartPOS)
    except:
        traceback.print_exc()


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

def generateGraphForMixCode(jsonObject,arrCodes,strRootProgramId,strRootLabel,isInNLNodes,graph,dictGraphIndexContext,dictAcceptableIdsForVersions):
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

        if strId=='1':
            strType='ProgramRoot'
            strLabelInClassification = strRootLabel
            isAbstract = True
            strValue='ProgramRoot_'+strRootProgramId
        else:
            strType='ASTNode'

        if not 'children' in jsonObject.keys():
            strValue=getTerminalValue(startLine, startOffset, endLine, endOffset,
                                                                arrCodes)
        else:
            strValue=jsonObject['type']
    else:
        strPosition=jsonObject['position']
        if 'isNLRootNode' in jsonObject.keys():
            strLabelInClassification = strRootLabel
            strType = 'NLRoot'
        else:
            strType='NLNode'
        if 'children' in jsonObject.keys():
            strValue = jsonObject['tag']
            if strValue == 'S1':
                strValue = 'NLRoot_' + strRootProgramId
                # print('tagg {}'.format(strValue))


        else:
            strValue = jsonObject['value']

    # strLabel = '{}\n{}'.format(strId, jsonObject['type'])

    strLabel = '{}\n{}\n{}\n{}\n{}'.format(isAbstract, strType,strValue, strLabelInClassification,strPosition)
    # strLabel = '{}\n{}\n{}'.format(strId,strPosition,strType)
    # print('current label value {}'.format(strValue))
    if isInNLNodes:
        graph.add_node(strLabel, color='red')
        for numContext in dictGraphIndexContext.keys():
            graphId = dictGraphIndexContext[numContext]
            graphId.add_node(strLabel, color='red')
    else:
        graph.add_node(strLabel, color='blue')
        for numContext in dictGraphIndexContext.keys():
            # print('accept lbl here {}\n{}'.format(strId, dictAcceptableIdsForVersions[numContext]))
            if int(strId) in dictAcceptableIdsForVersions[numContext]:
                # print('accept lbl here {} {}'.format(strId,strLabel))
                graphId = dictGraphIndexContext[numContext]
                graphId.add_node(strLabel, color='blue')



    if 'children' in jsonObject.keys():
        lstChildren = jsonObject['children']
        for i in range(0, len(lstChildren)):
            strChildLabel = generateGraphForMixCode(lstChildren[i],arrCodes,strRootProgramId,strRootLabel,isInNLNodes,graph,dictGraphIndexContext,dictAcceptableIdsForVersions)
            if strLabel != strChildLabel:
                graph.add_edge(strLabel, strChildLabel, color='black')
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

def findAddableIdsForContext(jsonAll,dictOfFatherIdMainAST,dictAcceptableIdsForVersions,mixStartLine,mixEndLine,dictAncestorToRoot):
    strId=''
    if 'id' in jsonAll.keys():
        strId=jsonAll['id']
    curStartLine=jsonAll['startLine']
    curEndLine=jsonAll['endLine']

    for numContext in dictAcceptableIdsForVersions.keys():
        originStart=mixStartLine-numContext
        originEnd=mixEndLine+numContext
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
            findAddableIdsForContext(itemChild, dictOfFatherIdMainAST, dictAcceptableIdsForVersions, mixStartLine,
                                     mixEndLine, dictAncestorToRoot)




fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopMixVersion=fopRoot+'step4_mixCode/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
createDirIfNotExist(fopMixVersion)

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

print('before traverse')
lstFpJsonFiles=[]
lstFop1=sorted(glob.glob(fopMixVersion+'*/'))
for fop1 in lstFop1:
    lstFop2=sorted(glob.glob(fop1+'*/'))
    for fop2 in lstFop2:
        fp3=fop2+'a_json.txt'
        # print(fp3)
        lstFpJsonFiles.append(fp3)
    print('end {}'.format(fop1))
# sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
print('after {} '.format(len(lstFpJsonFiles)))
distanceHeader=33

# if os.path.isdir(fopMixVersion):
#     shutil.rmtree(fopMixVersion)

lstNumContexts=[1,3,5]

for i in range(0,len(lstFpJsonFiles)):
    fpItemAST=lstFpJsonFiles[i]
    fnDictJson=os.path.basename(fpItemAST)
    fopItemProgram=os.path.dirname(fpItemAST)+'/'
    fonameItemProgram=os.path.basename(os.path.dirname(fpItemAST))
    fopItemTrainTest=os.path.dirname(fopItemProgram)+'/'
    fonameItemTrainTest=os.path.basename(os.path.dirname(fopItemProgram))

    # print('item program {} aa {}'.format(fonameItemProgram,fopItemProgram))

    try:

        # lstFopItemGraphFolders=glob.glob(fopItemProgram+'v_*_graphs/')
        # # print('len {}/{} {} {}'.format(i,len(lstFpJsonFiles),fpItemAST),len(lstFopItemGraphFolders))
        # if len(lstFopItemGraphFolders)>0:
        #     print('skip {}/{} {}'.format(i,len(lstFpJsonFiles),fpItemAST))
        #     continue

        fpCodeLogOutput=fopItemProgram+'a_logPrint.txt'
        sys.stdout = open(fpCodeLogOutput, 'w')

        fpItemFinalCode = fopItemProgram + '_a_code.cpp'
        f1 = open(fpItemFinalCode, 'r')
        arrFinalCodes = f1.read().strip().split('\n')
        f1.close()
        fpItemFinalPseudocode = fopItemProgram + '_a_pseudo.txt'
        f1 = open(fpItemFinalPseudocode, 'r')
        arrFinalPseudocodes = f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemAST, 'r')
        arrJsonAST = f1.read().strip().split('\n')
        f1.close()
        jsonAll = ast.literal_eval(arrJsonAST[0])
        dictOfFatherIdMainAST = {}
        getFatherRelationship(jsonAll,dictOfFatherIdMainAST)

        lstFpVersionLabel=glob.glob(fopItemProgram+'v_*_label.txt')
        for j in range(0,len(lstFpVersionLabel)):
            fpItemVersionLabel=lstFpVersionLabel[j]
            fnItemVersionLabel=os.path.basename(fpItemVersionLabel)
            fnVersionName=fnItemVersionLabel.replace('_label.txt','')
            fopItemVersionGraph = fopItemProgram + fnVersionName+ '_graphs/'
            createDirIfNotExist(fopItemVersionGraph)

            f1 = open(fpItemVersionLabel, 'r')
            arrVerLabel = f1.read().strip().split('\n')
            f1.close()
            jsonPartAST = ast.literal_eval(arrVerLabel[5])
            jsonPartPseudo = ast.literal_eval(arrVerLabel[11])
            print(type(jsonPartPseudo))
            jsonMixClone=copy.deepcopy(jsonAll)
            getMixJsonDict(jsonMixClone,jsonPartAST,jsonPartPseudo)
            fpItemMixCodeJson=fopItemVersionGraph+'jsonMix.txt'
            fpItemGraphText=fopItemVersionGraph+'g_all.dot'
            fpItemGraphPng=fopItemVersionGraph+'g_all.png'
            f1=open(fpItemMixCodeJson,'w')
            f1.write(str(jsonMixClone))
            f1.close()
            graphAll = pgv.AGraph(directed=True)
            strRootProgramId=fonameItemProgram+'-'+fnVersionName
            # print('root program {}'.format(strRootProgramId))
            strRootLabel=''
            strCodeType=arrVerLabel[0]
            strLOC=arrVerLabel[2]
            arrItemTab=arrVerLabel[10].split('\t')
            numInImpl=int(arrItemTab[0])
            numOutImpl=int(arrItemTab[1])
            strAppearPercent=int((((numInImpl*100.0)/(numInImpl+numOutImpl))//10)+1)
            if strAppearPercent==11:
                strAppearPercent=10
            strRootLabel='{}\t{}\t{}'.format(strCodeType,strLOC,strAppearPercent)

            isInNLNode=False
            dictGraphIndexContext={}
            dictAcceptableIdsForVersions={}
            for idxLine in lstNumContexts:
                dictAcceptableIdsForVersions[idxLine]=[]
                graphIt = pgv.AGraph(directed=True)
                dictGraphIndexContext[idxLine]=graphIt
            mixStartLine=jsonPartAST['startLine']
            mixEndLine = jsonPartAST['endLine']
            dictAncestorToRoot={}
            findAddableIdsForContext(jsonAll, dictOfFatherIdMainAST, dictAcceptableIdsForVersions, mixStartLine,
                                     mixEndLine, dictAncestorToRoot)

            for idxLine in lstNumContexts:
                dictAcceptableIdsForVersions[idxLine]=sorted(set(dictAcceptableIdsForVersions[idxLine]))
            # print(dictAcceptableIdsForVersions)

            generateGraphForMixCode(jsonMixClone, arrFinalCodes, strRootProgramId, strRootLabel, isInNLNode, graphAll,dictGraphIndexContext,dictAcceptableIdsForVersions)
            graphAll.write(fpItemGraphText)
            for keyGraph in dictGraphIndexContext.keys():
                graphIt=dictGraphIndexContext[keyGraph]
                fpContextItemGraphText = fopItemVersionGraph + 'g_'+str(keyGraph)+'.dot'
                fpContextItemGraphPng = fopItemVersionGraph + 'g_'+str(keyGraph)+'.png'
                graphIt.write(fpContextItemGraphText)
                if i < 5:
                    # (graphPydot,) = pydot.graph_from_dot_file(fpContextItemGraphText)
                    # graphPydot.write_png(fpContextItemGraphPng)
                    #
                    graphIt.layout(prog='dot')
                    graphIt.draw(fpContextItemGraphPng)

            if i<5:
                # (graphPydot,) = pydot.graph_from_dot_file(fpItemGraphText)
                # graphPydot.write_png(fpItemGraphPng)
                graphAll.layout(prog='dot')
                graphAll.draw(fpItemGraphPng)







        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print('end {}/{} {}'.format(i,len(lstFpJsonFiles),fpItemAST))

    except:
        traceback.print_exc()

