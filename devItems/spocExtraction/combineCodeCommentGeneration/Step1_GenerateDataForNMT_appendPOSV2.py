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


def walkAndGetPOSJSonByNLTK(dataParseResult,indexSentence,lstNonTerminals,lstTerminals):
  dictJson={}
  try:
      if str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==2:
        # print( str(type(dataParseResult[0])))
        if str(type(dataParseResult[0]))==strStrType:
          if  str(type(dataParseResult[1]))==strStrType:
            # print('ok1')
            dictJson['tag']=str(dataParseResult[0])
            dictJson['value'] = str(dataParseResult[1])
            dictJson['isTerminal'] = True
            dictJson['children'] = []

            newId = len(lstTerminals) + 1
            strValue=dictJson['value']
            strTag=dictJson['tag']
            strLabel ='Sent'+str(indexSentence) +'_Terminal'+str(newId)+'\n'+strTag + '\n' + strValue
            lstTerminals.append(strLabel)
            dictJson['label'] = strLabel
          elif str(type(dataParseResult[1]))==strParseResultsType:
            # print('ok 2')
            dictJson['tag'] = str(dataParseResult[0])
            dictJson['children']=[]
            dictJson['children'].append( walkAndGetPOSJSonByNLTK(dataParseResult[1],indexSentence,lstNonTerminals,lstTerminals))
            dictJson['isTerminal'] = False
            dictJson['value'] = ''
            newId = len(lstNonTerminals) + 1
            strTag = dictJson['tag']
            strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
            lstNonTerminals.append(strLabel)
            dictJson['label'] = strLabel

      elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==1:
        # print('go to branch here')
        dictJson=walkAndGetPOSJSonByNLTK(dataParseResult[0],indexSentence,lstNonTerminals,lstTerminals)
      elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)>2:
        if str(type(dataParseResult[0])) == strStrType:
          strTag =str(dataParseResult[0])
          dictJson['tag']=strTag
          dictJson['value'] = ''
          dictJson['isTerminal'] = False
          dictJson['children'] = []
          newId = len(lstNonTerminals) + 1
          strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
          lstNonTerminals.append(strLabel)
          dictJson['label'] = strLabel

          for i in range(1,len(dataParseResult)):
            dictChildI=walkAndGetPOSJSonByNLTK(dataParseResult[i],indexSentence,lstNonTerminals,lstTerminals)
            dictJson['children'].append(dictChildI)
  except:
      # traceback.print_exc()
      pass
  return dictJson

def walkAndGetPOSJSon(dataParseResult,indexSentence,lstNonTerminals,lstTerminals):
  dictJson={}
  if str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==2:
    # print( str(type(dataParseResult[0])))
    if str(type(dataParseResult[0]))==strStrType:
      if  str(type(dataParseResult[1]))==strStrType:
        # print('ok1')
        dictJson['tag']=str(dataParseResult[0])
        dictJson['value'] = str(dataParseResult[1])
        dictJson['isTerminal'] = True
        dictJson['children'] = []

        newId = len(lstTerminals) + 1
        strValue=dictJson['value']
        strTag=dictJson['tag']
        strLabel ='Sent'+str(indexSentence) +'_Terminal'+str(newId)+'\n'+strTag + '\n' + strValue
        lstTerminals.append(strLabel)
        dictJson['label'] = strLabel
      elif str(type(dataParseResult[1]))==strParseResultsType:
        # print('ok 2')
        dictJson['tag'] = str(dataParseResult[0])
        dictJson['children']=[]
        dictJson['children'].append( walkAndGetPOSJSon(dataParseResult[1],indexSentence,lstNonTerminals,lstTerminals))
        dictJson['isTerminal'] = False
        dictJson['value'] = ''
        newId = len(lstNonTerminals) + 1
        strTag = dictJson['tag']
        strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
        lstNonTerminals.append(strLabel)
        dictJson['label'] = strLabel

  elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==1:
    # print('go to branch here')
    dictJson=walkAndGetPOSJSon(dataParseResult[0],indexSentence,lstNonTerminals,lstTerminals)
  elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)>2:
    if str(type(dataParseResult[0])) == strStrType:
      strTag =str(dataParseResult[0])
      dictJson['tag']=strTag
      dictJson['value'] = ''
      dictJson['isTerminal'] = False
      dictJson['children'] = []
      newId = len(lstNonTerminals) + 1
      strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
      lstNonTerminals.append(strLabel)
      dictJson['label'] = strLabel

      for i in range(1,len(dataParseResult)):
        dictChildI=walkAndGetPOSJSon(dataParseResult[i],indexSentence,lstNonTerminals,lstTerminals)
        dictJson['children'].append(dictChildI)
  return dictJson


