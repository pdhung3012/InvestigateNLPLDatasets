from nltk.data import find
from bllipparser import RerankingParser
import nltk
from pyparsing import OneOrMore, nestedExpr

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"
nltk.download('bllip_wsj_no_aux')

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



model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)

numIter=1000000
indexSentence=1
for i in range(0,numIter):
    best = parser.parse("The old oak tree from India fell down. I love you. ")
    strParseContent=str(best.get_parser_best().ptb_parse)
    data = OneOrMore(nestedExpr()).parseString(strParseContent)
    lstNonTerminals = []
    lstTerminals = []
    indexSentence = indexSentence + 1
    dictWords = {}
    jsonPOS = walkAndGetPOSJSon(data, indexSentence, lstNonTerminals, lstTerminals)
    print('{}\n{}\n{}'.format((i+1),strParseContent,jsonPOS))
    # print(best.get_reranker_best())
    # print(best.get_parser_best())