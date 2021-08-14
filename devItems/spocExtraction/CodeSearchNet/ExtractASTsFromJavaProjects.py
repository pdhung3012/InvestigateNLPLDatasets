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


def walkJavaTreeAndReturnJSonObject(node,arrCodes,listId):
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
            # if endChildLine>=33:
            childNode = walkJavaTreeAndReturnJSonObject(listChildren[i], arrCodes, listId)
            dictJson['children'].append(childNode)
    elif len(dictJson['type'])>3:
        dictJson['children'] = []
        strTerminal = getTerminalValue(startLine, startOffset, endLine, endOffset, arrCodes)
        dictChild={}
        dictChild['id'] = len(listId) + 1
        listId.append(len(listId) + 1)
        dictChild['type']=strTerminal
        dictChild['startLine'] = startLine
        dictChild['startOffset'] = startOffset
        dictChild['endLine'] = endLine
        dictChild['endOffset'] = endOffset
        dictJson['children'].append(dictChild)

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
                if str(labelNode)!='None':
                    newGraph.add_edge(sourceLbl, targetLbl, label=labelNode, color=colorNode)
                else:
                    newGraph.add_edge(sourceLbl, targetLbl,  color=colorNode)
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

def getJsonDict(fpTempCPPFile,parser):
    dictJson=None
    arrCodes=None
    try:
        f1 = open(fpTempCPPFile, 'r')
        strCode = f1.read().strip()
        arrCodes = strCode.split('\n')
        f1.close()
        #
        tree = parser.parse(bytes(strCode, 'utf8'))
        cursor = tree.walk()
        node = cursor.node
        # print(type(tree))
        # print(str(node))
        # print(str(len(node.children)))
        # for property, value in vars(cursor).items():
        #     print(property, ":", value)
        # print(vars(tree))
        lstId = []
        dictJson = walkJavaTreeAndReturnJSonObject(node, arrCodes, lstId)
        # print(str(dictJson))
    except:
        traceback.print_exc()
    return dictJson,arrCodes

fopData='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopData+'build-tree-sitter/'
fpLanguageSo=fopBuildFolder+'my-languages.so'
fpDotGraphText=fopGithub+'dataPapers/temp_java.dot'
fpDotGraphImg=fopGithub+'dataPapers/temp_java.png'
fpSimpleDotGraphText=fopGithub+'dataPapers/temp_java_simplify.dot'
fpSimpleDotGraphImg=fopGithub+'dataPapers/temp_java_simplify.png'

# JAVA_LANGUAGE = Language(fpLanguageSo, 'java')
# fpTempCPPFile=fopGithub+'dataPapers/ScaledOut.java'
# parser = Parser()
# parser.set_language(JAVA_LANGUAGE)
# #
# f1=open(fpTempCPPFile,'r')
# strCode=f1.read()
# arrCodes=strCode.split('\n')
# f1.close()
# #
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
# dictJson=walkJavaTreeAndReturnJSonObject(node,arrCodes,lstId)
# print(str(dictJson))
#
# ind=1
# graph=pgv.AGraph(directed=True)
# dictLabel={}
# dictFatherLabel={}
# getDotGraph(dictJson,dictLabel,dictFatherLabel,graph)
# graph.write(fpDotGraphText)
# graph.layout(prog='dot')
# graph.draw(fpDotGraphImg)
#
# offsetLine=3
# commentIndexLine=49
# startLine=commentIndexLine-offsetLine
# endLine=commentIndexLine+offsetLine
# simpleGraph=copyGraphWithinLineIndex(graph,dictFatherLabel,startLine,endLine)
# simpleGraph.write(fpSimpleDotGraphText)
# simpleGraph.layout(prog='dot')
# simpleGraph.draw(fpSimpleDotGraphImg)


