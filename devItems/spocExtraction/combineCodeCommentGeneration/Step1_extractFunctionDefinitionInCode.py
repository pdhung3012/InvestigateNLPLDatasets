import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('../..')))
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
from nltk.data import find
from bllipparser import RerankingParser
import nltk
from pyparsing import OneOrMore, nestedExpr
from nltk.tokenize import word_tokenize,sent_tokenize
from pycorenlp import StanfordCoreNLP
from sklearn.feature_extraction.text import TfidfVectorizer


def getLstFunctionDecl(jsonObject,lstFunctionDecl):
    # print(jsonObject)
    if str(jsonObject['type'])=='function_definition':
        # print('go he')
        lstFunctionDecl.append(jsonObject)
    if 'children' in jsonObject.keys():
        lstChildren=jsonObject['children']
        for i in range(0,len(lstChildren)):
            getLstFunctionDecl(lstChildren[i],lstFunctionDecl)



fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fopInputASTTreeSitter=fopRoot+'step3_treesitter_tokenize/'
fopInputSortBySimilarityScore=fopInputAfterTranslation+'sortBySimilarityScore/'

fpCacheTreeSitter=fopInputSortBySimilarityScore+'cache_step3_treesitter.txt'
fpFunctionDeclLog=fopInputSortBySimilarityScore+'function_declarations.txt'

lstFpAST=[]

if not os.path.isfile(fpCacheTreeSitter):

    lstFopAST=sorted(glob.glob(fopInputASTTreeSitter+'/**/'),reverse=True)
    print('go here {}'.format(lstFopAST))
    for fopItem in lstFopAST:
        lstFpItem=sorted(glob.glob(fopItem+'*_code_ast.txt'),reverse=True)
        for fpItem in lstFpItem:
            lstFpAST.append(fpItem)
    f1=open(fpCacheTreeSitter,'w')
    f1.write('\n'.join(lstFpAST))
    f1.close()
else:
    f1 = open(fpCacheTreeSitter, 'r')
    lstFpAST=f1.read().strip().split('\n')
    f1.close()

f1=open(fpFunctionDeclLog,'w')
f1.write('')
f1.close()

lstAllFuncDecls=[]
for i in range(0,len(lstFpAST)):
    try:
        fpItem=lstFpAST[i]
        arrFpItem=fpItem.split('/')
        strFileAndFolder=arrFpItem[len(arrFpItem)-1].replace('_code_ast.txt','')+'\t'+arrFpItem[len(arrFpItem)-2]
        # print('begin {} {}'.format(i, fpItem))
        f1=open(fpItem,'r')
        strAST=f1.read().strip().split('\n')[1]
        jsonItem=ast.literal_eval(strAST)
        lstFuncDecls=[]
        getLstFunctionDecl(jsonItem,lstFuncDecls)

        lstBeginEnd=[]
        for item in lstFuncDecls:
            lstSubItem=[int(item['startLine']),int(item['endLine'])]
            lstBeginEnd.append(lstSubItem)

        lstAllFuncDecls.append('{}\t{}'.format(strFileAndFolder,str(lstBeginEnd)))

        if (i+1)%100==0 or i==len(lstFpAST)-1:
            if len(lstAllFuncDecls)>0:
                f1=open(fpFunctionDeclLog,'a')
                f1.write('\n'.join(map(str,lstAllFuncDecls))+'\n')
                f1.close()
                lstAllFuncDecls=[]
                print('end {} {}'.format(i,fpItem))
    except:
        traceback.print_exc()































