import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('..')))
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions_RTX3090 import createDirIfNotExist,getPOSInfo,writeDictToFileText
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render
import copy
import nltk
from pathlib import Path

def getCompactLabel(strInputLabel):
    strOutLabel=''
    try:
        arrInput=strInputLabel.strip().split('\n')
        if len(arrInput)>=4:
            strOutLabel=arrInput[1]+'\n'+arrInput[2]
            # dictCompactLabels[strInputLabel]=strOutLabel
    except:
        traceback.print_exc()
    return strOutLabel


def walkGraph(graphTotal,graphItem):
    try:
        lstNodes=graphItem.nodes()
        lstEdges=graphItem.edges()
        for item in lstNodes:
            strNodeLbl=getCompactLabel(item)
            if strNodeLbl!='':
                graphTotal.add_node(strNodeLbl)
        for item in lstEdges:
            tup=item
            if len(tup)>=2:
                strSourceLbl=tup[0]
                strTargetLbl = tup[1]
                strCompactSourceLbl=getCompactLabel(strSourceLbl)
                strCompactTargetLbl = getCompactLabel(strTargetLbl)
                if strCompactSourceLbl!='' and strCompactTargetLbl!='':
                    graphTotal.add_edge(strCompactSourceLbl,strCompactTargetLbl)
    except:
        traceback.print_exc()

def walkAndGetNodeEdgeForHGT(graphItem,dictHGTNodes,dictHGTEdges,fpFileItem,strTrainTestFolder,strProgramId):
    try:
        lstNodes = graphItem.nodes()
        lstEdges = graphItem.edges()
        dictLabelOfGraphItems={}
        for item in lstNodes:
            arrNodeItem=item.split('\n')
            if len(arrNodeItem)>=3:
                strClassName=arrNodeItem[1]
                strValue=arrNodeItem[2]
                dictLabelOfGraphItems[item]=[strClassName,strValue]
                if strClassName!='' and strValue!='':
                    if strClassName not in dictHGTNodes.keys():
                        dictHGTNodes[strClassName]={}
                    else:
                        if strValue not in dictHGTNodes[strClassName].keys():
                            if strClassName=='ProgramRoot' or strClassName=='NLRoot':
                                if len(arrNodeItem) >= 5:
                                    strLabelInClassification = arrNodeItem[3]
                                    if strClassName=='ProgramRoot':
                                        strValue=strProgramId
                                    strDictValue='{}\t{}\t{}'.format(strValue,strLabelInClassification,fpFileItem)
                                    dictHGTNodes[strClassName][strValue]=strDictValue
                            else:
                                strDictValue = '{}\t{}'.format(strValue, fpFileItem)
                                dictHGTNodes[strClassName][strValue] = strDictValue
        for item in lstEdges:
            tup = item
            if len(tup) >= 2:
                strSourceLbl = tup[0]
                strTargetLbl = tup[1]
                if strSourceLbl in dictLabelOfGraphItems.keys() and strTargetLbl in dictLabelOfGraphItems.keys():
                    itemSource=dictLabelOfGraphItems[strSourceLbl]
                    itemTarget=dictLabelOfGraphItems[strTargetLbl]
                    strSourceClass=itemSource[0]
                    strSourceValue=itemSource[1]
                    strTargetClass=itemTarget[0]
                    strTargetValue=itemTarget[1]
                    strNewKey='{} - {}'.format(strSourceClass,strTargetClass)
                    if strNewKey not in dictHGTEdges.keys():
                        dictHGTEdges[strNewKey]=[]
                    else:
                        strEdgeId=strTrainTestFolder+'\t'+strProgramId
                        tupItem=(strSourceValue,strTargetValue,strEdgeId)
                        dictHGTEdges[strNewKey].append(tupItem)
    except:
        traceback.print_exc()

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopMixVersion=fopRoot+'step4_mixCode/'
fopTotalGraphAll= fopRoot + 'step5_totalGraph/all/'
fpFileCachedVersion=fopRoot+'cached_graph_all.txt'
fpDotTotalGraph= fopTotalGraphAll + 'total.all.dot'
fpPngTotalGraph= fopTotalGraphAll + 'total.all.png'

createDirIfNotExist(fopTotalGraphAll)

dictTotalElements={}

lstFpVersionFiles=[]
if not os.path.isfile(fpFileCachedVersion):
    print('before traverse')
    lstFop1=sorted(glob.glob(fopMixVersion+'*/'))
    for fop1 in lstFop1:
        lstFop2=sorted(glob.glob(fop1+'*/'))
        for fop2 in lstFop2:
            lstFp3=sorted(glob.glob(fop2+'v_*_graphs/g_all.dot'))
            # print(fp3)
            for fp3 in lstFp3:
                lstFpVersionFiles.append(fp3)
        print('end {}'.format(fop1))
    # sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
    print('after {} '.format(len(lstFpVersionFiles)))
    f1=open(fpFileCachedVersion,'w')
    f1.write('\n'.join(lstFpVersionFiles))
    f1.close()
else:
    f1 = open(fpFileCachedVersion, 'r')
    lstFpVersionFiles=f1.read().strip().split('\n')
    f1.close()
lstFpVersionFiles=sorted(lstFpVersionFiles,reverse=True)
graphAll=pgv.AGraph(directed=True)
dictHGTNodes={}
dictHGTEdges={}

for i in range(0,len(lstFpVersionFiles)):
    try:
        fpItemVersionDot=lstFpVersionFiles[i]
        arrFpIntem=fpItemVersionDot.split('/')
        strProgramId='ProgramRoot_'+arrFpIntem[len(arrFpIntem)-3]+'-'+arrFpIntem[len(arrFpIntem)-2].replace('_graphs','')
        strTrainTestFolder=arrFpIntem[len(arrFpIntem)-4]
        graphItem = pgv.AGraph(fpItemVersionDot, strict=False, directed=True)
        walkGraph(graphAll,graphItem)
        walkAndGetNodeEdgeForHGT(graphItem, dictHGTNodes, dictHGTEdges, fpItemVersionDot,strTrainTestFolder,strProgramId)
        if i==10:
            graphAll.write(fpDotTotalGraph)
            graphAll.layout(prog='dot')
            graphAll.draw(fpPngTotalGraph)
            break
    except:
        traceback.print_exc()
print('end visit graphs')
for key in dictHGTNodes.keys():
    dictElement=dictHGTNodes[key]
    fpElement=fopTotalGraphAll+'nodes_'+key+'.txt'
    lstStr=[]
    for objInGraph in dictElement.keys():
        strItem=dictElement[objInGraph]
        lstStr.append(strItem)
    f1=open(fpElement,'w')
    f1.write('\n'.join(lstStr))
    f1.close()
print('end save nodes')
for key in dictHGTEdges.keys():
    lstElements=dictHGTEdges[key]
    fpElement = fopTotalGraphAll + 'edges_' + key + '.txt'
    lstStr = []
    for objInGraph in lstElements:
        strItem = '\t'.join(list(objInGraph))
        lstStr.append(strItem)
    f1 = open(fpElement, 'w')
    f1.write('\n'.join(lstStr))
    f1.close()
print('end save edges')

