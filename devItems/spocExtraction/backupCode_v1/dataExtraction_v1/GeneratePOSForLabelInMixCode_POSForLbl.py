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
from LibForGraphExtractionFromRawCode import getJsonDict,getTerminalValue
import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render
from pyparsing import OneOrMore, nestedExpr

import copy
import nltk
from nltk.data import find
from bllipparser import RerankingParser
import time


strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"


def walkAndGetPOSJson(dataParseResult,indexSentence,lstNonTerminals,lstTerminals):
  dictJson={}
  if str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==2:
    # print( str(type(dataParseResult[0])))
    if str(type(dataParseResult[0]))==strStrType:
      if  str(type(dataParseResult[1]))==strStrType:
        # print('ok1')
        dictJson['tag']=str(dataParseResult[0])
        dictJson['value'] = str(dataParseResult[1])
        dictJson['isTerminal'] = True
        # dictJson['children'] = []

        newId = len(lstTerminals) + 1
        # strValue=dictJson['value']
        # strTag=dictJson['tag']
        strPosition='Sent_'+str(indexSentence) +'_Terminal_'+str(newId)
        # strLabel ='Sent'+str(indexSentence) +'_Terminal'+str(newId)
        dictJson['position'] = strPosition
        lstTerminals.append(strPosition)
        # dictJson['label'] = strLabel
      elif str(type(dataParseResult[1]))==strParseResultsType:
        # print('ok 2')
        dictJson['tag'] = str(dataParseResult[0])
        dictJson['children']=[]
        dictJson['children'].append( walkAndGetPOSJson(dataParseResult[1],indexSentence,lstNonTerminals,lstTerminals))
        dictJson['isTerminal'] = False
        dictJson['value'] = ''
        newId = len(lstNonTerminals) + 1
        # strTag = dictJson['tag']
        strPosition = 'Sent_' + str(indexSentence) + '_NonTerminal_' + str(newId)
        dictJson['position'] = strPosition
        lstNonTerminals.append(strPosition)
        # dictJson['label'] = strLabel

  elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==1:
    # print('go to branch here')
    dictJson=walkAndGetPOSJson(dataParseResult[0],indexSentence,lstNonTerminals,lstTerminals)
  elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)>2:
    if str(type(dataParseResult[0])) == strStrType:
      strTag =str(dataParseResult[0])
      dictJson['tag']=strTag
      dictJson['value'] = ''
      dictJson['isTerminal'] = False
      dictJson['children'] = []
      newId = len(lstNonTerminals) + 1
      strPosition = 'Sent_' + str(indexSentence) + '_NonTerminal_' + str(newId)
      dictJson['position']=strPosition
      lstNonTerminals.append(strPosition)

      for i in range(1,len(dataParseResult)):
        dictChildI=walkAndGetPOSJson(dataParseResult[i],indexSentence,lstNonTerminals,lstTerminals)
        dictJson['children'].append(dictChildI)
  return dictJson

objParsed=OneOrMore(nestedExpr())
dictCommaItem={'tag': ',', 'value': ',', 'isTerminal': True, 'position': 'Sent_1_Terminal_X'}
def getGraphDependencyFromTextUsingNLTKArr(arrText,parser):
  dictTotal={}
  lstDicts=[]
  lstNonTerminals = []
  lstTerminals = []
  for strText in arrText:
    try:
      best = parser.parse(strText)
      strParseContent = str(best.get_parser_best().ptb_parse)
      # dictTotal=strParseContent
      data = objParsed.parseString(strParseContent)
      indexSentence = 1
      dictWords = {}
      dictItem = walkAndGetPOSJson(data, indexSentence, lstNonTerminals, lstTerminals)
      lstDicts.append(dictItem)
    except:
      # strJsonObj = '{}'
      dictItem={}
      traceback.print_exc()
  try:
    if len(lstDicts)>0:
      dictTotal=lstDicts[0]
      if 'tag' not in dictTotal.keys():
        dictTotal['tag']='S1'
      else:
        lenDicts=len(lstDicts)
        for i in range(1,lenDicts):
          lstChildren=lstDicts[i]['children']

          # append ,
          dictCommaCopy = copy.deepcopy(dictCommaItem)
          dictTotal['children'].append(dictCommaCopy)
          for child in lstChildren:
            dictTotal['children'].append(child)

  except:
    dictTotal={}
    traceback.print_exc()

  return dictTotal

