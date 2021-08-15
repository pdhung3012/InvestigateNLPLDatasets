import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import pygraphviz as pgv
import pylab,traceback
from pyparsing import OneOrMore, nestedExpr
import json

batch_size=100000
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

fopCCContent='/home/hungphd/media/dataPapersExternal/apiCallPapers_v1/AlonCommentExtraction/'
fopOutputCCContent='/home/hungphd/media/dataPapersExternal/textCorpus/cc/'
import glob
lstFiles=sorted(glob.glob(fopCCContent+'/**/*_comment.txt',recursive=True))
lstIntents=[]
import pandas as pd
try:
    index = 0
    lstBatches = []
    numSentence=0
    print('size of cc dataset {}'.format(len(lstFiles)))
    for i in range(0, len(lstFiles)):
        try:
            fpItem=lstFiles[i]
            print('iiiii {}/{}'.format(i,len(lstFiles)))
            f1=open(fpItem,'r')
            arrTexts=f1.read().strip().split('\n')
            f1.close()
            bufferStr=[]
            for j in range(0,len(arrTexts)):
                arrTextItem=str(arrTexts[j]).strip().split('\t')
                if(len(arrTextItem)<2):
                    continue
                strText=arrTextItem[1]

                if strText.startswith('//'):
                    strAddItem='\n'.join(bufferStr).strip().replace('//',strSingleComment).strip()
                    lstBatches.append(strAddItem)
                    numSentence=numSentence+1
                    if (numSentence % batch_size == 0):
                        index = index + 1
                        fpOut = fopOutputCCContent + str(index) + '.txt'
                        f1 = open(fpOut, 'w')
                        f1.write('\n'.join(lstBatches))
                        f1.close()
                        lstBatches = []
                        numSentence=0
                        print('end batch {}'.format(index))
                else:
                    bufferStr.append(strText)


        except:
            traceback.print_exc()
        # input('next')
    if len(lstBatches) > 0:
        index = index + 1
        fpOut = fopOutputCCContent + str(index) + '.txt'
        f1 = open(fpOut, 'w')
        f1.write('\n'.join(lstBatches))
        lstBatches = []
        print('line end batch {}'.format(index))

except:
    traceback.print_exc()

