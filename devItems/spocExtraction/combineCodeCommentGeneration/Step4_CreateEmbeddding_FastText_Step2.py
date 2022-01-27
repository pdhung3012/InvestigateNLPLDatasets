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
fopFastTextModel= fopStep5EmbeddingModels + 'fasttext-cbow/'
fpFastTextModelBin= fopFastTextModel + 'model.bin'
fpFastTextModelText= fopFastTextModel + 'model.text.txt'
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
createDirIfNotExist(fopFastTextModel)

lstFpTextFiles=glob.glob(fopStep5TextInfo+'*.textTrainEmb.txt')

lstStrTextInfo=[]
for fpItem in lstFpTextFiles:
    f1=open(fpItem,'r')
    arrTextItem=f1.read().strip().split('\n')
    f1.close()
    lstStrTextInfo=lstStrTextInfo+list(arrTextItem)

f1=open(fpFastTextModelText, 'w')
f1.write('\n'.join(lstStrTextInfo))
f1.close()

import fasttext
model = fasttext.train_unsupervised(fpFastTextModelText, model='cbow',dim=100)
model.save_model(fpFastTextModelBin)

print('end fasttext-skipgram training')


