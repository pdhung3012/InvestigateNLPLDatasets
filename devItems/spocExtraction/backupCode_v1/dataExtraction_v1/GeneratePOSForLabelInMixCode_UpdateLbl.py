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


fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopMixVersion=fopRoot+'step4_mixCode/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
fpPseudocodeBeforePOS=fopRoot+'pseudocode_before_pos.txt'
fpCachedFilePath=fopRoot+'cachedFilePaths.txt'
fpBeforePOS=fopRoot+'pseudocode_before_pos.txt'
fpAfterPOS=fopRoot+'pseudocode_after_pos.txt'
createDirIfNotExist(fopMixVersion)

model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)


print('before traverse')
lstFpJsonFiles=[]
if not os.path.isfile(fpCachedFilePath):
    lstFop1=sorted(glob.glob(fopMixVersion+'*/'))
    for fop1 in lstFop1:
        lstFop2=sorted(glob.glob(fop1+'*/'))
        for fop2 in lstFop2:
            lstFop3=sorted(glob.glob(fop2+'v_*_label.txt'))
            # print(fp3)
            for fp3 in lstFop3:
                lstFpJsonFiles.append(fp3)
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

f1=open(fpBeforePOS,'r')
arrRawText=f1.read().split('\n')
f1.close()

f1=open(fpAfterPOS,'r')
arrPOSJson=f1.read().split('\n')
f1.close()

dictTextAndPOS={}
for i in range(0,len(arrPOSJson)):
    arrTabs=arrPOSJson[i].split('\t')
    if(len(arrTabs)>=2):
        strJsonContent='\t'.join(arrTabs[1:])
        idx=int(arrTabs[0])
        dictTextAndPOS[arrRawText[idx]]=strJsonContent

print('end load dictTextPOS {}'.format(len(dictTextAndPOS)))

distanceHeader=33
totalNumLineProcess=0
# f1=open(fpPseudocodeBeforePOS,'w')
# f1.write('')
# f1.close()
lstStrPseudos=[]
for i in range(0,len(lstFpJsonFiles)):
    fpItemLabel=lstFpJsonFiles[i]
    try:
        # if(i+1)< 108937:
        #     continue
        f1=open(fpItemLabel,'r')
        arrItLabels=f1.read().strip().split('\n')
        f1.close()
        if len(arrItLabels) >= 12:
            strText = arrItLabels[8].replace('// ', '', 1).strip()
            if strText in dictTextAndPOS.keys():
                strNewPOS = dictTextAndPOS[strText]
            elif not strText=='':
                arrItemStr = strText.split(' , ')
                # itemStr=arrItemStr[0]
                strNewPOS = str(getGraphDependencyFromTextUsingNLTKArr(arrItemStr, parser))
                print('number {} need to be generated {}'.format(i,fpItemLabel))
            else:
                strNewPOS='{}'
            arrItLabels[11] = strNewPOS
        # if len(arrItLabels)>=12 and not ('oak' in arrItLabels[11] and 'India' in arrItLabels[11]):
        #     totalNumLineProcess = totalNumLineProcess + 1
        #     print('skip {}/{} {} total {}'.format(i, len(lstFpJsonFiles), fpItemLabel,totalNumLineProcess))
        #     continue
        # strText=arrItLabels[8].replace('// ','',1).strip()
        # strNewPOS=getGraphDependencyFromTextUsingNLTK(strText,parser)
        # arrItLabels[11]=str(strNewPOS)
        f1 = open(fpItemLabel, 'w')
        f1.write('\n'.join(arrItLabels))
        f1.close()
        # totalNumLineProcess = totalNumLineProcess + 1
        if ((i+1)%1000==0) or ((i+1)==len(lstFpJsonFiles)):
            print('end {}/{} total {}'.format(i,len(lstFpJsonFiles),totalNumLineProcess))


    except:
        f1 = open(fpItemLabel, 'r')
        arrItLabels = f1.read().strip().split('\n')
        f1.close()
        if len(arrItLabels)>=12:
            arrItLabels[11] = '{}'
            f1 = open(fpItemLabel, 'w')
            f1.write('\n'.join(arrItLabels))
            f1.close()
        traceback.print_exc()


