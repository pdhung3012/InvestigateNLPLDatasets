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

fopStanfordCoreNLP='../../../../dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
strSplitElement=' SPLITELEMENT '
def walkAndGetPOSJSon(dataParseResult,lstTerminals):
  dictJson={}
  if str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==2:
    # print( str(type(dataParseResult[0])))
    if str(type(dataParseResult[0]))==strStrType:
      if  str(type(dataParseResult[1]))==strStrType:
        # print('ok1')
        # dictJson['tag']=str(dataParseResult[0])
        # dictJson['value'] = str(dataParseResult[1])
        # dictJson['isTerminal'] = True
        # dictJson['children'] = []

        # newId = len(lstTerminals) + 1
        # strValue=dictJson['value']
        # strTag=dictJson['tag']
        # strLabel ='Sent'+str(indexSentence) +'_Terminal'+str(newId)+'\n'+strTag + '\n' + strValue
        tupTerminal=(str(dataParseResult[0]),str(dataParseResult[1]))
        lstTerminals.append(tupTerminal)
      elif str(type(dataParseResult[1]))==strParseResultsType:
        # print('ok 2')
        # dictJson['tag'] = str(dataParseResult[0])
        # dictJson['children']=[]
        # dictJson['children'].append( walkAndGetPOSJSon(dataParseResult[1],indexSentence,lstNonTerminals,lstTerminals))
        walkAndGetPOSJSon(dataParseResult[1], lstTerminals)
        # dictJson['isTerminal'] = False
        # dictJson['value'] = ''
        # newId = len(lstNonTerminals) + 1
        # strTag = dictJson['tag']
        # strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
        # lstNonTerminals.append(strLabel)
        # dictJson['label'] = strLabel

  elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==1:
    # print('go to branch here')
    walkAndGetPOSJSon(dataParseResult[0],lstTerminals)
  elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)>2:
    if str(type(dataParseResult[0])) == strStrType:
      # strTag =str(dataParseResult[0])
      # dictJson['tag']=strTag
      # dictJson['value'] = ''
      # dictJson['isTerminal'] = False
      # dictJson['children'] = []
      # newId = len(lstNonTerminals) + 1
      # strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
      # lstNonTerminals.append(strLabel)
      # dictJson['label'] = strLabel
      for i in range(1,len(dataParseResult)):
        dictChildI=walkAndGetPOSJSon(dataParseResult[i],lstTerminals)
        # dictJson['children'].append(dictChildI)
  # return dictJson

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
  lstPOSAll = []
  lstTreeAll = []
  lstTextAll = []
  try:
    output = nlpObj.annotate(strText, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
    })
    # print(output)
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

    for sentence in arrSentences:
      jsonDependency = sentence['basicDependencies']
      strParseContent=sentence['parse']
      lstNonTerminals = []
      lstTerminals = []
      indexSentence=indexSentence+1
      data = OneOrMore(nestedExpr()).parseString(strParseContent)
      dictWords = {}
      walkAndGetPOSJSon(data,lstTerminals)

      list1 = []
      list2 = []
      for i in lstTerminals:
          list1.append(i[0])
          list2.append(i[1])
      strPOS=' '.join(list1)
      strText=' '.join(list2)

      lstTextAll.append(strText)
      lstPOSAll.append(strPOS)
      lstTreeAll.append(strParseContent)

      # print('terminal {}'.format(lstTerminals))
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
      # dictTotal['children'].append(jsonPOS)
  except:
    strJsonObj = 'Error'
    # dictTotal=None
    traceback.print_exc()
  strTextAll=strSplitElement.join(lstTextAll).replace('\n',strEndLine)
  strPOSAll = strSplitElement.join(lstPOSAll).replace('\n',strEndLine)
  strTreeAll = strSplitElement.join(lstTreeAll).replace('\n',strEndLine)
  return strTextAll,strTreeAll,strPOSAll
  # return dictTotal

def extractPOSAndTree(fopTextCorpus,fopPOSCorpus,item,nlpObj):
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
                fpTree = fopItemPOSCorpus + indexName + '_tree.txt'
                fpTextPreprocess = fopItemPOSCorpus + indexName + '_preprocess.txt'
                # print('go here')
                f1 = open(fpPOS, 'w')
                f1.write('')
                f1.close()
                f1 = open(fpTree, 'w')
                f1.write('')
                f1.close()
                f1 = open(fpTextPreprocess, 'w')
                f1.write('')
                f1.close()

                for i in range(0, len(arrTexts)):
                    try:
                        strItem = arrTexts[i].replace(strEndLine, '\m').replace(strTabChar, '\t').replace('// ','')
                        strPostText, strTree, strPOS = getGraphDependencyFromText(strItem, nlpObj)
                        if strPostText != '':
                            lstProcessTextPerFile.append(strPostText)
                            lstTreePerFile.append(strTree)
                            lstPOSPerFile.append(strPOS)

                        if((len(lstProcessTextPerFile)>0) and (((i+1)==len(arrTexts)) or ((i+1)%1000==0))):
                            f1 = open(fpPOS, 'a')
                            f1.write('\n'.join(lstPOSPerFile)+'\n')
                            f1.close()
                            f1 = open(fpTree, 'a')
                            f1.write('\n'.join(lstTreePerFile)+'\n')
                            f1.close()
                            f1 = open(fpTextPreprocess, 'a')
                            f1.write('\n'.join(lstProcessTextPerFile)+'\n')
                            f1.close()
                            lstProcessTextPerFile=[]
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
from pycorenlp import StanfordCoreNLP


# for item in lstTypesOfSDs:

from multiprocessing.pool import ThreadPool as Pool

# from multiprocessing import Pool
from multiprocessing import Process
lstThreads=[]
for i in range(0,len(lstTypesOfSDs)):
    strServerPort='900'+str(i)
    nlpObj = StanfordCoreNLP('http://localhost:'+strServerPort)
    print('start thread {}'.format(i))
    p1=Process(target=extractPOSAndTree,args=[fopTextCorpus,fopPOSCorpus,lstTypesOfSDs[i],nlpObj])
    p1.start()
    lstThreads.append(p1)

for i in range(0,len(lstTypesOfSDs)):
    lstThreads[i].join()



