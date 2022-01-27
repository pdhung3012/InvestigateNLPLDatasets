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

def getAllNonTerminalNodesOfAST(jsonObject,lstAllNonTerminalNodes):
    try:
        # if indent not in dictIndents.keys():
        #     dictIndents[indent]=[]
        lstAllNonTerminalNodes.append(str(jsonObject['type']))

        if 'children' in jsonObject.keys():
            lstChildren=jsonObject['children']
            for i in range(0,len(lstChildren)):
                getAllNonTerminalNodesOfAST(lstChildren[i],lstAllNonTerminalNodes)
    except:
        traceback.print_exc

def getAllNonTerminalNodesOfPOS(jsonObject,lstAllNonTerminalNodes):
    try:
        # if indent not in dictIndents.keys():
        #     dictIndents[indent]=[]
        lstAllNonTerminalNodes.append(str(jsonObject['tag']))
        if 'children' in jsonObject.keys():
            lstChildren=jsonObject['children']
            for i in range(0,len(lstChildren)):
                getAllNonTerminalNodesOfPOS(lstChildren[i],lstAllNonTerminalNodes)
    except:
        traceback.print_exc

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
fopStep5EmbeddingModels=fopRoot+'embeddingModels/'
fopStep5TextInfo=fopStep5EmbeddingModels+'textInfo/'
fopD2vModel=fopStep5EmbeddingModels+'d2v/'
fopStep3TreesitterTokenize=fopRoot+'step3_treesitter_tokenize/'
fopStep2CodeReplaceDict=fopRoot+'step2_code_replaceDict/'
fopStep2PseudoTokenize=fopRoot+'step2_pseudo_tokenize/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
fopGraphEntityInfo=fopStep3V2+'graphEntityInfo/'
fopPOSNLTK=fopRoot+'step2_afterTranslation/sortBySimilarityScore/pos_nltk/'
fopPOSStanford=fopRoot+'step2_afterTranslation/sortBySimilarityScore/pos_stanford/'
createDirIfNotExist(fopStep5V2)
createDirIfNotExist(fopStep5EmbeddingModels)
createDirIfNotExist(fopStep5TextInfo)

lstFpPseudoFile=[]
lstFop1=sorted(glob.glob(fopStep2PseudoTokenize+'**/'),reverse=True)
for fop in lstFop1:
    lstFp2=sorted(glob.glob(fop+'*_text.txt'),reverse=True)
    for fpItem in lstFp2:
        lstFpPseudoFile.append(fpItem)

fpPseudocodeTrainEmb=fopStep5TextInfo+'pseudocode.textTrainEmb.txt'
fpCodeTrainEmb=fopStep5TextInfo+'code.textTrainEmb.txt'
fpASTTrainEmb=fopStep5TextInfo+'ast.textTrainEmb.txt'
fpPOSTrainEmb=fopStep5TextInfo+'pos.textTrainEmb.txt'

f1=open(fpPseudocodeTrainEmb,'w')
f1.write('')
f1.close()
f1=open(fpCodeTrainEmb,'w')
f1.write('')
f1.close()
f1=open(fpASTTrainEmb,'w')
f1.write('')
f1.close()

lstStrPseudocode=[]
lstStrCode=[]
lstStrASTNodeNonT=[]
lstStrNLNodeNonT=[]
for i in range(0,len(lstFpPseudoFile)):
    fpPseudoFile=lstFpPseudoFile[i]
    arrFpPseudo=fpPseudoFile.split('/')
    nameOfProgram=os.path.basename(fpPseudoFile).replace('_text.txt','')
    fpCodeFile=fopStep2CodeReplaceDict+arrFpPseudo[len(arrFpPseudo)-2]+'/'+nameOfProgram+'_code.cpp'
    fpASTFile=fopStep3TreesitterTokenize+arrFpPseudo[len(arrFpPseudo)-2]+'/'+nameOfProgram+'_code_ast.txt'
    f1=open(fpPseudoFile,'r')
    strPseudo=f1.read().strip()
    f1.close()
    lstStrPseudocode.append(strPseudo)
    f1=open(fpCodeFile,'r')
    strCode=f1.read().strip()
    f1.close()
    lstStrCode.append(strCode)
    f1 = open(fpASTFile, 'r')
    strAST = f1.read().strip().split('\n')[1]
    jsonAST=ast.literal_eval(strAST)
    f1.close()
    lstItemAST=[]
    getAllNonTerminalNodesOfAST(jsonAST,lstItemAST)
    lstStrASTNodeNonT.append(' '.join(lstItemAST))
    if((i+1)%1000==0) or (i+1)==len(lstFpPseudoFile) :
        f1 = open(fpPseudocodeTrainEmb, 'a')
        f1.write('\n'.join(lstStrPseudocode)+'\n')
        f1.close()
        f1 = open(fpCodeTrainEmb, 'a')
        f1.write('\n'.join(lstStrCode)+'\n')
        f1.close()
        f1 = open(fpASTTrainEmb, 'a')
        f1.write('\n'.join(lstStrASTNodeNonT)+'\n')
        f1.close()
        lstStrPseudocode = []
        lstStrCode = []
        lstStrASTNodeNonT = []
        print('end {} {}'.format(i,len(lstStrASTNodeNonT)))



lstFpPOSNLTK=glob.glob(fopPOSNLTK+'*.pos.txt')
lstFpPOSStanford=glob.glob(fopPOSStanford+'*.pos.txt')
lstPOSAll=lstFpPOSNLTK+lstFpPOSStanford

f1=open(fpPOSTrainEmb,'w')
f1.write('')
f1.close()
print('end for pseudocode, code and AST')
for i in range(0,len(lstPOSAll)):
    fpItem=lstPOSAll[i]
    f1=open(fpItem,'r')
    arrPOS=f1.read().strip().split('\n')
    f1.close()
    lsStrPOS=[]
    for item in arrPOS:
        if item!='{}':
            lstItemPOS=[]
            jsonAST=ast.literal_eval(item)
            getAllNonTerminalNodesOfPOS(jsonAST,lstItemPOS)
            lsStrPOS.append(' '.join(lstItemPOS))
    f1 = open(fpPOSTrainEmb, 'a')
    f1.write('\n'.join(lsStrPOS)+'\n')
    f1.close()
    print('end pos {}'.format(fpItem))


