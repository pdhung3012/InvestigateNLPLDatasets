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

def walkAndGetNodeEdgeForHGT(graphItem,dictHGTNodes,dictHGTEdges,dictValuesToLiterals,strProgramIdAndTrainTestFolder):
    try:
        lstNodes = graphItem.nodes()
        lstEdges = graphItem.edges()
        dictLabelOfGraphItems={}
        for item in lstNodes:
            arrNodeItem=item.split('\n')
            if len(arrNodeItem)>=3:
                strClassName=arrNodeItem[0]
                strValue=arrNodeItem[len(arrNodeItem)-1]
                dictLabelOfGraphItems[item]=[strClassName,strValue]
                if strClassName!='' and strValue!='':
                    if strClassName not in dictHGTNodes.keys():
                        dictHGTNodes[strClassName]={}
                    if strClassName=='ASTNode':
                        strItem=strValue
                        if strItem in dictValuesToLiterals.keys():
                            strValue=dictValuesToLiterals[strItem]
                            # print('here {}'.format(strValue))

                    if strValue not in dictHGTNodes[strClassName].keys():
                        if strClassName=='ProgramRoot' or strClassName=='NLRoot':
                            if len(arrNodeItem) >= 3:
                                # strLabelInClassification = arrNodeItem[3]
                                if strClassName=='ProgramRoot':
                                    strValue=strProgramIdAndTrainTestFolder
                                strNodeId = strProgramIdAndTrainTestFolder
                                strDictValue='{}{}{}'.format(strValue,strSplitCharacterForNodeEdge,strNodeId)
                                dictHGTNodes[strClassName][strValue]=strDictValue
                        else:
                            dictHGTNodes[strClassName][strValue] = strValue
        for item in lstEdges:
            tup = item
            if len(tup) >= 2:
                strSourceLbl = tup[0]
                strTargetLbl = tup[1]
                if strSourceLbl in dictLabelOfGraphItems.keys() and strTargetLbl in dictLabelOfGraphItems.keys():
                    itemSource = dictLabelOfGraphItems[strSourceLbl]
                    itemTarget = dictLabelOfGraphItems[strTargetLbl]
                    strSourceClass = itemSource[0]
                    strSourceValue = itemSource[1]
                    if strSourceClass == 'translation_unit':
                        strSourceValue = strProgramIdAndTrainTestFolder
                    strTargetClass = itemTarget[0]
                    strTargetValue = itemTarget[1]
                    strNewKey = '{} - {}'.format(strSourceClass, strTargetClass)
                    if strNewKey not in dictHGTEdges.keys():
                        dictHGTEdges[strNewKey] = []
                        strEdgeId = strProgramIdAndTrainTestFolder
                        tupItem = (strSourceValue, strTargetValue, strEdgeId)
                        dictHGTEdges[strNewKey].append(tupItem)
                    else:
                        strEdgeId = strProgramIdAndTrainTestFolder
                        tupItem = (strSourceValue, strTargetValue, strEdgeId)
                        dictHGTEdges[strNewKey].append(tupItem)

    except:
        traceback.print_exc()


strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar='_EL_'
strEndFileChar='_EF_'
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
strSplitCharacterForNodeEdge = '_ABAZ_'



fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep3V2=fopRoot+'step3_v2/'
fopStep5V2=fopRoot+'step5_v2_HGT/'
fopStep3TreesitterTokenize=fopRoot+'step3_treesitter_tokenize/'
fopStep2Tokenize=fopRoot+'step2_tokenize/'
fopStep2PseudoTokenize=fopRoot+'step2_pseudo_tokenize/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
fopGraphEntityInfo=fopStep3V2+'graphEntityInfo/'
createDirIfNotExist(fopStep5V2)

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
# arrPOSNLTK=dictFolderContent[fnPOSNLTK]
# arrPOSStanford=dictFolderContent[fnPOSStanford]

lstNumContexts=[1,3,5,1000]
lstPOSType=['nltk','stanford']

dictContextAndPOS={}
for itContext in lstNumContexts:
    for pos in lstPOSType:
        strKey='context_{}_pos_{}'.format(itContext,pos)
        # f1=open(fopOutGraph+strKey+'.txt','w')
        # f1.write('')
        # f1.close()
        dictContextAndPOS[strKey]=[]

