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
                if itemChild['id']==jsonPartCode['id']:
                    jsonPartPOS['id']=itemChild['id']
                    jsonPartPOS['isNLTree']=True
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

def generateGraphForMixCode(jsonObject,arrCodes,strRootProgramId,strRootLabel,isInNLNodes,graph):
    strValue=''
    isAbstract = False
    strType='ASTNode'
    strLabelInClassification=''

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
            isAbstract = True
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
        if not 'children' in jsonObject.keys():
            strValue=jsonObject['tag']
            if strValue=='S1':
                strValue='NLRoot_'+strRootProgramId
        else:
            strValue=jsonObject['value']

    # strLabel = '{}\n{}'.format(strId, jsonObject['type'])

    strLabel = '{}\n{}\n{}\n{}\n{}'.format(isAbstract, strType,strValue, strLabelInClassification)

    if isInNLNodes:
        graph.add_node(strLabel, color='blue')
    else:
        graph.add_node(strLabel, color='red')

    if 'children' in jsonObject.keys():
        lstChildren = jsonObject['children']
        for i in range(0, len(lstChildren)):
            strChildLabel = generateGraphForMixCode(lstChildren[i],arrCodes,strRootProgramId,strRootLabel,isInNLNodes,graph)
            if strLabel != strChildLabel:
                graph.add_edge(strLabel, strChildLabel, color='black')
    # else:
    #     strTerminalLabel = '\n{}\n{}'.format(strPosition,
    #                                            getTerminalValue(startLine, startOffset, endLine, endOffset,
    #                                                             arrCodes))
    #     graph.add_node(strTerminalLabel, color='yellow')
    #     graph.add_edge(strLabel, strTerminalLabel, color='black')

    return strLabel


fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
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


lstFpJsonFiles=glob.glob(fopMixVersion+'**/a_json.txt',recursive=True)
distanceHeader=33

# if os.path.isdir(fopMixVersion):
#     shutil.rmtree(fopMixVersion)

lstNumContexts=[1,2,3,1000]

for i in range(0,len(lstFpJsonFiles)):
    fpItemAST=lstFpJsonFiles[i]
    fnDictJson=os.path.basename(fpItemAST)
    fopItemProgram=os.path.dirname(fpItemAST)
    fonameItemProgram=os.path.basename(fopItemProgram)
    fopItemTrainTest=os.path.dirname(fopItemProgram)
    fonameItemTrainTest=os.path.basename(fopItemTrainTest)

    try:
        fpCodeLogOutput=fopItemProgram+'a_logPrint.txt'
        sys.stdout = open(fpCodeLogOutput, 'a')

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
        jsonAll = arrJsonAST[0]

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
            jsonPartAST = arrVerLabel[5]
            jsonPartPseudo = arrVerLabel[11]
            jsonMixClone=copy.deepcopy(jsonAll)
            getMixJsonDict(jsonMixClone,jsonPartAST,jsonPartPseudo)
            fpItemMixCodeJson=fopItemVersionGraph+'jsonMix.txt'
            f1=open(fpItemMixCodeJson,'w')
            f1.write(str(jsonMixClone))
            f1.close()
            graph = pgv.AGraph(directed=True)


            for idxContext in lstNumContexts:
                try:




                except:
                    traceback.print_exc()





        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print('end {}/{} {}'.format(i,len(lstFpJsonFiles),fpItemAST))

    except:
        traceback.print_exc()