def getGraphDependencyFromTextUsingNLTK(strText,parser):
  dictTotal={}
  try:
      best = parser.parse(strText)
      strParseContent = str(best.get_parser_best().ptb_parse)
      data = objParsed.parseString(strParseContent)
      lstNonTerminals = []
      lstTerminals = []
      indexSentence = 1
      dictWords = {}
      dictTotal = walkAndGetPOSJson(data, indexSentence, lstNonTerminals, lstTerminals)
  except:
    strJsonObj = '{}'
    dictTotal={}
    traceback.print_exc()
  return dictTotal


def getGraphDependencyFromText(strText,nlpObj):
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
      data = objParsed.parseString(strParseContent)
      dictWords = {}
      jsonPOS=walkAndGetPOSJson(data,indexSentence,lstNonTerminals,lstTerminals)
      # print('POS {}'.format(jsonPOS))

      # for dep in jsonDependency:
      #   strDep=dep['dep']
      #   if strDep=='ROOT':
      #       continue
      #   # print('dep : {}'.format(dep))
      #   indexSource=dep['governor']
      #   indexTarget=dep['dependent']
      #   itemTuple=(indexSource,indexTarget,strDep,lstTerminals[indexSource-1],lstTerminals[indexTarget-1])
      #   lstEdges.append(itemTuple)
      # jsonPOS['dependencies']=lstEdges
      dictTotal['children'].append(jsonPOS)
  except:
    strJsonObj = 'Error'
    dictTotal=None
    traceback.print_exc()
  return dictTotal

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fpPseudocodeBeforePOS=fopRoot+'pseudocode_before_pos.txt'
fpPseudocodeAfterPOS=fopRoot+'pseudocode_after_pos.txt'

model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

f1=open(fpPseudocodeBeforePOS,'r')
arrBeforeLines=f1.read().split('\n')
f1.close()
lstStrPOS=[]
# f1=open(fpPseudocodeAfterPOS,'w')
# f1.write('')
# f1.close()
dictStringPOS={}
start_time = time.time()
for i in range(0,len(arrBeforeLines)):
  if i<79900:
    continue

  itemStr=arrBeforeLines[i]
  if itemStr=='':
    lstStrPOS.append('{}\t{}'.format(i,'{}'))
  else:
    # itemStr='Hello it is me ( here )'
    arrItemStr=itemStr.split(' , ')
    # itemStr=arrItemStr[0]
    itemPOS=str(getGraphDependencyFromTextUsingNLTKArr(arrItemStr,parser))
    # itemPOS = str(getGraphDependencyFromTextUsingNLTK(itemStr, parser))
    # itemPOS = str(getGraphDependencyFromText(itemStr, nlp))
    itemToFile='{}\t{}'.format(i,itemPOS)
    lstStrPOS.append(itemToFile)
  # dictStringPOS[itemStr]='aaa'
  # print('end {}'.format((i+1)))
  if (i+1)%100==0 or (i+1)==len(arrBeforeLines):
    f1 = open(fpPseudocodeAfterPOS, 'a')
    f1.write('\n'.join(lstStrPOS)+'\n')
    f1.close()
    lstStrPOS = []
    end_time=time.time()
    duration = (end_time - start_time)
    print('until {} withduration {}'.format((i+1),duration))
    start_time=end_time
  # if (i+1)==10:
  #   break
duration= (time.time() - start_time)


