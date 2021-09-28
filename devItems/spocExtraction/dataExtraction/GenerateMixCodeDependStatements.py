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
from pyparsing import OneOrMore, nestedExpr
import nltk
from nltk.data import find
from bllipparser import RerankingParser

nltk.download('bllip_wsj_no_aux')

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"

strRegexCamelCases=r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))'

strStmtSplit=' StmtSplit '
strTabChar=' tabChar '
strEndLineChar=' endLineChar '
strSplitIndent=' IndentSplit '
strSplitJson=' JsonSplit '
# fopStanfordCoreNLP='../../../dataPapers/stanford-corenlp-4.2.2/'
# nlpObj = StanfordCoreNLP('http://localhost:9000')
model_dir = find('models/bllip_wsj_no_aux').path
parser = RerankingParser.from_unified_model_dir(model_dir)


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
      best = parser.parse("The old oak tree from India fell down. I love you. ")
      strParseContent = str(best.get_parser_best().ptb_parse)
      data = OneOrMore(nestedExpr()).parseString(strParseContent)
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

def walkJsonAndGetIndent(jsonObject,dictLinesAndElements,indent):
    try:
        # if indent not in dictIndents.keys():
        #     dictIndents[indent]=[]
        jsonObject['indent']=indent
        # dictIndents[indent].append(jsonObject)

        startLine=jsonObject['startLine']
        endLine=jsonObject['endLine']
        strLineOffset='{}-{}'.format(startLine,endLine)
        if strLineOffset not in dictLinesAndElements.keys():
            dictLinesAndElements[strLineOffset]={}
            dictLinesAndElements[strLineOffset]['children']=[jsonObject]
        else:
            dictLinesAndElements[strLineOffset]['children'].append(jsonObject)

        if 'children' in jsonObject.keys():
            lstChildren=jsonObject['children']
            indentChild=indent+1
            for i in range(0,len(lstChildren)):
                walkJsonAndGetIndent(lstChildren[i],dictLinesAndElements,indentChild)
    except:
        traceback.print_exc()

def walkAndFindErrorInsideObject(jsonObject):
    isHavingError=False
    try:
        if jsonObject['type']=='ERROR':
            isHavingError=True
        elif 'children' in jsonObject.keys():
            lstChildren=jsonObject['children']
            for i in range(0,len(lstChildren)):
                isHavingError=walkAndFindErrorInsideObject(lstChildren[i])
                if isHavingError:
                    break
    except:
        traceback.print_exc()
    return isHavingError

