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
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import fasttext


strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar='_EL_'
strEndFileChar='_EF_'
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
strSplitCharacterForNodeEdge = '_ABAZ_'

def getVector(model,strInput):
    vectorItem = model.get_sentence_vector(strInput)
    strVector = ' '.join(map(str, vectorItem))
    return strVector

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep3V2=fopRoot+'step3_v2/'
fopStep5V2=fopRoot+'step5_v2_HGT/'
fopStep5EmbeddingModels=fopRoot+'embeddingModels/'
fopStep5TextInfo=fopStep5EmbeddingModels+'textInfo/'
fopVectorModel= fopStep5EmbeddingModels + 'fasttext-cbow/'
fpModelBin= fopVectorModel + 'model.bin'
fpModelText= fopVectorModel + 'model.text.txt'
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
createDirIfNotExist(fopVectorModel)

lstFpTextFiles=glob.glob(fopStep5TextInfo+'*.textTrainEmb.txt')

lstStrTextInfo=[]
setVocabs=set()
for fpItem in lstFpTextFiles:
    f1=open(fpItem,'r')
    arrTextItem=f1.read().strip().split('\n')
    f1.close()
    for line in arrTextItem:
        arrWords=line.split()
        for word in arrWords:
            setVocabs.add(word)
    lstStrTextInfo=lstStrTextInfo+list(arrTextItem)


f1=open(fpModelText, 'w')
f1.write('\n'.join(lstStrTextInfo))
f1.close()

model=fasttext.FastText.load_model(fpModelBin)

lstFpStep3V2=glob.glob(fopStep3V2+'*.txt')
dictAllFilesInput={}
for fpItem in lstFpStep3V2:
    nameItem=os.path.basename(fpItem)
    f1=open(fpItem,'r')
    arrLines=f1.read().strip().split('\n')
    f1.close()
    dictAllFilesInput[nameItem]=arrLines

fnLocation='location.txt'
fpOutNLRootTextEmb=fopVectorModel+ 'NLRoot.textForEmb.txt'
fpOutNLRootVectorEmb=fopVectorModel+ 'NLRoot.vectorForEmb.txt'
fpOutProgramRootTextEmb=fopVectorModel+ 'ProgramRoot.textForEmb.txt'
fpOutProgramRootVectorEmb=fopVectorModel+ 'ProgramRoot.vectorForEmb.txt'
fpOutNodeVectorEmb=fopVectorModel+ 'Node.vectorForEmb.txt'

lstStrVector=[]
for item in setVocabs:
    strVector = getVector(model, item)
    lstStrVector.append(item+'\t'+strVector)
f1=open(fpOutNodeVectorEmb,'w')
f1.write('\n'.join(lstStrVector))
f1.close()

arrLocs=dictAllFilesInput[fnLocation]
prevId=''
arrItemPseudoCode=None
arrItemCode=None
lstNLRootText=[]
lstNLRootVector=[]
lstProgramRootText=[]
lstProgramRootVector=[]
f1=open(fpOutProgramRootTextEmb,'w')
f1.write('')
f1.close()
f1=open(fpOutProgramRootVectorEmb,'w')
f1.write('')
f1.close()
f1=open(fpOutNLRootTextEmb,'w')
f1.write('')
f1.close()
f1=open(fpOutNLRootVectorEmb,'w')
f1.write('')
f1.close()

for i in range(0,len(arrLocs)):
    arrTabLocs=arrLocs[i].split('\t')
    fpItemPseuddocode=fopStep2PseudoTokenize+arrTabLocs[1]+'/'+arrTabLocs[0]+'_text.txt'
    fpItemCode = fopStep2CodeReplaceDict + arrTabLocs[1] + '/' + arrTabLocs[0] + '_code.cpp'
    if arrTabLocs[0]!=prevId:
        f1=open(fpItemPseuddocode,'r')
        arrItemPseudoCode=f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemCode, 'r')
        arrItemCode = f1.read().strip().split('\n')
        f1.close()
    lstMixCode=copy.deepcopy(list(arrItemCode))
    linePseudocode=int(arrTabLocs[2])-1
    lstMixCode[linePseudocode]='// '+arrItemPseudoCode[linePseudocode]
    strItemProgramRoot=strEndLineChar.join(lstMixCode)
    strItemNLRoot=arrItemPseudoCode[linePseudocode]

    strVectorMix=getVector(model,' '.join(lstMixCode))
    strVectorPseudocode=getVector(model,arrItemPseudoCode[linePseudocode])
    lstProgramRootText.append(strItemProgramRoot)
    lstProgramRootVector.append(arrLocs[i]+'\t'+strVectorMix)
    lstNLRootText.append(strItemNLRoot)
    lstNLRootVector.append(arrLocs[i]+'\t'+strVectorPseudocode)

    if (i+1)%1000==0 or (i+1)==len(arrLocs):
        f1 = open(fpOutProgramRootTextEmb, 'a')
        f1.write('\n'.join(lstProgramRootText) + '\n')
        f1.close()
        f1 = open(fpOutProgramRootVectorEmb, 'a')
        f1.write('\n'.join(lstProgramRootVector) + '\n')
        f1.close()
        f1 = open(fpOutNLRootTextEmb, 'a')
        f1.write('\n'.join(lstNLRootText) + '\n')
        f1.close()
        f1 = open(fpOutNLRootVectorEmb, 'a')
        f1.write('\n'.join(lstNLRootVector) + '\n')
        f1.close()
        lstNLRootText = []
        lstNLRootVector = []
        lstProgramRootText = []
        lstProgramRootVector = []

    prevId=arrTabLocs[0]





print('end generate vector')