def getGraphDependencyFromTextByStanford(strText,nlpObj):
  lstDeps = []
  lstNodes=[]
  lstEdges=[]

  try:
    output = nlpObj.annotate(strText, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
    })
    jsonTemp = output
    # strJsonObj = jsonTemp
    # print('output here: '+str(jsonTemp))
    arrSentences=jsonTemp['sentences']
    dictTotal={}
    dictTotal['tag'] = 'Paragraph'
    dictTotal['label'] = 'Paragraph'
    dictTotal['value'] = ''
    dictTotal['isTerminal'] = False
    dictTotal['children'] = []
    indexSentence=0
    # print(strText)
    for sentence in arrSentences:
      jsonDependency = sentence['basicDependencies']
      strParseContent=sentence['parse']
      lstNonTerminals = []
      lstTerminals = []
      indexSentence=indexSentence+1
      data = OneOrMore(nestedExpr()).parseString(strParseContent)
      dictWords = {}
      jsonPOS=walkAndGetPOSJSon(data,indexSentence,lstNonTerminals,lstTerminals)
      # print('POS {}'.format(jsonPOS))
      # print(str(jsonDependency))
      for dep in jsonDependency:
        strDep=dep['dep']
        # print(strDep)
        if strDep=='ROOT':
            continue
        # print('dep : {}'.format(dep))
        try:
            indexSource = dep['governor']
            indexTarget = dep['dependent']
            itemTuple = (indexSource, indexTarget, strDep, lstTerminals[indexSource - 1], lstTerminals[indexTarget - 1])
            lstEdges.append(itemTuple)
        except:
            pass

      jsonPOS['dependencies']=lstEdges
      dictTotal['children'].append(jsonPOS)
  except:
    strJsonObj = 'Error'
    dictTotal={}
    traceback.print_exc()
  return dictTotal

fopStanfordCoreNLP='/home/hungphd/git/dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopInputStep2Pseudocode=fopRoot+'step2_pseudo_tokenize/'
fopInputStep2ReplaceDict=fopRoot+'step2_code_replaceDict/'
fopInputStep2BeforeTranslation=fopRoot+'step2_beforeTranslation/step1/'
fopInputStep2Folds=fopRoot+'step2_beforeTranslation/folds/'
fopInputAfterTranslation=fopRoot+'step2_afterTranslation/'
fpSourceAfterTrans=fopInputAfterTranslation+'source.txt'
fopPOSStanford=fopInputAfterTranslation+'pos_stanford/'
fopPOSNLTK=fopInputAfterTranslation+'pos_nltk/'
fopSortedBySimScore=fopInputAfterTranslation+'sortBySimilarityScore/'
fpSortedSource=fopSortedBySimScore+'source.txt'
fopSortedPOSStanford=fopSortedBySimScore+'pos_stanford/'
fopSortedPOSNLTK=fopSortedBySimScore+'pos_nltk/'
createDirIfNotExist(fopSortedPOSStanford)
createDirIfNotExist(fopSortedPOSNLTK)


strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
nltk.download('bllip_wsj_no_aux')
model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)

strServerPort = '9000'
nlpObj = StanfordCoreNLP('http://localhost:' + strServerPort)

fpAppendNLTKText=fopSortedBySimScore+'appendPOS.nltk.text.txt'
fpAppendNLTKPOS=fopSortedBySimScore+'appendPOS.nltk.pos.txt'
fpAppendStanfordText=fopSortedBySimScore+'appendPOS.stanford.text.txt'
fpAppendStanfordPOS=fopSortedBySimScore+'appendPOS.stanford.pos.txt'

fpV2AppendNLTKText=fopSortedBySimScore+'v2.appendPOS.nltk.text.txt'
fpV2AppendNLTKPOS=fopSortedBySimScore+'v2.appendPOS.nltk.pos.txt'
fpV2AppendStanfordText=fopSortedBySimScore+'v2.appendPOS.stanford.text.txt'
fpV2AppendStanfordPOS=fopSortedBySimScore+'v2.appendPOS.stanford.pos.txt'

