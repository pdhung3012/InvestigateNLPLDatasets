import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('..')))
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


# to run POS using stanfordnlp, you need to download models of stanford corenlp (https://stanfordnlp.github.io/CoreNLP/ ) and add the corenlp folder to your PATH environment
# then run the following commands to open the server:
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
fopStanfordCoreNLP='../../../dataPapers/stanford-corenlp-4.2.2/'

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

objParsed=OneOrMore(nestedExpr())
def getGraphDependencyFromTextUsingStanfordNLP(strText,nlpObj):
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
      dictTotal['children'].append(jsonPOS)
  except:
    strJsonObj = 'Error'
    dictTotal=None
    traceback.print_exc()
  return dictTotal

strSplitParsedTree='\n SplitParsedTree \n'
strSplitParsedLine='\n SplitParsedLine \n'
def getParsedTreesFromTextUsingStanfordNLP(strText,nlpObj):
  strOutput='ERROR'
  try:
    output = nlpObj.annotate(strText, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
    })
    jsonTemp = output
    # strJsonObj = jsonTemp
    arrSentences=jsonTemp['sentences']
    # dictTotal={}
    # dictTotal['tag'] = 'Paragraph'
    # dictTotal['label'] = 'Paragraph'
    # dictTotal['value'] = ''
    # dictTotal['isTerminal'] = False
    # dictTotal['children'] = []
    indexSentence=0
    # print(strText)
    lstOutput=[]
    for sentence in arrSentences:
      # jsonDependency = sentence['basicDependencies']
      strParseContent=sentence['parse']
      lstNonTerminals = []
      lstTerminals = []
      # indexSentence=indexSentence+1
      lstOutput.append(strParseContent)
      # data = objParsed.parseString(strParseContent)
      # dictWords = {}
      # jsonPOS=walkAndGetPOSJson(data,indexSentence,lstNonTerminals,lstTerminals)
      # dictTotal['children'].append(jsonPOS)
    strOutput=strSplitParsedTree.join(lstOutput)
  except:
    # strJsonObj = 'Error'
    # dictTotal=None
    traceback.print_exc()
  return strOutput


fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopPseudoTokens=fopRoot+'step2_pseudo_tokenize/'
fopEstimateTime=fopRoot+'estimate_time_pos/'
fopPseudocodePOS=fopRoot+'step2_pseudocode_pos_para_stanford/'
fpCachedFilePath=fopRoot+'cachedFilePaths_pseudo_tokenizes.txt'
createDirIfNotExist(fopEstimateTime)
fpEstimate=fopEstimateTime+'pos_estimation_paragraph_stanford.txt'
model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

lstFpJsonFiles=[]
if not os.path.isfile(fpCachedFilePath):
    lstFop1=sorted(glob.glob(fopPseudoTokens+'*/'))
    for fop1 in lstFop1:
        lstFp2=sorted(glob.glob(fop1+'*.txt'))
        for fp2 in lstFp2:
            lstFpJsonFiles.append(fp2)
        print('end {}'.format(fop1))
    # sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
    print('after {} '.format(len(lstFpJsonFiles)))
    f1=open(fpCachedFilePath,'w')
    f1.write('\n'.join(lstFpJsonFiles))
    f1.close()
else:
    f1=open(fpCachedFilePath,'r')
    lstFpJsonFiles=f1.read().split('\n')
    f1.close()

lstFpJsonFiles=sorted(lstFpJsonFiles,reverse=True)

f1=open(fpEstimate,'w')
f1.write('')
f1.close()
lstStrEstimate=[]
for i in range(0,len(lstFpJsonFiles)):
    fpItemPseudo=lstFpJsonFiles[i]
    # if i<=11600:
    #     continue
    try:
        f1=open(fpItemPseudo,'r')
        strPseudos=f1.read().strip().replace('\n',' . ')
        f1.close()
        lstStr=[]
        durationItem=0
        wordCount=0
        if strPseudos != '':
            strItem = strPseudos
            wordCount = wordCount + len(strItem.split())
            start_time = time.time()
            dictItem = getParsedTreesFromTextUsingStanfordNLP(strItem, nlp)
            end_time = time.time()
            durationItem = durationItem + (end_time - start_time)
        else:
            dictItem = 'ERROR'
        lstStr.append(str(dictItem))

        fpItemPOS=fpItemPseudo.replace(fopPseudoTokens,fopPseudocodePOS)
        arrFpPOS=fpItemPOS.split('/')
        fopItemPOS='/'.join(arrFpPOS[:(len(arrFpPOS)-1)])
        createDirIfNotExist(fopItemPOS)
        f1=open(fpItemPOS,'w')
        f1.write(strSplitParsedLine.join(lstStr))
        f1.close()

        strEstimate='{}\t{}\t{}'.format(wordCount,durationItem,fpItemPseudo)
        lstStrEstimate.append(strEstimate)
        if (i+1)%100==0 or (i+1)==len(lstFpJsonFiles):
            print('end {}'.format((i+1)))
            if len(lstStrEstimate)>0:
                f1=open(fpEstimate,'a')
                f1.write('\n'.join(lstStrEstimate)+'\n')
                f1.close()
                lstStrEstimate=[]
    except:
        traceback.print_exc()
print('complete')