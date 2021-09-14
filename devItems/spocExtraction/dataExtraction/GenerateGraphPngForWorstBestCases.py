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

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopResultMLs=fopRoot+'step6_resultMLs/'

lstMLResultsFolders=glob.glob(fopResultMLs+'*/')
numTests=100

for fopResultItem in lstMLResultsFolders:
    fpItemTestP=fopResultItem+'resultTestP.txt'
    fpItemTestW = fopResultItem + 'resultTestW.txt'
    f1=open(fpItemTestP,'r')
    arrTestLines=f1.read().strip().split('\n')
    f1.close()
    for i in range(0,numTests):
        arrTabs=arrTestLines[i].split('\t')
        try:
            fpDot=arrTabs[3]+'/'+arrTabs[4]+'_graph.dot'
            fpPng = arrTabs[3] + '/' + arrTabs[4] + '_graph.png'
            (graphPydot,) = pydot.graph_from_dot_file(fpDot)
            graphPydot.write_png(fpPng)
        except:
            traceback.print_exc()
        print('end {} {}'.format(i,arrTestLines[i]))
    for i in range(len(arrTestLines)-1-numTests,len(arrTestLines)):
        arrTabs=arrTestLines[i].split('\t')
        try:
            fpDot=arrTabs[3]+'/'+arrTabs[4]+'_graph.dot'
            fpPng = arrTabs[3] + '/' + arrTabs[4] + '_graph.png'
            (graphPydot,) = pydot.graph_from_dot_file(fpDot)
            graphPydot.write_png(fpPng)
        except:
            traceback.print_exc()
        print('end {} {}'.format(i,arrTestLines[i]))

    f1=open(fpItemTestW,'r')
    arrTestLines=f1.read().strip().split('\n')
    f1.close()
    for i in range(0,numTests):
        arrTabs=arrTestLines[i].split('\t')
        try:
            fpDot=arrTabs[3]+'/'+arrTabs[4]+'_graph.dot'
            fpPng = arrTabs[3] + '/' + arrTabs[4] + '_graph.png'
            (graphPydot,) = pydot.graph_from_dot_file(fpDot)
            graphPydot.write_png(fpPng)
        except:
            traceback.print_exc()
        print('end {} {}'.format(i,arrTestLines[i]))
    for i in range(len(arrTestLines)-1-numTests,len(arrTestLines)):
        arrTabs=arrTestLines[i].split('\t')
        try:
            fpDot=arrTabs[3]+'/'+arrTabs[4]+'_graph.dot'
            fpPng = arrTabs[3] + '/' + arrTabs[4] + '_graph.png'
            (graphPydot,) = pydot.graph_from_dot_file(fpDot)
            graphPydot.write_png(fpPng)
        except:
            traceback.print_exc()
        print('end {} {}'.format(i,arrTestLines[i]))

