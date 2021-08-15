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

# fpQAContent='/home/hungphd/media/dataPapersExternal/StackOverflow_database/conala-mined.jsonl'
# fopOutputQAContent='/home/hungphd/media/dataPapersExternal/textCorpus/qa/'
# f1=open(fpQAContent, "r")
# read_it=f1.read()
# f1.close()
# lstIntents = []
# try:
#     # association_data = json.load(read_it)
#     # print(type(association_data))
#     # print(association_data)
#     arrJsons = read_it.strip().split('\n')
#
#     for i in range(0, len(arrJsons)):
#         try:
#             print('iiiii {}'.format(i))
#             jsonObject=json.loads(arrJsons[i])
#             strIntent = jsonObject['intent']
#             lstIntents.append(strIntent)
#             # print(strIntent)
#         except:
#             traceback.print_exc()
#         # input('next')
# except:
#     traceback.print_exc()
#
# index=0
# lstBatches=[]
# for i in range(0,len(lstIntents)):
#     try:
#         strIntent=lstIntents[i]
#         strProcess=strIntent.replace('\n',strEndLine).replace('\t',strTabChar)
#         lstBatches.append(strProcess)
#         if (i+1)%batch_size==0 or (i+1)==len(lstIntents):
#             index=index+1
#             fpOut=fopOutputQAContent+str(index)+'.txt'
#             f1=open(fpOut,'w')
#             f1.write('\n'.join(lstBatches))
#             lstBatches=[]
#             print('end index {}'.format(index))
#     except:
#         traceback.print_exc()

# fopSpocContent='/home/hungphd/git/dataPapers/textInSPOC/trainSPOCPlain/'
# fopOutputSpocContent='/home/hungphd/media/dataPapersExternal/textCorpus/ad/'
# import glob
# lstFiles=sorted(glob.glob(fopSpocContent+'*_text.txt'))
# lstIntents=[]
# try:
#
#     for i in range(0, len(lstFiles)):
#         try:
#             print('iiiii {}'.format(i))
#             f1=open(lstFiles[i],'r')
#             arrIntent = f1.read().strip().split('\n')
#             f1.close()
#             for j in range(0,len(arrIntent)):
#                 if arrIntent[j].strip()!='':
#                     lstIntents.append(arrIntent[j].strip())
#             # print(strIntent)
#         except:
#             traceback.print_exc()
#         # input('next')
# except:
#     traceback.print_exc()
#
# index=0
# lstBatches=[]
# for i in range(0,len(lstIntents)):
#     try:
#         strIntent=lstIntents[i]
#         strProcess=strIntent.replace('\n',strEndLine).replace('\t',strTabChar)
#         lstBatches.append(strProcess)
#         if (i+1)%batch_size==0 or (i+1)==len(lstIntents):
#             index=index+1
#             fpOut=fopOutputSpocContent+str(index)+'.txt'
#             f1=open(fpOut,'w')
#             f1.write('\n'.join(lstBatches))
#             lstBatches=[]
#             print('end index {}'.format(index))
#     except:
#         traceback.print_exc()

# fopSRContent='/home/hungphd/git/SoftwareStoryPointsPrediction/devItems/dataset/'
# fopOutputSRContent='/home/hungphd/media/dataPapersExternal/textCorpus/sr/'
# import glob
# lstFiles=sorted(glob.glob(fopSRContent+'*.csv'))
# lstIntents=[]
# import pandas as pd
# try:
#
#     for i in range(0, len(lstFiles)):
#         try:
#             print('iiiii {}'.format(i))
#             df=pd.read_csv(lstFiles[i])
#             colTitle=df['title']
#             colDescription=df['description']
#             for j in range(0,len(colTitle)):
#                 strTitle=str(colTitle[j]).strip()
#                 strDesc=str(colDescription[j]).strip()
#                 if strTitle=='' or strDesc=='':
#                     continue
#                 lstIntents.append(strTitle)
#                 lstIntents.append(strDesc)
#             # print(strIntent)
#         except:
#             traceback.print_exc()
#         # input('next')
# except:
#     traceback.print_exc()
#
# index=0
# lstBatches=[]
# for i in range(0,len(lstIntents)):
#     try:
#         strIntent=lstIntents[i]
#         strProcess=strIntent.replace('\n',strEndLine).replace('\t',strTabChar)
#         lstBatches.append(strProcess)
#         if (i+1)%batch_size==0 or (i+1)==len(lstIntents):
#             index=index+1
#             fpOut=fopOutputSRContent+str(index)+'.txt'
#             f1=open(fpOut,'w')
#             f1.write('\n'.join(lstBatches))
#             lstBatches=[]
#             print('end index {}'.format(index))
#     except:
#         traceback.print_exc()

fopCMContent='/home/hungphd/media/dataPapersExternal/CSN_githubProjects/commitMessage/'
fopOutputCMContent='/home/hungphd/media/dataPapersExternal/textCorpus/cm/'
import glob
lstFiles=sorted(glob.glob(fopCMContent+'/**/*.txt',recursive=True))
lstIntents=[]
import pandas as pd
try:
    index = 0
    lstBatches = []
    numSentence=0
    print('size of cm dataset '.format(len(lstFiles)))
    for i in range(0, len(lstFiles)):
        try:
            fpItem=lstFiles[i]
            print('iiiii {}/{}'.format(i,len(lstFiles)))
            f1=open(fpItem,'r')
            arrTexts=f1.read().strip().split('\n')
            f1.close()
            bufferStr=[]
            for j in range(0,len(arrTexts)):
                strText=str(arrTexts[j]).strip()
                if strText.startswith('Date:'):
                    bufferStr=[]
                elif strText.startswith('commit'):
                    strAddItem='\n'.join(bufferStr).strip().replace('\n',strEndLine).replace('\t',strTabChar).strip()
                    lstBatches.append(strAddItem)
                    numSentence=numSentence+1
                    if (numSentence % batch_size == 0):
                        index = index + 1
                        fpOut = fopOutputCMContent + str(index) + '.txt'
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
        fpOut = fopOutputCMContent + str(index) + '.txt'
        f1 = open(fpOut, 'w')
        f1.write('\n'.join(lstBatches))
        lstBatches = []
        print('line end batch {}'.format(index))

except:
    traceback.print_exc()

