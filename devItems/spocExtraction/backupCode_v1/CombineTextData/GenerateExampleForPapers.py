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
from LibForGraphExtractionFromRawCode import getJsonDict,getTerminalValue
import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render

def generateGraphCompact(jsonObject,strFatherLabel,arrCodes,idChange,isBlueColor,graph):
    startLine=jsonObject['startLine']
    startOffset=jsonObject['startOffset']
    endLine=jsonObject['endLine']
    endOffset=jsonObject['endOffset']
    strPosition='{}-{}-{}-{}'.format(startLine,startOffset,endLine,endOffset)
    strId=str(jsonObject['id'])
    strLabel='{}\n{}'.format(strId,jsonObject['type'])
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
            strChildLabel=generateGraphCompact(lstChildren[i],strLabel,arrCodes,idChange, isBlueColor, graph)
            if strLabel!=strChildLabel:
                graph.add_edge(strLabel,strChildLabel,color='black')
    else:
        strTerminalLabel='{}\n{}'.format('terminal_'+strId,getTerminalValue(startLine,startOffset,endLine,endOffset,arrCodes))
        graph.add_node(strTerminalLabel, color='yellow')
        graph.add_edge(strLabel, strTerminalLabel, color='black')

    return strLabel


fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopSampleGraph=fopRoot+'sampleGraphForPaper/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'



f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiteralsToValues={}
dictValuesToLiterals={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiteralsToValues[arrTabs[0]]=strContent
        dictValuesToLiterals[strContent]=arrTabs[0]

lstFopMixVersion=[]
lstFopMixVersion=sorted(glob.glob(fopSampleGraph+'*/'))
distanceHeader=33

for i in range(0,len(lstFopMixVersion)):
    fpItemJson=lstFopMixVersion[i]+'a_json.txt'
    fpItemJsonDot = lstFopMixVersion[i] + 'a_json.dot'
    fpItemJsonPng = lstFopMixVersion[i] + 'a_json.png'
    fpItemCpp=lstFopMixVersion[i]+'_a_code.cpp'
    f1=open(fpItemCpp,'r')
    arrCodes=f1.read().strip().split('\n')
    f1.close()
    f1=open(fpItemJson,'r')
    strContent=f1.read()
    f1.close()
    dictJsonAll=ast.literal_eval(strContent)
    graphItCompact = pgv.AGraph(directed=True)
    generateGraphCompact(dictJsonAll,'',arrCodes,-1,True,graphItCompact)
    graphItCompact.write(fpItemJsonDot)
    graphItCompact.layout(prog='dot')
    graphItCompact.draw(fpItemJsonPng)

    lstFopItemGraphs=sorted(glob.glob(lstFopMixVersion[i]+'v_*_graphs/'))
    lstFpItemGraph=[]
    for fop in lstFopItemGraphs:
        lstFpDot=sorted(glob.glob(fop+'*.dot'))
        for fpItem in lstFpDot:
            lstFpItemGraph.append(fpItem)

    for j in range(0,len(lstFpItemGraph)):
        fpItemMixDot=lstFpItemGraph[j]
        fpItemMixPng = lstFpItemGraph[i].replace('.dot','_compact.png')
        graphItem = pgv.AGraph(fpItemMixDot, strict=False, directed=True)
        graphItem.layout(prog='dot')
        graphItem.draw(fpItemMixPng)
    print('end {}'.format(i))





