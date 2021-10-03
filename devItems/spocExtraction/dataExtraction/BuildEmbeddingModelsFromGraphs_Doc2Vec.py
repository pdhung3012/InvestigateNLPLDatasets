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
import copy
import ast

def walkASTJson(jsonAST,lstStrASTs):
    if 'type' in jsonAST.keys():
        lstStrASTs.append(jsonAST['type'])
    if 'children' in jsonAST.keys():
        lstChildren=jsonAST['children']
        for i in range(0,len(lstChildren)):
            walkASTJson(lstChildren[i],lstStrASTs)

def walkPOSJson(jsonPOS,lstStrPOSs):
    if 'tag' in jsonPOS.keys():
        lstStrPOSs.append(jsonPOS['tag'])
    if 'children' in jsonPOS.keys():
        lstChildren=jsonPOS['children']
        for i in range(0,len(lstChildren)):
            walkPOSJson(lstChildren[i],lstStrPOSs)

# create training vector for token: code and text

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopPOSModel=fopRoot+'embeddingModels/d2v/'
fopDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
fopStep4=fopRoot+'step4_mixCode/'
fpPOSJson=fopRoot+''
fpFileCachedPseudocode=fopRoot+'cached_fp_pseudocode.txt'
fpFileCachedCode=fopRoot+'cached_fp_code.txt'
fpFileCachedAST=fopRoot+'cached_fp_ast.txt'
fpJsonPseudoAfterPOS=fopRoot+'pseudocode_after_pos.txt'
fpCachedPOS=fopPOSModel+'cached_pos.txt'
fpCachedPseudocode=fopPOSModel+'cached_pseudocode.txt'
fpCachedCode=fopPOSModel+'cached_code.txt'
fpCachedAST=fopPOSModel+'cached_ast.txt'
fpD2VModel=fopPOSModel+'d2v.model.txt'

f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiteralsToValues={}
dictValuesToLiterals={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiteralsToValue[arrTabs[0]]=strContent
        dictValuesToLiterals[strContent]=arrTabs[0]


lstFpPseudocode=[]
lstFpCode=[]
lstFpAST=[]
if not os.path.isfile(fpFileCachedPseudocode):
    print('before traverse')
    lstFop1=sorted(glob.glob(fopMixVersion+'*/'))
    for fop1 in lstFop1:
        lstFop2=sorted(glob.glob(fop1+'*/'))
        for fop2 in lstFop2:
            fp3Pseudocode=fop2+'_a_pseudo.txt'
            fp3Code=fop2+'_a_code.cpp'
            fp3AST=fop2+'a_json.txt'
            lstFpPseudocode.append(fp3Pseudocode)
            lstFpCode.append(fp3Code)
            lstFpAST.append(fp3AST)
        print('end {}'.format(fop1))
    # sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
    print('after {} '.format(len(lstFpPseudocode)))
    f1=open(fpFileCachedPseudocode,'w')
    f1.write('\n'.join(lstFpPseudocode))
    f1.close()
    f1=open(fpFileCachedCode,'w')
    f1.write('\n'.join(lstFpCode))
    f1.close()
    f1=open(fpFileCachedAST,'w')
    f1.write('\n'.join(lstFpAST))
    f1.close()
else:
    f1=open(fpFileCachedPseudocode,'r')
    lstFpPseudocode=f1.read().split('\n')
    f1.close()
    f1=open(fpFileCachedCode,'r')
    lstFpCode=f1.read().split('\n')
    f1.close()
    f1=open(fpFileCachedAST,'r')
    lstFpAST=f1.read().split('\n')
    f1.close()

f1=open(fpCachedPseudocode,'w')
f1.write('')
f1.close()
for i in range(0,len(lstFpPseudocode)):
    fpItemI=lstFpPseudocode[i]
    f1=open(fpItemI,'r')
    arrItems=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpCachedPseudocode, 'a')
    f1.write('\n'.join(arrItems)+'\n')
    f1.close()


f1=open(fpCachedCode,'w')
f1.write('')
f1.close()
lstDictLiteralKey=sorted(dictValuesToLiterals,reverse=True)
for i in range(0,len(lstFpCode)):
    fpItemI=lstFpCode[i]
    f1=open(fpItemI,'r')
    arrItems=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpCachedCode, 'a')
    f1.write('\n'.join(arrItems)+'\n')
    f1.close()
    lstStrItemCode=[]
    for j in range(33,len(arrItems)):
        item=arrItems[j]
        for key in lstDictLiteralKey:
            if key in item:
                valKey=dictValuesToLiterals[key]
                item=item.replace(key,valKey)
        lstStrItemCode.append(item)
    f1 = open(fpCachedPseudocode, 'a')
    f1.write('\n'.join(lstStrItemCode) + '\n')
    f1.close()

f1=open(fpCachedAST,'w')
f1.write('')
f1.close()
# lstDictLiteralKey=sorted(dictValuesToLiterals,reverse=True)
for i in range(0,len(lstFpAST)):
    fpItemI=lstFpAST[i]
    f1=open(fpItemI,'r')
    strJsonAST=f1.read().strip().split('\n')[0]
    f1.close()
    jsonAST=ast.literal_eval(strJsonAST)
    lstStrASTs=[]
    walkASTJson(jsonAST,lstStrASTs)
    strASTsLine=' '.join(lstStrASTs)
    f1 = open(fpCachedAST, 'a')
    f1.write(strASTsLine+'\n')
    f1.close()

f1=open(fpPOSJson,'r')
arrPOSJson=fpPOSJson.read().split('\n')
f1.close()

f1=open(fpCachedPOS,'w')
f1.write('')
f1.close()
# lstDictLiteralKey=sorted(dictValuesToLiterals,reverse=True)
for i in range(0,len(arrPOSJson)):
    strItemI=arrPOSJson[i]
    strJsonPOS=strItemI.split('\t')[1]
    f1.close()
    jsonPOS=ast.literal_eval(strJsonPOS)
    lstStrPOSs=[]
    walkPOSJson(jsonPOS,lstStrPOSs)
    strPOSsLine=' '.join(lstStrPOSs)
    f1 = open(fpCachePOS, 'a')
    f1.write(strPOSsLine+'\n')
    f1.close()

print('prepare for the Doc2VecTraining')
f1=open(fpCachedPseudocode,'r')
arrOutPseudocode=f1.read().split('\n')
f1.close()
f1=open(fpCachedCode,'r')
arrOutCode=f1.read().split('\n')
f1.close()
f1=open(fpCachedAST,'r')
arrOutAST=f1.read().split('\n')
f1.close()
f1=open(fpCachedPOS,'r')
arrOutPOS=f1.read().split('\n')
f1.close()

lstAllInputTexts=arrOutPseudocode+arrOutCode+arrOutPOS+arrOutPOS
print('len all text{}'.format(len(lstAllInputTexts)))
tagged_data = [TaggedDocument(words=word_tokenize(_d), tags=[str(i)]) for i, _d in enumerate(lstAllInputTexts)]
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
model.save(fpD2VModel)
print('end doc2vec training')





# for item: generaate vector of text and code