f1=open(fpAppendStanfordText,'r')
arrStanfordText=f1.read().strip().split('\n')
f1.close()
f1=open(fpAppendStanfordPOS,'r')
arrStanfordPOS=f1.read().strip().split('\n')
f1.close()

numError=0
lstErrorText=[]
for i in range(0,len(arrStanfordText)):
    itemPOS=arrStanfordPOS[i]
    itemText = arrStanfordText[i]
    if itemPOS=='{}':
        numError=numError+1
        lstErrorText.append(itemText)
print('percentage error in StanfordNLP {}/{}'.format(numError,len(arrStanfordText)))

# maxRun=10
# lstItemTexts=[]
# lstItemPOSs=[]
# for i in range(0,len(lstErrorText)):
#     itemText=lstErrorText[i]
#     itemTextPreprocess=itemText.replace('%','_MODULO_')
#     try:
#         indexRun=0
#         strPOSStanford ='{}'
#         while(str(strPOSStanford)=='{}' and indexRun<maxRun):
#             strPOSStanford = getGraphDependencyFromTextByStanford(itemTextPreprocess, nlpObj)
#             if str(strPOSStanford)=='{}':
#                 print('text error\n{}'.format(itemText))
#                 indexRun=indexRun+1
#                 # input('error here')
#             # else:
#             #     print('success\n{}'.format(itemText))
#         lstItemTexts.append(itemText)
#         lstItemPOSs.append(strPOSStanford)
#     except:
#         traceback.print_exc()
#
#     if(len(lstItemTexts)%100==0 or (i==len(lstItemTexts)-1 and len(lstItemTexts)>0)):
#         f1 = open(fpV2AppendStanfordText, 'a+')
#         f1.write('\n'.join(lstItemTexts) + '\n')
#         f1.close()
#         f1 = open(fpV2AppendStanfordPOS, 'a+')
#         f1.write('\n'.join(map(str, lstItemPOSs)) + '\n')
#         f1.close()
#         lstItemTexts = []
#         lstItemPOSs=[]


f1=open(fpAppendNLTKText,'r')
arrNLTKText=f1.read().strip().split('\n')
f1.close()
f1=open(fpAppendNLTKPOS,'r')
arrNLTKPOS=f1.read().strip().split('\n')
f1.close()

numError=0
lstErrorText=[]
for i in range(0,len(arrNLTKText)):
    itemPOS=arrNLTKPOS[i]
    itemText = arrNLTKText[i]
    if itemPOS=='{}':
        numError=numError+1
        lstErrorText.append(itemText)
print('percentage error in NLTK {}/{}'.format(numError,len(arrNLTKText)))

maxRun=10
lstItemTexts=[]
lstItemPOSs=[]
for i in range(0,len(lstErrorText)):
    itemText=lstErrorText[i]
    itemTextPreprocess=itemText.replace('(','_P_').replace('(','_PC_').replace('[','_S_').replace(']','_SC_')
    try:
        indexRun=0
        strPOSNLTK ='{}'
        while(str(strPOSNLTK)=='{}' and indexRun<maxRun):
            try:
                lstNonT = []
                lstT = []
                best = parser.parse(itemTextPreprocess)
                strParseContent = str(best.get_parser_best().ptb_parse)
                print(strParseContent)
                dataParseResult = OneOrMore(nestedExpr()).parseString(strParseContent)
                strPOSNLTK = walkAndGetPOSJSonByNLTK(dataParseResult, 0, lstNonT, lstT)
            except:
                traceback.print_exc()
                strPOSNLTK = '{}'
            if str(strPOSNLTK)=='{}':
                print('text error\n{}'.format(itemText))
                indexRun=indexRun+1
                input('error here')
            # else:
            #     print('success\n{}'.format(itemText))
        lstItemTexts.append(itemText)
        lstItemPOSs.append(strPOSNLTK)
    except:
        traceback.print_exc()

    if(len(lstItemTexts)%100==0 or (i==len(lstItemTexts)-1 and len(lstItemTexts)>0)):
        f1 = open(fpV2AppendNLTKText, 'a+')
        f1.write('\n'.join(lstItemTexts) + '\n')
        f1.close()
        f1 = open(fpV2AppendNLTKPOS, 'a+')
        f1.write('\n'.join(map(str, lstItemPOSs)) + '\n')
        f1.close()
        lstItemTexts = []
        lstItemPOSs=[]