def findReplaceableStatements(dictLinesAndElements,lstTupFunctionDeclarations):
    try:
        # find tuples of method declarations
        for item in dictLinesAndElements.keys():
            if dictLinesAndElements[item]['children'][0]['type']=='function_definition':
                obj=dictLinesAndElements[item]['children'][0]
                startLine=obj['startLine']
                endLine=obj['endLine']
                tup=(startLine,endLine)
                # print('go here')
                lstTupFunctionDeclarations.append(tup)

        lstPopKeys=[]
        for item in dictLinesAndElements.keys():
            arrStartEnd=item.split('-')
            startLine=int(arrStartEnd[0])
            endLine=int(arrStartEnd[1])
            isInFD=False
            selectedTup=None
            for tup in lstTupFunctionDeclarations:
                if startLine>tup[0] and endLine<tup[1]:
                    isInFD=True
                    selectedTup=tup
                    break

            if not isInFD:
                # dictLinesAndElements.pop(item, None)
                lstPopKeys.append(item)
                continue
            else:
                dictLinesAndElements[item]['scopeOfMethods']=selectedTup

        for key in lstPopKeys:
            dictLinesAndElements.pop(key, None)
        lstPopKeys=[]
        print('dict after check method scope {}'.format(len(dictLinesAndElements)))

        for item in dictLinesAndElements.keys():
            selectedTup=dictLinesAndElements[item]['scopeOfMethods']
            lstChildren = dictLinesAndElements[item]['children']
            dictIndentElements = {}
            for j in range(0, len(lstChildren)):
                itemEleJ = lstChildren[j]
                indIndent = itemEleJ['indent']
                if indIndent not in dictIndentElements.keys():
                    dictIndentElements[indIndent] = [itemEleJ]
                else:
                    dictIndentElements[indIndent].append(itemEleJ)
            dictLinesAndElements[item]['sortedElementsByIndents'] = dictIndentElements
            # main sstatement is the node that is closest to the root. If there are 2 or more nodes in the same deep, we calculate
            indentDeepest = sorted(dictLinesAndElements[item]['sortedElementsByIndents'].keys())[0]
            lstPossibleStatements = dictLinesAndElements[item]['sortedElementsByIndents'][indentDeepest]
            # mainStmt = ''
            selectItem = lstPossibleStatements[0]
            isHavingError=False
            if len(lstPossibleStatements) == 1:
                selectItem['singleRoot']=True
                isHavingError=walkAndFindErrorInsideObject(selectItem)
            else:
                # for j in range(1, len(lstPossibleStatements)):
                #     candItem = lstPossibleStatements[j]
                #     isHavingError = walkAndFindErrorInsideObject(selectItem)
                #     if isHavingError:
                #         break
                #     if candItem['startLine'] < selectItem['startLine'] and candItem['endLine'] > selectItem['endLine']:
                #         selectItem = candItem
                #     elif candItem['startLine'] == selectItem['startLine'] and candItem['endLine'] == selectItem[
                #         'endLine']:
                #         if (candItem['endOffset'] - candItem['startOffset']) > (
                #                 selectItem['endOffset'] - selectItem['startOffset']):
                #             selectItem = candItem
                # selectItem['singleRoot'] = False
                lstPopKeys.append(item)

            # mainStmt = '{}-{}-{}-{}-{}'.format(selectItem['type'], selectItem['startLine'], selectItem['startOffset'],
            #                                    selectItem['endLine'], selectItem['endOffset'])
            dictLinesAndElements[item]['mainStmt'] = selectItem
            selectItem['isReplaceable'] = True

            if isHavingError:
                lstPopKeys.append(item)
            elif (selectItem['startLine']-selectedTup[0]<2) or (selectedTup[1] -selectItem['endLine']<2):
                lstPopKeys.append(item)
            elif selectItem['startLine']==selectItem['endLine'] and (selectItem['endOffset']-selectItem['startOffset']<=3):
                lstPopKeys.append(item)



        for key in lstPopKeys:
            dictLinesAndElements.pop(key, None)
        lstPopKeys=[]
        print('dict after check replaceable {}'.format(len(dictLinesAndElements)))

        #  select the indent with most isReplaceable items
        dictIndentAndStatements={}
        for key in dictLinesAndElements.keys():
            mainStmt=dictLinesAndElements[key]['mainStmt']
            indent=mainStmt['indent']
            if indent not in dictIndentAndStatements.keys():
                dictIndentAndStatements[indent]=1
            else:
                dictIndentAndStatements[indent]=dictIndentAndStatements[indent]+1
        dictIndentAndStatements = dict(sorted(dictIndentAndStatements.items(), key=operator.itemgetter(1), reverse=True))
        print('indent {}'.format(dictIndentAndStatements))
        if len(dictIndentAndStatements.keys())>0:
            for key in lstPopKeys:
                dictLinesAndElements.pop(key,None)
            highestIndent=list(dictIndentAndStatements.keys())[0]
            for key in dictLinesAndElements.keys():
                mainStmt = dictLinesAndElements[key]['mainStmt']
                indent = mainStmt['indent']
                if indent!=highestIndent:
                    lstPopKeys.append(key)
                    # dictLinesAndElements.pop(key,None)
        for key in lstPopKeys:
            dictLinesAndElements.pop(key,None)
        lstPopKeys=[]
        print('dict after indent selection {}'.format(len(dictLinesAndElements)))
    except:
        traceback.print_exc()

