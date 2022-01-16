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

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputStep2Pseudocode=fopRoot+'step2_pseudo_tokenize/'
fopInputStep2ReplaceDict=fopRoot+'step2_code_replaceDict/'
fopInputStep2BeforeTranslation=fopRoot+'step2_beforeTranslation/step1/'
createDirIfNotExist(fopInputStep2ReplaceDict)
createDirIfNotExist(fopInputStep2BeforeTranslation)


lstFopStep2Tok1=sorted(glob.glob(fopInputStep2Pseudocode+'**/'),reverse=True)
lstFpStep2Pseudocode=[]
for fop1 in lstFopStep2Tok1:
    lstFpItem1=sorted(glob.glob(fop1+'*_text.txt'),reverse=True)
    for fpItem in lstFpItem1:
        lstFpStep2Pseudocode.append(fpItem)

fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiteralsReverse={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiteralsReverse[strContent]=arrTabs[0]

fpLocation=fopInputStep2BeforeTranslation+'location.txt'
fpSource=fopInputStep2BeforeTranslation+'source.txt'
fpTarget=fopInputStep2BeforeTranslation+'target.txt'

f1=open(fpLocation,'w')
f1.write('')
f1.close()
f1=open(fpSource,'w')
f1.write('')
f1.close()
f1=open(fpTarget,'w')
f1.write('')
f1.close()

for i in range(0,len(lstFpStep2Pseudocode)):
    arrFpItem=lstFpStep2Pseudocode[i].split('/')
    fopItem='/'.join(arrFpItem[:len(arrFpItem)-1])+'/'
    fonTrainTest=arrFpItem[len(arrFpItem)-2]
    fopItemCode=fopItem.replace(fopInputStep2Pseudocode,fopInputStep2ReplaceDict)
    namePseudoCode=arrFpItem[len(arrFpItem)-1]
    nameCode=namePseudoCode.replace('_text.txt','_code.cpp')
    f1=open(fopItem+namePseudoCode,'r')
    arrPseudocode=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fopItemCode + nameCode, 'r')
    arrCode = f1.read().strip().split('\n')
    f1.close()
    lstLocations=[]
    for j in range(0,len(arrPseudocode)):
        nameProgram=namePseudoCode.replace('_text.txt','')
        strLoc='{}\t{}\t{}'.format(nameProgram,fonTrainTest,(j+1))
        lstLocations.append(strLoc)

    f1=open(fpLocation,'a')
    f1.write('\n'.join(lstLocations)+'\n')
    f1.close()
    f1=open(fpSource,'a')
    f1.write('\n'.join(arrPseudocode)+'\n')
    f1.close()
    f1=open(fpTarget,'a')
    f1.write('\n'.join(arrCode)+'\n')
    f1.close()





# for i in range(0,len(lstFpStep2Code)):
#     arrFpItem=lstFpStep2Code[i].split('/')
#     fopItem='/'.join(arrFpItem[:len(arrFpItem)-1])+'/'
#     fopOutItem=fopItem.replace(fopInputStep2Code,fopInputStep2ReplaceDict)
#     createDirIfNotExist(fopOutItem)
#     fnNameFile=arrFpItem[len(arrFpItem)-1]
#     f1=open(lstFpStep2Code[i],'r')
#     arrInputCodes=f1.read().strip().split('\n')
#     f1.close()
#     lstOutputCodes=[]
#     for j in range(33,len(arrInputCodes)):
#         arrItemWords=arrInputCodes[j].split()
#         lstOutWords=[]
#         for word in arrItemWords:
#             if word in dictLiteralsReverse.keys():
#                 val=dictLiteralsReverse[word]
#             else:
#                 val=word
#             lstOutWords.append(val)
#         lstOutputCodes.append(' '.join(lstOutWords))
#
#     f1=open(fopOutItem+fnNameFile,'w')
#     f1.write('\n'.join(lstOutputCodes))
#     f1.close()
#     print('end {} {}/{}'.format(lstFpStep2Code[i],(i+1),len(lstFpStep2Code)))



