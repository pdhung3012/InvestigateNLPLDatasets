import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('../..')))
sys.path.append(os.path.abspath(os.path.join('../../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import pygraphviz as pgv
import pylab,traceback
from pyparsing import OneOrMore, nestedExpr

fopStanfordCoreNLP='../../../dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"

def getPrefixId(startPointLine,startPointOffset,endPointLine,endPointOffset):
    strId='{}--{}--{}--{}'.format(startPointLine,startPointOffset,endPointLine,endPointOffset)
    return strId

def getLineAndOffsetFromLabel(strLabel):
    # print(strLabel)
    arrLineInfo=strLabel.split('\n')[0].strip().split('--')
    startLine=int(arrLineInfo[0])
    startOffset = int(arrLineInfo[1])
    endLine = int(arrLineInfo[2])
    endOffset = int(arrLineInfo[3])
    return (startLine,startOffset,endLine,endOffset)

def getTerminalValue(startPointLine,startPointOffset,endPointLine,endPointOffset,arrCodes):
    lstStr=[]
    if startPointLine==endPointLine:
        return arrCodes[startPointLine][startPointOffset:endPointOffset]
    for i in range(startPointLine,endPointLine+1):

        if i==startPointLine:
            strAdd=arrCodes[i][startPointOffset:]
            lstStr.append(strAdd)
        elif i==endPointLine:
            strAdd = arrCodes[i][:endPointOffset]
            lstStr.append(strAdd)
        else:
            strAdd = arrCodes[i]
            lstStr.append(strAdd)
    strReturn='\n'.join(lstStr)
    return strReturn

# def addNodeEdgeForNLPart(dictNL,dictFatherLabel,graph,strId):
#     # isTerminal=dictNL['isTerminal']
#     strNewKey=strId+'\n'+str(dictNL['label'])
#     # if 'label' in dictNL.keys():
#     #     strNewKey=strId+'\n'+str(dictNL['label'])
#     graph.add_node(strNewKey,color='red')
#     lstChildren=dictNL['children']
#     for i in range(0,len(lstChildren)):
#         strChildKey=addNodeEdgeForNLPart(lstChildren[i],dictFatherLabel,graph,strId)
#         if strNewKey!=strChildKey:
#             graph.add_edge(strNewKey,strChildKey,color='red')
#             dictFatherLabel[strChildKey]=strNewKey
#
#     if 'dependencies' in dictNL.keys():
#         lstDeps=dictNL['dependencies']
#         for i in range(0,len(lstDeps)):
#             tup=lstDeps[i]
#             strSource=strId+'\n'+tup[3]
#             strTarget = strId + '\n' + tup[4]
#             if strSource!=strTarget:
#                 graph.add_edge(strSource,strTarget,color='green',label=tup[2])
#     return strNewKey

def copyGraphWithinLineIndex(graph,dictFatherLabel,startLineIndex,endLineIndex):
    newGraph=pgv.AGraph(directed=True)
    # nodes=graph.nodes()
    # edges=graph.edges()
    lstNodesStr=[]
    try:
        for node in graph.nodes_iter():
            # print(node)
            colorNode=node.attr['color']
            labelNode = str(node)
            tup=getLineAndOffsetFromLabel(labelNode)
            if tup[0]>=startLineIndex and tup[2]<=endLineIndex:
                newGraph.add_node(labelNode,color=colorNode)
                lstNodesStr.append(labelNode)
    except:
        isError=True

    try:
        for edge in graph.edges_iter():
            colorNode = edge.attr['color']
            labelNode = edge.attr['label']
            # print(edge.attr)
            sourceLbl = str(edge[0])
            targetLbl = str(edge[1])
            tupSource = getLineAndOffsetFromLabel(sourceLbl)
            tupTarget = getLineAndOffsetFromLabel(targetLbl)
            if tupSource[0] >= startLineIndex and tupSource[2] <= endLineIndex and tupTarget[0] >= startLineIndex and \
                    tupTarget[2] <= endLineIndex:
                newGraph.add_edge(sourceLbl, targetLbl, label=labelNode, color=colorNode)
    except:
        # traceback.print_exc()
        isError=True


    try:
        # print('dict nodeFather: {}\nlist: {}'.format(dictFatherLabel,lstNodesStr))
        setNodeStr=set(lstNodesStr)
        for node in lstNodesStr:
            # print(type(node))
            # print(node)
            nodeIter=node
            # and (str(dictFatherLabel[nodeIter]) not in setNodeStr
            indexGo=0
            while ((nodeIter in dictFatherLabel.keys() )and (not str(dictFatherLabel[nodeIter])in setNodeStr)):
                indexGo=indexGo+1
                nodeChild=nodeIter
                nodeIter=dictFatherLabel[nodeIter]
                # print('father {} and child {}'.format(nodeIter,nodeChild))
                # setNodeStr.add(nodeIter)
                newGraph.add_node(nodeIter,color='blue')
                newGraph.add_edge(nodeIter,nodeChild,color='blue')
            # if indexGo>0:
            # print('{}'.format(dictFatherLabel.keys()))
            # print('abel {} has {} fathers and a real father {}'.format(node.replace('\n',' ENDLINE '),indexGo,dictFatherLabel[node].replace('\n',' ENDLINE ')))

    except:
        isError=True
        traceback.print_exc()

    return newGraph

def getDotGraph(dictJson,dictLabel,dictFatherLabel,graph):
    strType=str(dictJson['type'])
    strId=getPrefixId(dictJson['startLine'],dictJson['startOffset'],dictJson['endLine'],dictJson['endOffset'])
    strLabel=strId+'\n'+strType
    # endPoint=int(str(dictJson['end_point']).split(',')[0].replace('(',''))
    # if endPoint<33:
    #     return 'include_label'
    if strLabel not in dictLabel.keys():
        graph.add_node(strLabel, color='blue')
        dictLabel[strLabel]=1
    if 'children' in dictJson.keys():
        lstChildren=dictJson['children']
        for i in range(0,len(lstChildren)):
            strChildLabel=getDotGraph(lstChildren[i],dictLabel,dictFatherLabel,graph)
            # if strChildLabel!='include_label':
                # if strChildLabel not in dictLabel.keys():
                #     graph.add_node(strChildLabel,color='blue')
                #     dictLabel[strChildLabel] = 1
            if strLabel!=strChildLabel:
                graph.add_edge(strLabel,strChildLabel,color='blue')
            # if strChildLabel=='33--0--33--3\nprimitive_type':
            #     print('add father to this label {}'.format(strChildLabel.replace('\n',' ENDLINE ')))
                dictFatherLabel[strChildLabel]=strLabel
            # if strChildLabel == '33--0--33--3\nprimitive_type':
            #     print('get value {}'.format(dictFatherLabel[strChildLabel.replace('\n',' ENDLINE ')]))
    # if 'nlGraph' in dictJson.keys():
    #     dictNL=dictJson['nlGraph']
    #     strNLID=addNodeEdgeForNLPart(dictNL,dictFatherLabel, graph,strId)
    #     if strLabel!=strNLID:
    #         graph.add_edge(strLabel, strNLID, color='red')
    #         dictFatherLabel[strNLID] = strLabel
    return strLabel

def getJsonDict(fpCPP,fpDotGraphAllText,fpDotGraphAllImage,fpDotGraphSimplifyText,fpDotGraphSimplifyImage,parser,nlpObj,offsetContext,isSaveGraph):
    dictJson=None
    g=None
    try:
        f1 = open(fpCPP, 'r')
        strCode = f1.read()
        arrCodes=strCode.split('\n')
        f1.close()
        tree=parser.parse(bytes(strCode, 'utf8'))
        cursor = tree.walk()
        node = cursor.node

        indexComment=-1
        for i in range(0,len(arrCodes)):
            strItem=arrCodes[i].strip()
            if strItem.startswith('//'):
                indexComment=i
                break
        # print('a comment here {}'.format(arrCodes[indexComment]))
        startIndex=indexComment-offsetContext
        endIndex=indexComment+offsetContext

        lstIds=[]
        dictJson=walkTreeAndReturnJSonObject(node,arrCodes,lstIds,nlpObj)

        if isSaveGraph:
            graph = pgv.AGraph(directed=True)
            dictLabel = {}
            dictFatherLabel={}
            getDotGraph(dictJson, dictLabel,dictFatherLabel, graph)
            graph.write(fpDotGraphAllText)
            graph.layout(prog='dot')
            graph.draw(fpDotGraphAllImage)
            # print('draw graph here {}'.format(fpDotGraphAllImage))

            startLine = indexComment - offsetContext
            endLine = indexComment + offsetContext
            simpleGraph = copyGraphWithinLineIndex(graph,dictFatherLabel, startLine, endLine)
            simpleGraph.write(fpDotGraphSimplifyText)
            simpleGraph.layout(prog='dot')
            simpleGraph.draw(fpDotGraphSimplifyImage)
    except:
        dictJson=None
        traceback.print_exc()
    return dictJson

def walkTreeAndReturnJSonObject(node,arrCodes,listId,nlpObj):
    dictJson={}
    strType=str(node.type)
    dictJson['type']=strType
    dictJson['id'] = len(listId)+1
    listId.append(len(listId)+1)
    strStart=str(node.start_point)
    strEnd = str(node.end_point)
    arrStart = strStart.split(',')
    arrEnd = strEnd.split(',')
    startLine = int(arrStart[0].replace('(', ''))
    startOffset = int(arrStart[1].replace(')', ''))
    endLine = int(arrEnd[0].replace('(', ''))
    endOffset = int(arrEnd[1].replace(')', ''))
    dictJson['startLine']=startLine
    dictJson['startOffset'] = startOffset
    dictJson['endLine'] = endLine
    dictJson['endOffset'] = endOffset

    # if strType!='translation_unit' and endLine<33:
    #     return dictJson
    listChildren=node.children

    if listChildren is not None and len(listChildren)>0:
        dictJson['children'] = []
        for i in range(0,len(listChildren)):

            arrChildEnd = str(listChildren[i].end_point).split(',')
            endChildLine = int(arrChildEnd[0].replace('(', ''))
            if endChildLine>=33:
                childNode = walkTreeAndReturnJSonObject(listChildren[i], arrCodes, listId,nlpObj)
                dictJson['children'].append(childNode)
    # elif len(dictJson['type'])>3:
    #     dictJson['children'] = []
    #     strTerminal = getTerminalValue(startLine, startOffset, endLine, endOffset, arrCodes)
    #     dictChild={}
    #     dictChild['id'] = len(listId) + 1
    #     listId.append(len(listId) + 1)
    #     dictChild['type']=strTerminal
    #     dictChild['startLine'] = startLine
    #     dictChild['startOffset'] = startOffset
    #     dictChild['endLine'] = endLine
    #     dictChild['endOffset'] = endOffset
    #     dictJson['children'].append(dictChild)

    # if dictJson['type'] == 'comment':
    #     # dictChild['isComment'] = True
    #     strTextComment = dictJson['children'][0]['type'].replace('//','').strip()
    #     jsonComment = getGraphDependencyFromText(strTextComment, nlpObj)
    #     # print('go to comment here {} aaa {}'.format(jsonComment,strTextComment))
    #
    #     if jsonComment is not None:
    #         # print('comment {}'.format(jsonComment))
    #         dictJson['children'][0]['nlGraph'] = jsonComment

    return dictJson

# def walkAndGetPOSJSon(dataParseResult,indexSentence,lstNonTerminals,lstTerminals):
#   dictJson={}
#   if str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==2:
#     # print( str(type(dataParseResult[0])))
#     if str(type(dataParseResult[0]))==strStrType:
#       if  str(type(dataParseResult[1]))==strStrType:
#         # print('ok1')
#         dictJson['tag']=str(dataParseResult[0])
#         dictJson['value'] = str(dataParseResult[1])
#         dictJson['isTerminal'] = True
#         dictJson['children'] = []
#
#         newId = len(lstTerminals) + 1
#         strValue=dictJson['value']
#         strTag=dictJson['tag']
#         strLabel ='Sent'+str(indexSentence) +'_Terminal'+str(newId)+'\n'+strTag + '\n' + strValue
#         lstTerminals.append(strLabel)
#         dictJson['label'] = strLabel
#       elif str(type(dataParseResult[1]))==strParseResultsType:
#         # print('ok 2')
#         dictJson['tag'] = str(dataParseResult[0])
#         dictJson['children']=[]
#         dictJson['children'].append( walkAndGetPOSJSon(dataParseResult[1],indexSentence,lstNonTerminals,lstTerminals))
#         dictJson['isTerminal'] = False
#         dictJson['value'] = ''
#         newId = len(lstNonTerminals) + 1
#         strTag = dictJson['tag']
#         strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
#         lstNonTerminals.append(strLabel)
#         dictJson['label'] = strLabel
#
#   elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)==1:
#     # print('go to branch here')
#     dictJson=walkAndGetPOSJSon(dataParseResult[0],indexSentence,lstNonTerminals,lstTerminals)
#   elif str(type(dataParseResult))==strParseResultsType and len(dataParseResult)>2:
#     if str(type(dataParseResult[0])) == strStrType:
#       strTag =str(dataParseResult[0])
#       dictJson['tag']=strTag
#       dictJson['value'] = ''
#       dictJson['isTerminal'] = False
#       dictJson['children'] = []
#       newId = len(lstNonTerminals) + 1
#       strLabel = 'Sent' + str(indexSentence) + '_NonTerminal' + str(newId) + '\n' + strTag
#       lstNonTerminals.append(strLabel)
#       dictJson['label'] = strLabel
#
#       for i in range(1,len(dataParseResult)):
#         dictChildI=walkAndGetPOSJSon(dataParseResult[i],indexSentence,lstNonTerminals,lstTerminals)
#         dictJson['children'].append(dictChildI)
#   return dictJson


# def getGraphDependencyFromText(strText,nlpObj):
#   lstDeps = []
#   lstNodes=[]
#   lstEdges=[]
#
#   try:
#     output = nlpObj.annotate(strText, properties={
#       'annotators': 'parse',
#       'outputFormat': 'json'
#     })
#     jsonTemp = output
#     # strJsonObj = jsonTemp
#     arrSentences=jsonTemp['sentences']
#     dictTotal={}
#     dictTotal['tag'] = 'Paragraph'
#     dictTotal['label'] = 'Paragraph'
#     dictTotal['value'] = ''
#     dictTotal['isTerminal'] = False
#     dictTotal['children'] = []
#     indexSentence=0
#     # print(strText)
#     for sentence in arrSentences:
#       jsonDependency = sentence['basicDependencies']
#       strParseContent=sentence['parse']
#       lstNonTerminals = []
#       lstTerminals = []
#       indexSentence=indexSentence+1
#       data = OneOrMore(nestedExpr()).parseString(strParseContent)
#       dictWords = {}
#       jsonPOS=walkAndGetPOSJSon(data,indexSentence,lstNonTerminals,lstTerminals)
#       # print('POS {}'.format(jsonPOS))
#
#       for dep in jsonDependency:
#         strDep=dep['dep']
#         if strDep=='ROOT':
#             continue
#         # print('dep : {}'.format(dep))
#         indexSource=dep['governor']
#         indexTarget=dep['dependent']
#         # print(source+' ss '+target)
#         # itemTuple=(dep['dep'],dep['governorGloss'],dep['dependentGloss'])
#         # lstDeps.append(itemTuple)
#         # if source not in dictWords:
#         #   dictWords[source]=len(dictWords.keys())+1
#         #   tupleNode=(dictWords[source],'pseudo_node',source)
#         #   lstNodes.append(tupleNode)
#         # if target not in dictWords:
#         #   dictWords[target]=len(dictWords.keys())+1
#         #   tupleNode=(dictWords[target],'pseudo_node',target)
#         #   lstNodes.append(tupleNode)
#         itemTuple=(indexSource,indexTarget,strDep,lstTerminals[indexSource-1],lstTerminals[indexTarget-1])
#         lstEdges.append(itemTuple)
#       jsonPOS['dependencies']=lstEdges
#       dictTotal['children'].append(jsonPOS)
#   except:
#     strJsonObj = 'Error'
#     dictTotal=None
#     traceback.print_exc()
#   return dictTotal



# fopData='/home/hungphd/'
# fopGithub='/home/hungphd/git/'
# fopBuildFolder=fopData+'build-tree-sitter/'
# fpLanguageSo=fopBuildFolder+'my-languages.so'
# fpDotGraphText=fopGithub+'dataPapers/temp.dot'
# fpDotGraphImg=fopGithub+'dataPapers/temp.png'
# fpSimpleDotGraphText=fopGithub+'dataPapers/temp_simplify.dot'
# fpSimpleDotGraphImg=fopGithub+'dataPapers/temp_simplify.png'
#
# CPP_LANGUAGE = Language(fpLanguageSo, 'cpp')
# fpTempCPPFile=fopGithub+'dataPapers/1_2A_42264131_v2.cpp'
#
# from pycorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP('http://localhost:9000')
#
# parser = Parser()
# parser.set_language(CPP_LANGUAGE)
#
# f1=open(fpTempCPPFile,'r')
# strCode=f1.read()
# arrCodes=strCode.split('\n')
# f1.close()
#
# tree= parser.parse(bytes(strCode,'utf8'))
# cursor = tree.walk()
# node=cursor.node
# print(type(tree))
# print(str(node))
# print(str(len(node.children)))
# # for property, value in vars(cursor).items():
# #     print(property, ":", value)
# # print(vars(tree))
# lstId=[]
# dictJson=walkTreeAndReturnJSonObject(node,arrCodes,lstId,nlp)
# print(str(dictJson))
# ind=1
# graph=pgv.AGraph(directed=True)
# dictLabel={}
# getDotGraph(dictJson,dictLabel,graph)
# graph.write(fpDotGraphText)
# graph.layout(prog='dot')
# graph.draw(fpDotGraphImg)
#
# offsetLine=3
# commentIndexLine=34
# startLine=commentIndexLine-offsetLine
# endLine=commentIndexLine+offsetLine
# simpleGraph=copyGraphWithinLineIndex(graph,startLine,endLine)
# simpleGraph.write(fpSimpleDotGraphText)
# simpleGraph.layout(prog='dot')
# simpleGraph.draw(fpSimpleDotGraphImg)