def checkAppearInImplementation(dictLiterals,strPseudo,strCode):
    strPseudoSplit=''
    strCodeSplit=''
    strTokSplit=''
    strCodeTokSplit = ''
    try:
        # print('code {}'.format(strCode))
        arrPseudos=strPseudo.split()
        arrCodes=strCode.split()
        lstTokCode=[]
        for itemCode in arrCodes:
            # print('itemCode {}'.format(itemCode))
            arrCodeSplit=re.findall(strRegexCamelCases, itemCode)
            if len(arrCodeSplit)==0:
                arrCodeSplit=[itemCode]
            # print('arr {}'.format(arrCodeSplit))
            for item in arrCodeSplit:
                # print('abc {}'.format(item))
                lstTokCode.append(item.lower())
        setTokCode=set(lstTokCode)
        lstTokPseudo=[]
        numAppear=0
        numDisappear=0
        for itemPseudo in arrPseudos:
            isAppear = False
            if itemPseudo.startswith('SpecialLiteral_'):
                # print('itemPseudo {}'.format(itemPseudo))
                # input('I love')
                valItem=dictLiterals[itemPseudo]
                # print('val {}\nstr {}'.format(valItem,strCode))
                if valItem in strCode:
                    isAppear=True
                else:
                    isAppear=False
            else:
                arrPseudoSplit = re.findall(strRegexCamelCases, itemPseudo)
                if len(arrPseudoSplit)==0:
                    arrPseudoSplit=[itemPseudo]
                isAppear=False
                for item in arrPseudoSplit:
                    strItLower=item.lower()
                    if not strItLower in setTokCode:
                        isAppear=False
                        break
                    else:
                        isAppear=True
            if isAppear:
                numAppear=numAppear+1
                lstTokPseudo.append(itemPseudo+'#1')
            else:
                numDisappear=numDisappear+1
                lstTokPseudo.append(itemPseudo + '#0')
        strPseudoSplit=' '.join(arrPseudos)
        strCodeSplit=' '.join(arrCodes)
        strTokSplit=' '.join(lstTokPseudo)
        strCodeTokSplit=' '.join(lstTokCode)
    except:
        traceback.print_exc()
    percent=0
    if (numAppear+numDisappear)!=0:
        percent=numAppear*1.0/(numAppear+numDisappear)
    else:
        percent=0
    return strCodeSplit,strCodeTokSplit,strPseudoSplit,strTokSplit,numAppear,numDisappear,percent

