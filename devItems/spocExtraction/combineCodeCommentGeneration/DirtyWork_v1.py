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

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopStep4NMT=fopRoot+'step4_NMT_optimization_v2/'
fopStep3V2=fopRoot+'step3_v2/'
fopStep3TreesitterTokenize=fopRoot+'step3_treesitter_tokenize/'
fopStep2Tokenize=fopRoot+'step2_tokenize/'
fopStep2PseudoTokenize=fopRoot+'step2_pseudo_tokenize/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'

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
fnTrainValidTest='trainValidTest.index.txt'

# dictAvg={}
# dictAvg['train']=[0,0]
# dictAvg['valid']=[0,0]
# dictAvg['test']=[0,0]
# for i in range(0,len(dictFolderContent[fnLocation])):
#     arrTrainValidTestItem=dictFolderContent[fnTrainValidTest][i].split('\t')
#     # fpPseudoItem=fopStep2PseudoTokenize+arrTrainValidTestItem[2]+'/'+arrTrainValidTestItem[1]+'_text.txt'
#     # f1=open(fpPseudoItem,'r')
#     # arrContent=f1.read().strip().split('\n')
#     # f1.close()
#     lenTarget=float(dictFolderContent['label.p3.jaccardSimilarity.txt'][i])
#     # lenTarget=len(arrContent)
#     print(i)
#     # lenTarget=len(dictFolderContent['target.txt'][i].split())
#     dictAvg[arrTrainValidTestItem[0]]=[dictAvg[arrTrainValidTestItem[0]][0]+lenTarget,dictAvg[arrTrainValidTestItem[0]][1]+1]
#
# for key in dictAvg.keys():
#     val=dictAvg[key]
#     avg=val[0]*1.0/val[1]
#     print('{}\t{}\t{}\t{}'.format(key,val[0],val[1],avg))


fopLossAcc='/home/hungphd/media/dataPapersExternal/mixCodeRaw/step3_v3/plotAcc/'

import matplotlib.pyplot as plt

fpRNN=fopLossAcc+'rnn.txt'
xRNN=[]
yLossRNN=[]
yValidAccRNN=[]
f1=open(fpRNN,'r')
arrContent=f1.read().strip().split('\n')
f1.close()
for i in range(0,len(arrContent),2):
    # print(i)
    numberX=(i+1)*100.0/len(arrContent)
    xRNN.append(numberX)
    strLine=arrContent[i+1]
    strLineBefore=arrContent[i]
    # print(strLine)
    lossVal=float(strLineBefore.split('Loss:')[1].split('|')[0].strip())
    validVal=float(strLine.split('Val. Acc:')[1].strip().replace('%',''))
    yLossRNN.append(lossVal)
    yValidAccRNN.append(validVal)

fpHGTOrg=fopLossAcc+'hgt-ori.txt'
xHGTOrg=[]
yLossHGTOrg=[]
yValidAccHGTOrg=[]
f1=open(fpHGTOrg,'r')
arrContent=f1.read().strip().split('\n')
f1.close()

for i in range(0,500):
    # print(i)
    numberX=(i+1)*100.0/500
    xHGTOrg.append(numberX)
    strLine=arrContent[i]
    # print(strLine)
    lossVal=float(strLine.split('Loss:')[1].split(',')[0].strip())
    validVal=float(strLine.split('Val:')[1].split(',')[0].strip().replace('%',''))*100
    yLossHGTOrg.append(lossVal)
    yValidAccHGTOrg.append(validVal)

fpHGTAug=fopLossAcc+'hgt-aug.txt'
xHGTAug=[]
yLossHGTAug=[]
yValidAccHGTAug=[]
f1=open(fpHGTAug,'r')
arrContent=f1.read().strip().split('\n')
f1.close()

for i in range(0,500):
    # print(i)
    numberX=(i+1)*100.0/500
    xHGTAug.append(numberX)
    strLine=arrContent[i]
    # print(strLine)
    lossVal=float(strLine.split('Loss:')[1].split(',')[0].strip())
    validVal=float(strLine.split('Val:')[1].split(',')[0].strip().replace('%',''))*100
    yLossHGTAug.append(lossVal)
    yValidAccHGTAug.append(validVal)


# create data
# x = [10, 20, 30, 40, 50]
# y = [30, 30, 30, 30, 30]


# plot lines
# plot1 = plt.figure()
plt.plot(xRNN, yLossRNN, label="LSTM-RNN")
plt.plot(xHGTOrg, yLossHGTOrg, label="Hetero-GNN")
plt.plot(xHGTAug, yLossHGTAug, label="Hetero-GNN-Opt")
plt.xlabel("% of epochs")
plt.ylabel("Training Loss")
plt.legend()
# plt.show()
plt.savefig(fopLossAcc+'loss.png')
plt.close(1)

plt.clf()
plt.plot(xRNN, yValidAccRNN, label="LSTM-RNN")
plt.plot(xHGTOrg, yValidAccHGTOrg, label="Hetero-GNN")
plt.plot(xHGTAug, yValidAccHGTAug, label="Hetero-GNN-Opt")
plt.xlabel("% of epochs")
plt.ylabel("Validation Accuracy")
plt.legend()
# plt.show()
plt.savefig(fopLossAcc+'val.png')


# plot2=plt.figure()
# plt.clf()
# plt.plot(xRNN, yValidAccRNN, label="RNN-LSTM")
# plt.legend()
# plt.savefig(fopLossAcc+'valid_acc.jpg')
# # plt.close('all')