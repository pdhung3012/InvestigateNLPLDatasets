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
createDirIfNotExist(fopOutputSplit)

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
    fff=open(fpIn,'r')
    strIn=fff.read()
    arrIn=strIn.split('\n')
    fff.close()

    lstOut=[]
    for item in arrIn:
        arrItems=word_tokenize(item)
        lstLines=[]
        for word in arrItems:
            if word not in dictVocab:
                dictVocab[word]=str(len(dictVocab.keys())+1)
            lstLines.append(dictVocab[word])
        lstOut.append(' '.join(lstLines))

    fff=open(fpOut,'w')
    fff.write('\n'.join(lstOut))
    fff.close()



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



