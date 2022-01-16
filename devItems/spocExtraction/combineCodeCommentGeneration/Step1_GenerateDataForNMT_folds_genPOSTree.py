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

      for dep in jsonDependency:
        strDep=dep['dep']
        if strDep=='ROOT':
            continue
        # print('dep : {}'.format(dep))
        indexSource=dep['governor']
        indexTarget=dep['dependent']
        itemTuple=(indexSource,indexTarget,strDep,lstTerminals[indexSource-1],lstTerminals[indexTarget-1])
        lstEdges.append(itemTuple)
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


strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
nltk.download('bllip_wsj_no_aux')
model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)

strServerPort = '9000'
nlpObj = StanfordCoreNLP('http://localhost:' + strServerPort)

f1=open(fpSourceAfterTrans,'r')
arrSources=f1.read().strip().split('\n')
f1.close()

dictText=set()
for i in range(0,len(arrSources)):
    if arrSources[i].strip()!='':
        dictText.add(arrSources[i].strip())
print(len(dictText))
lstText=list(dictText)

lstItemText=[]
lstItemPOS1=[]
lstItemPOS2=[]
indexItem=0

# if os.path.exists(fopPOSStanford) and os.path.isdir(fopPOSStanford):
#     shutil.rmtree(fopPOSStanford)
# if os.path.exists(fopPOSNLTK) and os.path.isdir(fopPOSNLTK):
#     shutil.rmtree(fopPOSNLTK)
createDirIfNotExist(fopPOSStanford)
createDirIfNotExist(fopPOSNLTK)

for i in range(0,len(lstText)):
    try:
        strText=lstText[i]
        strPOSStanford=getGraphDependencyFromTextByStanford(strText,nlpObj)

        try:
            lstNonT = []
            lstT = []
            best = parser.parse(strText)
            strParseContent = str(best.get_parser_best().ptb_parse)
            dataParseResult = OneOrMore(nestedExpr()).parseString(strParseContent)
            strPOSNLTK = walkAndGetPOSJSonByNLTK(dataParseResult, 0, lstNonT, lstT)
        except:
            traceback.print_exc()
            strPOSNLTK ={}

        lstItemText.append(strText)
        lstItemPOS1.append(strPOSStanford)
        lstItemPOS2.append(strPOSNLTK)
        indexItem=indexItem+1
    except:
        traceback.print_exc()
    if len(lstItemText)>0 and ( indexItem%100==0 or i==(len(lstText)-1)):
        nameItem=indexItem//10000+1
        strNameItem='{:03d}'.format(nameItem)
        fpItemTextPOS1=fopPOSStanford+strNameItem+'.text.txt'
        fpItemTextPOS2 = fopPOSNLTK + strNameItem + '.text.txt'
        fpItemPOSPOS1 = fopPOSStanford + strNameItem + '.pos.txt'
        fpItemPOSPOS2 = fopPOSNLTK + strNameItem + '.pos.txt'
        f1=open(fpItemTextPOS1,'a+')
        f1.write('\n'.join(lstItemText)+'\n')
        f1.close()
        f1 = open(fpItemTextPOS2, 'a+')
        f1.write('\n'.join(lstItemText) + '\n')
        f1.close()
        f1 = open(fpItemPOSPOS1, 'a+')
        f1.write('\n'.join(map(str,lstItemPOS1)) + '\n')
        f1.close()
        f1 = open(fpItemPOSPOS2, 'a+')
        f1.write('\n'.join(map(str,lstItemPOS2)) + '\n')
        f1.close()
        lstItemText=[]
        lstItemPOS1=[]
        lstItemPOS2=[]
        print('complete for index {}'.format(indexItem))



























