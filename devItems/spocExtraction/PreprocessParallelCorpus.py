import operator;
import csv;
import pandas as pd;
import sys, os
import traceback
import operator
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist
from nltk import word_tokenize

fopDataFolder='/home/hung/git/dataPapers/'
fopInputSPOCData=fopDataFolder+'/SPOCDataset/spoc/'
fopTrainTestSplit=fopDataFolder + '/parallelCorpus/'
fopOutputSplit=fopDataFolder + '/parallelCorpus-Number/'

fpTrainText=fopTrainTestSplit+'train.s'
fpTrainCode=fopTrainTestSplit+'train.t'
fpEvalText=fopTrainTestSplit+'valid.s'
fpEvalCode=fopTrainTestSplit+'valid.t'
fpTestText=fopTrainTestSplit+'test.s'
fpTestCode=fopTrainTestSplit+'test.t'
fpOutputTrainText=fopOutputSplit+'train.s'
fpOutputTrainCode=fopOutputSplit+'train.t'
fpOutputEvalText=fopOutputSplit+'valid.s'
fpOutputEvalCode=fopOutputSplit+'valid.t'
fpOutputTestText=fopOutputSplit+'test.s'
fpOutputTestCode=fopOutputSplit+'test.t'
fpOutputVocab=fopOutputSplit+'vocab.txt'
fpOutputDict=fopOutputSplit+'vocab.txt'

dictVocab={}
def preprocessFiles(fpIn,fpOut,dictVocab):
    fff=open(fpIn,'w')
    arrIn=fff.read().split('\n')
    fff.close()
    fff = open(fpOut, 'w')
    arrOut = fff.read().split('\n')
    fff.close()


    for item in arrIn:
        arrItems=word_tokenize(item)
        for word in arrItems:
            if word not in dictVocab:
                dictVocab[word]=str(len(dictVocab.keys())+1)

    for item in arrOut:
        arrItems=word_tokenize(item)
        for word in arrItems:
            if word not in dictVocab:
                dictVocab[word]=str(len(dictVocab.keys())+1)



lstDicts=[]
lstVocabs=['UNKNOWN']
for key in dictVocab.keys():
    val=dictVocab[key]
    lstDicts.append('{}\t{}'.format(key,val))
    lstVocabs.append('{}'.format(val))

dictVocab={}
preprocessFiles(fpTrainText,fpOutputTrainText,dictVocab)
preprocessFiles(fpTrainCode,fpOutputTrainCode,dictVocab)
preprocessFiles(fpEvalText,fpOutputEvalText,dictVocab)
preprocessFiles(fpEvalCode,fpOutputEvalCode,dictVocab)
preprocessFiles(fpTestText,fpOutputTestText,dictVocab)
preprocessFiles(fpTestCode,fpOutputTestCode,dictVocab)

fff=open(fpOutputVocab,'w')
fff.write('\n'.join(lstVocabs))
fff.close()
fff=open(fpOutputDict,'w')
fff.write('\n'.join(lstDicts))
fff.close()



