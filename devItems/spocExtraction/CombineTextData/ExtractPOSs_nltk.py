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
import glob
import time
import nltk
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.parse import stanford

fopStanfordCoreNLP='../../../../dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '


def getPOSAndTreeFromText(strText):
  strTextAll=''
  # strTreeAll=''
  strPOSAll=''
  try:
      arrText = word_tokenize(strText)
      arrSent=sent_tokenize(strText)
      tags=nltk.pos_tag(arrText)
      list1=[]
      list2=[]
      for item in tags:
          list1.append(item[0])
          list2.append(item[1])
      strTextAll=' '.join(list1)
      strPOSAll=' '.join(list2)
      # parseContent=sp.parse(arrSent)
      # trees = [tree for tree in parseContent]
      # lstTree=[]
      # for tree in trees:
      #     lstTree.append(str(tree))
      # strTreeAll=strSplitElement.join(lstTree)
      strTextAll=strTextAll.replace('\n',strEndLine)
      strPOSAll=strPOSAll.replace('\n',strEndLine)
      # strTreeAll=strTreeAll.replace('\n',strEndLine)
  except:
    strJsonObj = 'Error'
    # dictTotal=None
    traceback.print_exc()


  return strTextAll,strPOSAll
  # return dictTotal

def extractPOSAndTree(fopTextCorpus,fopPOSCorpus,item):
    try:
        fopItemTextCorpus = fopTextCorpus + item + '/'
        # fopItemTreeCorpus = fopTextCorpus + item + '/'
        fopItemPOSCorpus = fopPOSCorpus + item + '/'
        # createDirIfNotExist(fopItemTreeCorpus)
        createDirIfNotExist(fopItemPOSCorpus)
        lstTextFiles = sorted(glob.glob(fopItemTextCorpus + '/*.txt'))
        lstPOSPerFile=[]
        lstTreePerFile = []
        lstProcessTextPerFile = []

        # print('len {}'.format(len(lstTextFiles)))
        for j in range(0,len(lstTextFiles)):
            try:
                start_time = time.time()
                f1 = open(lstTextFiles[j], 'r')
                arrTexts = f1.read().split('\n')
                f1.close()
                indexName = os.path.basename(lstTextFiles[j]).replace('.txt', '')
                fpPOS = fopItemPOSCorpus + indexName + '_pos.txt'
                # fpTree = fopItemPOSCorpus + indexName + '_tree.txt'
                fpTextPreprocess = fopItemPOSCorpus + indexName + '_preprocess.txt'
                # print('go here')
                f1 = open(fpPOS, 'w')
                f1.write('')
                f1.close()
                # f1 = open(fpTree, 'w')
                # f1.write('')
                # f1.close()
                f1 = open(fpTextPreprocess, 'w')
                f1.write('')
                f1.close()

                for i in range(0, len(arrTexts)):
                    try:
                        strItem = arrTexts[i].replace(strEndLine, '\m').replace(strTabChar, '\t').replace('// ','')
                        strPostText,  strPOS = getPOSAndTreeFromText(strItem)
                        if strPostText != '':
                            lstProcessTextPerFile.append(strPostText)
                            # lstTreePerFile.append(strTree)
                            lstPOSPerFile.append(strPOS)

                        if((len(lstProcessTextPerFile)>0) and (((i+1)==len(arrTexts)) or ((i+1)%1000==0))):
                            f1 = open(fpPOS, 'a')
                            f1.write('\n'.join(lstPOSPerFile)+'\n')
                            f1.close()
                            # f1 = open(fpTree, 'a')
                            # f1.write('\n'.join(lstTreePerFile)+'\n')
                            # f1.close()
                            f1 = open(fpTextPreprocess, 'a')
                            f1.write('\n'.join(lstProcessTextPerFile)+'\n')
                            f1.close()
                            lstPOSPerFile=[]
                            lstTreePerFile=[]
                            lstProcessTextPerFile=[]
                            print('finish write at index {} of file {}'.format(i,lstTextFiles[j]))

                        # if i==100:
                        #     break
                    except:
                        traceback.print_exc()
                duration=time.time() - start_time
                print('index {}/{} duration {}'.format(i,len(lstTextFiles),duration))
            except:
                traceback.print_exc()
    except:
        traceback.print_exc()


batch_size=100000
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

# fopCCContent='/home/hungphd/media/dataPapersExternal/apiCallPapers_v1/AlonCommentExtraction/'
fopTextCorpus='/home/hungphd/media/dataPapersExternal/textCorpus/'
# fopTextPostProcessCorpus='/home/hungphd/media/dataPapersExternal/textPostProcessCorpus/'
fopPOSCorpus='/home/hungphd/media/dataPapersExternal/posCorpus/'
# fopParseTreeCorpus='/home/hungphd/media/dataPapersExternal/treeCorpus/'
createDirIfNotExist(fopPOSCorpus)
lstTypesOfSDs=['ad','cs','cc','cm','qa','sr']

fopStanfordParser='/home/hungphd/git/dataPapers/stanford-parser-4.2.0'
os.environ['STANFORD_PARSER'] = fopStanfordParser
os.environ['STANFORD_MODELS'] = fopStanfordParser

from pycorenlp import StanfordCoreNLP

# for item in lstTypesOfSDs:

from multiprocessing.pool import ThreadPool as Pool

# from multiprocessing import Pool
from multiprocessing import Process
lstThreads=[]
for i in range(0,len(lstTypesOfSDs)):
    # strServerPort='900'+str(i)
    # nlpObj = StanfordCoreNLP('http://localhost:'+strServerPort)
    # sp = stanford.StanfordParser()
    print('start thread {}'.format(i))
    p1=Process(target=extractPOSAndTree,args=[fopTextCorpus,fopPOSCorpus,lstTypesOfSDs[i]])
    p1.start()
    lstThreads.append(p1)

for i in range(0,len(lstTypesOfSDs)):
    lstThreads[i].join()



