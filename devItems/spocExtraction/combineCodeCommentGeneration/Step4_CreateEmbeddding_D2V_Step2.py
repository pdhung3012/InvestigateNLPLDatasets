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
fopD2vModel=fopStep5EmbeddingModels+'d2v/'
fpD2VModelBin=fopD2vModel+'model.bin'
fpD2VModelText=fopD2vModel+'model.text.txt'
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
createDirIfNotExist(fopD2vModel)

lstFpTextFiles=glob.glob(fopStep5TextInfo+'*.textTrainEmb.txt')

lstStrTextInfo=[]
for fpItem in lstFpTextFiles:
    f1=open(fpItem,'r')
    arrTextItem=f1.read().strip().split('\n')
    f1.close()
    lstStrTextInfo=lstStrTextInfo+list(arrTextItem)

f1=open(fpD2VModelText,'w')
f1.write('\n'.join(lstStrTextInfo))
f1.close()

tagged_data = [TaggedDocument(words=word_tokenize(_d), tags=[str(i)]) for i, _d in enumerate(lstStrTextInfo)]
max_epochs = 20
vec_size = 100
alpha = 0.025

model = Doc2Vec(vector_size=vec_size,
                alpha=alpha,
                min_alpha=0.00025,
                min_count=1,
                dm=0)

model.build_vocab(tagged_data)

for epoch in range(max_epochs):
    # print('iteration {0}'.format(epoch))
    model.train(tagged_data,
                total_examples=model.corpus_count,
                epochs=model.epochs)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha
    print('End epoch{}'.format(epoch))
model.save(fpD2VModelBin)
print('end doc2vec training')


