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
from pyparsing import OneOrMore, nestedExpr

import copy
import nltk
from nltk.data import find
from bllipparser import RerankingParser
import time

def getGraphFromJsonPOS(jsonObj,graph):
    strLabel='{}\n{}\n{}'.format(jsonObj['tag'],jsonObj['value'],jsonObj['position'])
    graph.add_node(strLabel, color='red')
    if 'children' in jsonObj.keys():
        lstChildren=jsonObj['children']
        for i in range(0,len(lstChildren)):
            child=lstChildren[i]
            strChildLabel=getGraphFromJsonPOS(child,graph)
            graph.add_edge(strLabel,strChildLabel)
    return strLabel

strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fpPseudocodeAfterPOS=fopRoot+'pseudocode_after_pos_v1.txt'
fopGraph=fopRoot+'graphPOS/'
createDirIfNotExist(fopGraph)
f1=open(fpPseudocodeAfterPOS,'r')
arrAfterLines=f1.read().split('\n')
f1.close()

for i in range(0,len(arrAfterLines)):
  itemStr=arrAfterLines[i]
  arrItTabs=itemStr.split('\t')
  if len(arrItTabs)>=2:
    strJson=arrItTabs[1]
    jsonObj=ast.literal_eval(strJson)
    fpGraphDot=fopGraph+str((i+1))+'.dot'
    fpGraphPng = fopGraph + str((i + 1)) + '.png'
    graphAll = pgv.AGraph(directed=True)
    getGraphFromJsonPOS(jsonObj,graphAll)
    graphAll.write(fpGraphDot)
    graphAll.layout(prog='dot')
    graphAll.draw(fpGraphPng)
    print('end {}'.format(i))


