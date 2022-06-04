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
strEndLineChar='_EL_'
strEndFileChar='_EF_'
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '



fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep4NMT=fopRoot+'step4_Inconsistent_v2/'
fopStep3V2=fopRoot+'step3_v2/'
fopStep3TreesitterTokenize=fopRoot+'step3_treesitter_tokenize/'
fopStep2Tokenize=fopRoot+'step2_tokenize/'
fopStep2PseudoTokenize=fopRoot+'step2_pseudo_tokenize/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
fopOutGraphConsistent=fopStep3V2+'graphEntityInfo-Consistent/'
fopOutGraphInconsistent=fopStep3V2+'graphEntityInfo-Inconsistent/'
createDirIfNotExist(fopOutGraphConsistent)
createDirIfNotExist(fopOutGraphInconsistent)
createDirIfNotExist(fopStep4NMT)

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

lstNumContexts=[0]
lstPOSType=['stanford']

dictContextAndPOS={}
for itContext in lstNumContexts:
    for pos in lstPOSType:
        strKey='context_{}_pos_{}'.format(itContext,pos)
        # f1=open(fopOutGraph+strKey+'.txt','w')
        # f1.write('')
        # f1.close()
        dictContextAndPOS[strKey]=[]

dictIncContextAndPOS={}
for itContext in lstNumContexts:
    for pos in lstPOSType:
        strKey='context_{}_pos_{}'.format(itContext,pos)
        # f1=open(fopOutGraph+strKey+'.txt','w')
        # f1.write('')
        # f1.close()
        dictIncContextAndPOS[strKey]=[]


arrFinalCodes=None
arrFinalPseudocodes=None
arrJsonAST=None
jsonAll=None
dictOfFatherIdMainAST = {}
prevProgramId=''
for i in range(0,len(arrLocs)):
    # if (i+1)<=36000:
    #     continue
    arrTabLocs=arrLocs[i].split('\t')
    # strTrainTestFolder=arrTabLocs[1]
    # strRootProgramId=arrTabLocs[0]
    linePseudocodeProgram=int(arrTabLocs[2])
    lineInRealCode=linePseudocodeProgram-1+distanceHeader
    # print('line in real {}'.format(lineInRealCode))
    # input('aaa')
    # fpItemAST=fopStep3TreesitterTokenize+strTrainTestFolder+'/'+strRootProgramId+'_code_ast.txt'
    # fpItemCode = fopStep2Tokenize + strTrainTestFolder + '/' + strRootProgramId + '_code.cpp'
    # fpItemFinalPseudocode = fopStep2PseudoTokenize+strTrainTestFolder+'/'+strRootProgramId + '_text.txt'
    # fopOutputItem=fopStep4NMT+strTrainTestFolder+'__'+strRootProgramId+'__'+str(lineInRealCode+1)+'/'
    # createDirIfNotExist(fopOutputItem)
    # fpCodeLogOutput = fopOutputItem + 'a_logPrint.txt'
    # fpOutMixCode = fopOutputItem + 'a_mixCode.cpp'
    # fpOutExpectedCode = fopOutputItem + 'a_expectedCode.cpp'
    # sys.stdout = open(fpCodeLogOutput, 'w')

    # if strRootProgramId!=prevProgramId:
    #     f1 = open(fpItemCode, 'r')
    #     arrFinalCodes = f1.read().strip().split('\n')
    #     f1.close()
    #     f1 = open(fpItemFinalPseudocode, 'r')
    #     arrFinalPseudocodes = f1.read().strip().split('\n')
    #     f1.close()
    #     f1 = open(fpItemAST, 'r')
    #     arrJsonAST = f1.read().strip().split('\n')
    #     f1.close()

    for key in dictContextAndPOS.keys():
        fpGraphKey=fopStep4NMT+arrTabLocs[1]+'__'+arrTabLocs[0]+'__'+str(lineInRealCode+1)+'/graphCorrect_'+key+'.dot'
        strGraph=''
        f1=open(fpGraphKey,'r')
        arrGraph=f1.read().strip().split('\n')
        strGraph=strEndLineChar.join(arrGraph)
        f1.close()
        print('{} {}'.format((i+1),key))
        dictContextAndPOS[key].append(strGraph)

    for key in dictIncContextAndPOS.keys():
        fpGraphKey=fopStep4NMT+arrTabLocs[1]+'__'+arrTabLocs[0]+'__'+str(lineInRealCode+1)+'/graphIncorrect_'+key+'.dot'
        strGraph=''
        f1=open(fpGraphKey,'r')
        arrGraph=f1.read().strip().split('\n')
        strGraph=strEndLineChar.join(arrGraph)
        f1.close()
        print('{} {}'.format((i+1),key))
        dictIncContextAndPOS[key].append(strGraph)

    # sys.stdout.close()
    # sys.stdout = sys.__stdout__
    # prevProgramId=strRootProgramId
    # input('need check here ')

    if (i+1)%1000==0 or (i==len(arrLocs)-1) :
        batchNum=str((i+1)//1000)
        if i==len(arrLocs)-1 and (i+1)%1000!=0:
            batchNum = str((i + 1) // 1000+1)

        for key in dictContextAndPOS.keys():
            createDirIfNotExist(fopOutGraphConsistent+key+'/')
            fpOutputKey=fopOutGraphConsistent+key+'/'+batchNum+'.txt'
            f1=open(fpOutputKey,'w')
            f1.write('\n'.join(dictContextAndPOS[key])+'\n')
            f1.close()
            dictContextAndPOS[key].clear()
        print('end {}/{} {}'.format(i, len(arrLocs), len(dictContextAndPOS[key])))
        for key in dictIncContextAndPOS.keys():
            createDirIfNotExist(fopOutGraphInconsistent+key+'/')
            fpOutputKey=fopOutGraphInconsistent+key+'/'+batchNum+'.txt'
            f1=open(fpOutputKey,'w')
            f1.write('\n'.join(dictIncContextAndPOS[key])+'\n')
            f1.close()
            dictIncContextAndPOS[key].clear()