arrFinalCodes=None
arrFinalPseudocodes=None
arrJsonAST=None
jsonAll=None
dictOfFatherIdMainAST = {}
prevProgramId=''
arrCurrentGraphPOS=[]
fpGraphTemp=fopStep5V2+'graph_temp.txt'
for context in lstNumContexts:
    for pos in lstPOSType:
        fonContextAndPOS='context_{}_pos_{}'.format(context,pos)
        fopStep5ContextPOS=fopStep5V2+fonContextAndPOS+'/'
        fpLogErrorFile=fopStep5ContextPOS+'log_error.txt'
        createDirIfNotExist(fopStep5ContextPOS)
        dictHGTNodes = {}
        dictHGTEdges = {}
        prevGraphFile = ''
        f1=open(fpLogErrorFile,'w')
        f1.write('')
        f1.close()
        for i in range(0,len(arrLocs)):
            arrTabLocs=arrLocs[i].split('\t')
            # strTrainTestFolder=arrTabLocs[1]
            # strRootProgramId=arrTabLocs[0]
            linePseudocodeProgram=int(arrTabLocs[2])
            lineInRealCode=linePseudocodeProgram-1+distanceHeader
            currentGraphFile=(i+1+1000)//1000
            currentGraphIndex=i%1000
            strProgramIdAndTrainTestFolder = arrTabLocs[1] + '__' + arrTabLocs[0] + '__' + arrTabLocs[2]
            if currentGraphFile!=prevGraphFile:
                f1=open(fopGraphEntityInfo+fonContextAndPOS+'/'+str(currentGraphFile)+'.txt','r')
                arrCurrentGraphPOS=f1.read().strip().split('\n')
                f1.close()

                # f1 = open(fopGraphEntityInfo + fonContextAndPOS + '/38.txt', 'r')
                # arrCurrentGraphPOS = f1.read().strip().split('\n')
                # f1.close()
                # print('print size current {}'.format(len(arrCurrentGraphPOS)))
                # input('size')

            try:

                strGraphContent=arrCurrentGraphPOS[currentGraphIndex].replace(strEndLineChar,'\n')
                f1=open(fpGraphTemp,'w')
                f1.write(strGraphContent)
                f1.close()
                # strProgramId = 'ProgramRoot_' + arrFpIntem[len(arrFpIntem) - 3] + '-' + arrFpIntem[
                #     len(arrFpIntem) - 2].replace('_graphs', '')
                # strTrainTestFolder = arrFpIntem[len(arrFpIntem) - 4]

                graphItem = pgv.AGraph(fpGraphTemp, strict=False, directed=True)
                # walkGraph(graphAll, graphItem)
                walkAndGetNodeEdgeForHGT(graphItem, dictHGTNodes, dictHGTEdges, dictValuesToLiterals,strProgramIdAndTrainTestFolder)
                # if i == 10:
                #     graphAll.write(fpDotTotalGraph)
                #     graphAll.layout(prog='dot')
                #     graphAll.draw(fpPngTotalGraph)
                if ((i + 1) % 1000 == 0) or ((i + 1) == len(arrLocs)):
                    print('{} end {}'.format(fonContextAndPOS,(i + 1)))
                # if i==1000:
                #     break
            except:
                f1=open(fpLogErrorFile,'a')
                f1.write(strProgramIdAndTrainTestFolder+'\n')
                f1.close()
                traceback.print_exc()
            prevGraphFile=currentGraphFile
        print('end visit graphs')
        for key in dictHGTNodes.keys():
            dictElement = dictHGTNodes[key]
            fpElement = fopStep5ContextPOS + 'nodes_' + key + '.txt'
            lstStr = []
            for objInGraph in dictElement.keys():
                strItem = dictElement[objInGraph]
                lstStr.append(strItem)
            f1 = open(fpElement, 'w')
            f1.write('\n'.join(lstStr))
            f1.close()
        print('end save nodes')
        for key in dictHGTEdges.keys():
            lstElements = dictHGTEdges[key]
            fpElement = fopStep5ContextPOS + 'edges_' + key + '.txt'
            lstStr = []
            for objInGraph in lstElements:
                strItem = strSplitCharacterForNodeEdge.join(list(objInGraph))
                lstStr.append(strItem)
            f1 = open(fpElement, 'w')
            f1.write('\n'.join(lstStr))
            f1.close()
    print('end save edges')