def generateMixVersionsAndLabels(dictLinesAndElements,dictLabelStatistics,dictLiterals,arrCodes,arrPseudos,fopCodeVersion,fonameItemAST,idCode,fopAllocateByMainStmt,fopAllocateByNumOfStmts,parser):
    try:
        isOK=False
        indexVersion=0
        fpItemPseudo=fopCodeVersion+'_a_pseudo.txt'
        fpItemCode=fopCodeVersion+'_a_code.cpp'
        f1=open(fpItemPseudo,'w')
        f1.write('\n'.join(arrPseudos))
        f1.close()
        f1=open(fpItemCode,'w')
        f1.write('\n'.join(arrCodes))
        f1.close()

        for keyItem in dictLinesAndElements.keys():
            valItem=dictLinesAndElements[keyItem]
            indexVersion=indexVersion+1
            fnIndexVersion='v_{}'.format(indexVersion)
            fpItemVersionCode=fopCodeVersion+fnIndexVersion+'_mix.cpp'
            fpItemVersionLabel = fopCodeVersion + fnIndexVersion + '_label.txt'
            mainStmt = valItem['mainStmt']
            startLineMainStmt=mainStmt['startLine']
            endLineMainStmt = mainStmt['endLine']

            lstPseudoLines=range(startLineMainStmt-distanceHeader,endLineMainStmt-distanceHeader+1)
            lstStrPseudoLines=[]
            lstStrCodeLines = []
            for it in lstPseudoLines:
                lstStrPseudoLines.append(arrPseudos[it])
                lstStrCodeLines.append(arrCodes[it+distanceHeader])

            strPOSComment=' , then '.join(lstStrPseudoLines)
            strTotalComment = '// ' + strPOSComment
            dictPOSJson={}
            dictPOSJson = getGraphDependencyFromTextUsingNLTK(strPOSComment, parser)
            strTotalCode=' '.join(lstStrCodeLines)
            strCodeSplit,strCodeTokSplit,strPseudoSplit,strTokSplit,numAppear,numDisappear,percent=checkAppearInImplementation(dictLiterals,strTotalComment,strTotalCode)

            lstMixCodes = []
            for i in range(0,len(arrCodes)):
                itemLine=arrCodes[i]
                numTabs=0
                strLineAdd=arrCodes[i]

                if (i-distanceHeader) in lstPseudoLines:
                    lstStrs = []
                    while(itemLine[numTabs]=='\t'):
                        numTabs=numTabs+1
                        lstStrs.append('\t')
                        if numTabs == len(itemLine):
                            break
                    if i == startLineMainStmt:
                        strLineAdd='{}{}'.format(''.join(lstStrs),strTotalComment)
                    else:
                        strLineAdd = '{}{}'.format(''.join(lstStrs), '//')
                lstMixCodes.append(strLineAdd)
            f1=open(fpItemVersionCode,'w')
            f1.write('\n'.join(lstMixCodes))
            f1.close()

            strMainStatement=mainStmt['type']
            strPosition='{}-{}-{}-{}'.format(mainStmt['startLine'],mainStmt['startOffset'],mainStmt['endLine'],mainStmt['endOffset'])
            numOfLine=endLineMainStmt-startLineMainStmt+1
            numOfStatements=0
            lstListOfBelowStatements=[]
            strDictToString=''
            if mainStmt['singleRoot']:
                numOfStatements=1
                lstListOfBelowStatements.append(mainStmt['type'])
                if 'children' in mainStmt.keys():
                    for child in mainStmt['children']:
                        if 'isReplaceable' in child.keys() and child['isReplaceable']:
                            strStmtChild=child['type']
                            numOfStatements=numOfStatements+1
                            lstListOfBelowStatements.append(strStmtChild)
                strDictToString=str(mainStmt)
            else:
                indentDeepest = sorted(dictLinesAndElements[keyItem]['sortedElementsByIndents'].keys())[0]
                lstPossibleStatements = dictLinesAndElements[keyItem]['sortedElementsByIndents'][indentDeepest]
                numOfStatements=len(lstPossibleStatements)
                for stmt in lstPossibleStatements:
                    lstListOfBelowStatements.append(stmt['type'])
                strDictToString =strSplitJson.join(map(str,lstPossibleStatements))
            strBelowStatements=strStmtSplit.join(lstListOfBelowStatements)

            if strMainStatement not in dictLabelStatistics['mainStmt'].keys():
                dictLabelStatistics['mainStmt'][strMainStatement]=1
            else:
                dictLabelStatistics['mainStmt'][strMainStatement] =dictLabelStatistics['mainStmt'][strMainStatement] + 1

            if numOfStatements not in dictLabelStatistics['numOfStatements'].keys():
                dictLabelStatistics['numOfStatements'][numOfStatements]=1
            else:
                dictLabelStatistics['numOfStatements'][numOfStatements] =dictLabelStatistics['numOfStatements'][numOfStatements] + 1


            f1=open(fpItemVersionLabel,'w')
            strLbl='{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\t{}\t{}\n{}'.format(strMainStatement,strPosition,numOfLine,numOfStatements,strBelowStatements,strDictToString, strCodeSplit,strCodeTokSplit,strPseudoSplit,strTokSplit,numAppear,numDisappear,percent,str(dictPOSJson))
            f1.write(strLbl)
            f1.close()

            fopItemAllMainStmt=fopAllocateByMainStmt+strMainStatement+'/'+fonameItemAST+'/'+idCode+'/'
            createDirIfNotExist(fopItemAllMainStmt)
            fopItemAllNumOfStmts = fopAllocateByNumOfStmts + str(numOfStatements) + '/' + fonameItemAST + '/' + idCode + '/'
            createDirIfNotExist(fopItemAllNumOfStmts)



            # if os.path.isdir(fopItemAllMainStmt):
            #     shutil.rmtree(fopItemAllMainStmt)
            # if os.path.isdir(fopItemAllNumOfStmts):
            #     shutil.rmtree(fopItemAllNumOfStmts)
            shutil.copy(fopCodeVersion+fnIndexVersion+'_mix.cpp', fopItemAllMainStmt+fnIndexVersion+'_mix.cpp')
            shutil.copy(fopCodeVersion+fnIndexVersion+ '_label.txt', fopItemAllMainStmt+fnIndexVersion+ '_label.txt')
            shutil.copy(fopCodeVersion+fnIndexVersion+'_mix.cpp', fopItemAllNumOfStmts+fnIndexVersion+'_mix.cpp')
            shutil.copy(fopCodeVersion + fnIndexVersion + '_label.txt',fopItemAllNumOfStmts + fnIndexVersion + '_label.txt')

    except:
        traceback.print_exc()

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopCodeFile=fopRoot+'step2_tokenize/'
fopPseudoFile=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopLabels=fopRoot+'step2_pseudo_tokenize/'
fopTreeSitterFile=fopRoot+'step3_treesitter_tokenize/'
fopMixVersion=fopRoot+'step4_mixCode/'
fopAllocateByMainStmt=fopRoot+'step4_mainStmt/'
fopAllocateByNumOfStmts=fopRoot+'step4_numOfStatements/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
createDirIfNotExist(fopMixVersion)
createDirIfNotExist(fopAllocateByMainStmt)
createDirIfNotExist(fopAllocateByNumOfStmts)

