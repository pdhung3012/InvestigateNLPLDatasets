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

fopStanfordCoreNLP='../../../../dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
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

def addNodeEdgeForNLPart(dictNL,dictFatherLabel,graph,strId):
    # isTerminal=dictNL['isTerminal']
    strNewKey=strId+'\n'+str(dictNL['label'])
    # if 'label' in dictNL.keys():
    #     strNewKey=strId+'\n'+str(dictNL['label'])
    graph.add_node(strNewKey,color='red')
    lstChildren=dictNL['children']
    for i in range(0,len(lstChildren)):
        strChildKey=addNodeEdgeForNLPart(lstChildren[i],dictFatherLabel,graph,strId)
        if strNewKey!=strChildKey:
            graph.add_edge(strNewKey,strChildKey,color='red')
            dictFatherLabel[strChildKey]=strNewKey

    if 'dependencies' in dictNL.keys():
        lstDeps=dictNL['dependencies']
        for i in range(0,len(lstDeps)):
            tup=lstDeps[i]
            strSource=strId+'\n'+tup[3]
            strTarget = strId + '\n' + tup[4]
            if strSource!=strTarget:
                graph.add_edge(strSource,strTarget,color='green',label=tup[2])
    return strNewKey


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
    dictTotal=None
    traceback.print_exc()
  return dictTotal


batch_size=100000
strEndLine=' ENDLINE '
strTabChar=' TABCHAR '
strSingleComment=' SINGLECOMMENTCHAR '

# fopCCContent='/home/hungphd/media/dataPapersExternal/apiCallPapers_v1/AlonCommentExtraction/'
fopTextCorpus='/home/hungphd/media/dataPapersExternal/textCorpus/'
fopPOSCorpus='/home/hungphd/media/dataPapersExternal/posCorpus/'
fopParseTreeCorpus='/home/hungphd/media/dataPapersExternal/treeCorpus/'
createDirIfNotExist(fopPOSCorpus)
lstTypesOfSDs=['ad','cs','cc','cm','qa','sr']

for item in lstTypesOfSDs:
    try:
        fopItemTextCorpus = fopTextCorpus + item + '/'
        lstTextFiles = sorted(glob.glob(fopItemTextCorpus + '/*.txt'))
        f1=open(lstTextFiles[i],'r')
        arrTexts=f1.read().split('\t')
        f1.close()
        for i in range(0,len(arrTexts)):
            try:

            except:
                traceback.print_exc()

    except:
        traceback.print_exc()



