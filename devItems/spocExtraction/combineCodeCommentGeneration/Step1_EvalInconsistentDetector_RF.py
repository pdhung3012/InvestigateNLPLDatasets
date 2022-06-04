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

def jaccardSimilarityList(list1,list2):
    # list1=sourceSentence.lower().split()
    # list2=targetSentence.lower().split()
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union

def getVector(model,strInput):
    vectorItem = model.get_sentence_vector(strInput)
    strVector = ' '.join(map(str, vectorItem))
    return strVector

fopStanfordCoreNLP='/home/hungphd/git/dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputStep3V2=fopRoot+'step3_v2/'
fopFasttextEmb=fopRoot+'embeddingModels/fasttext-cbow/'
fopInputStep6Incons=fopRoot+'step6_Incons/fasttext-RF/'
createDirIfNotExist(fopInputStep6Incons)

lstFpStep3V2=sorted(glob.glob(fopInputStep3V2+'*.txt'))
dictInputContent={}
for i in range(0,len(lstFpStep3V2)):
    fpItemStep3=lstFpStep3V2[i]
    fnItem=os.path.basename(fpItemStep3)
    f1=open(fpItemStep3,'r')
    arrContent=f1.read().strip().split('\n')
    f1.close()
    dictInputContent[fnItem]=arrContent

fnSource='source.txt'
fnTarget='target.txt'
fnTrainValidTest='trainValidTest.index.txt'
fnInconsistentSource='inconsistentSource.txt'

import fasttext
fpModelBin=fopFasttextEmb+'model.bin'
model = fasttext.FastText.load_model(fpModelBin)

fpTextInfo=fopInputStep6Incons+'text.txt'
fpEmbLabelInfo=fopInputStep6Incons+'emb.txt'
arrSource=dictInputContent[fnSource]
arrTarget = dictInputContent[fnTarget]
arrTrainTestIndex=dictInputContent[fnTrainValidTest]
arrInconsistent=dictInputContent[fnInconsistentSource]
lstTextInput=[]
lstEmbInput=[]
for i in range(0,len(arrSource)):
    arrTab1=arrInconsistent[i].split(strTabChar)
    arrTab2 = arrTrainTestIndex[i].split('\t')
    strInputTextCorrect=arrSource[i]+strEndLine+arrTarget[i]
    strInputTextIncorrect=arrTab1[2]+strEndLine+arrTarget[i]
    lstTextInput.append(strInputTextCorrect)
    lstTextInput.append(strInputTextIncorrect)
    strVectorCorrect = getVector(model, strInputTextCorrect)
    strVectorIncorrect = getVector(model, strInputTextIncorrect)
    lstEmbInput.append('{}\t{}\t{}'.format(arrTrainTestIndex[i],1,strVectorCorrect))
    lstEmbInput.append('{}\t{}\t{}'.format(arrTrainTestIndex[i], 0, strVectorIncorrect))

f1=open(fpTextInfo,'w')
f1.write('\n'.join(lstTextInput))
f1.close()
f1=open(fpEmbLabelInfo,'w')
f1.write('\n'.join(lstEmbInput))
f1.close()



