f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiterals={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiterals[arrTabs[0]]=strContent

# print('len dict {}'.format(len(dictLiterals.keys())))
# input('abc ')


lstFpDictASTs=glob.glob(fopTreeSitterFile+'**/*_code_ast.txt',recursive=True)
distanceHeader=33

dictLabelStatistics={}
dictLabelStatistics['mainStmt']={}
dictLabelStatistics['numOfStatements']={}
if os.path.isdir(fopMixVersion):
    shutil.rmtree(fopMixVersion)

for i in range(0,len(lstFpDictASTs)):
    fpItemAST=lstFpDictASTs[i]
    fnItemAST=os.path.basename(fpItemAST)
    fopItemAST=os.path.dirname(fpItemAST)
    fonameItemAST=os.path.basename(fopItemAST)
    try:
        idCode=fnItemAST.replace('_code_ast.txt','')
        fpItemPseudo=fopPseudoFile+fonameItemAST+'/'+idCode+'_text.txt'
        fpItemCode = fopCodeFile + fonameItemAST+'/' + idCode + '_code.cpp'
        fopCodeVersion=fopMixVersion+fonameItemAST+'/'+idCode+'/'
        if os.path.isdir(fopCodeVersion):
            shutil.rmtree(fopCodeVersion)
        createDirIfNotExist(fopCodeVersion)
        fnLogOutput='a_logPrint.txt'
        fpCodeLogOutput=fopCodeVersion+fnLogOutput
        fpCodeJsonOutput = fopCodeVersion + 'a_json.txt'

        sys.stdout = open(fpCodeLogOutput, 'w')
        f1=open(fpItemPseudo,'r')
        arrPseudos=f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpItemCode, 'r')
        arrCodes = f1.read().strip().split('\n')
        f1.close()
        f1=open(fpItemAST,'r')
        strASTContent=f1.read().strip().split('\n')[1]
        f1.close()
        jsonObject = ast.literal_eval(strASTContent)
        f1=open(fpCodeJsonOutput,'w')
        f1.write(str(jsonObject))
        f1.close()
        dictLinesAndElements={}
        indent=1
        lstTupFunctionDeclarations=[]
        walkJsonAndGetIndent(jsonObject,dictLinesAndElements,indent)
        print('dict before {}'.format(len(dictLinesAndElements.keys())))
        findReplaceableStatements(dictLinesAndElements, lstTupFunctionDeclarations)
        print('dict after {}'.format(len(dictLinesAndElements.keys())))
        # print('dict final content\n{}'.format(dictLinesAndElements))
        generateMixVersionsAndLabels(dictLinesAndElements,dictLabelStatistics,dictLiterals,arrCodes,arrPseudos,fopCodeVersion,fonameItemAST,idCode,fopAllocateByMainStmt,fopAllocateByNumOfStmts,parser)

        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print('end {}/{} {}'.format(i,len(lstFpDictASTs),fpCodeLogOutput))
        # if i==2000:
        #     break
    except:
        traceback.print_exc()

fpDictLblMainStmt=fopMixVersion+ 'labels_mainStmt.txt'
fpDictLblNumOfStatement=fopMixVersion+ 'labels_numOfStatement.txt'

dictSorted=dict(sorted(dictLabelStatistics['mainStmt'].items(), key=operator.itemgetter(1), reverse=True))
lstStr=[]
for key in dictSorted.keys():
    lstStr.append('{}\t{}'.format(key,dictSorted[key]))
f1=open(fpDictLblMainStmt,'w')
f1.write('\n'.join(lstStr))
f1.close()

dictSorted=dict(sorted(dictLabelStatistics['numOfStatements'].items(), key=operator.itemgetter(1), reverse=True))
lstStr=[]
for key in dictSorted.keys():
    lstStr.append('{}\t{}'.format(key,dictSorted[key]))
f1=open(fpDictLblNumOfStatement,'w')
f1.write('\n'.join(lstStr))
f1.close()