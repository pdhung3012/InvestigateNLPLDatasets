import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import pygraphviz as pgv
import pylab

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


def getDotGraph(dictJson,dictLabel,graph):
    strType=str(dictJson['type'])
    ind=int(dictJson['id'])
    strLabel=str(ind)+'__'+dictJson['type']
    # endPoint=int(str(dictJson['end_point']).split(',')[0].replace('(',''))
    # if endPoint<33:
    #     return 'include_label'
    if strLabel not in dictLabel.keys():
        graph.add_node(strLabel, color='blue')
        dictLabel[strLabel]=1
    if 'children' in dictJson.keys():
        lstChildren=dictJson['children']
        for i in range(0,len(lstChildren)):
            strChildLabel=getDotGraph(lstChildren[i],dictLabel,graph)
            # if strChildLabel!='include_label':
                # if strChildLabel not in dictLabel.keys():
                #     graph.add_node(strChildLabel,color='blue')
                #     dictLabel[strChildLabel] = 1
            graph.add_edge(strLabel,strChildLabel,color='blue')

    return strLabel

def getJsonDict(fpCPP,fpDotGraphText,fpDotGraphImage,parser):
    dictJson=None
    g=None
    try:
        f1 = open(fpCPP, 'r')
        strCode = f1.read()
        f1.close()
        parser.parse(bytes(strCode, 'utf8'))
        cursor = tree.walk()
        node = cursor.node
        id=1
        dictJson=walkTreeAndReturnJSonObject(node,id)
        ind=1
        graph=pgv.AGraph()
        getDotGraph(dictJson,ind,graph)
        graph.render(filename=fpDotGraphText)
        pylab.savefig(fpDotGraphImage)
    except:
        dictJson=None
    return dictJson

def walkTreeAndReturnJSonObject(node,arrCodes,listId):
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
                childNode = walkTreeAndReturnJSonObject(listChildren[i], arrCodes, listId)
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


    return dictJson

fopData='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopData+'build-tree-sitter/'
fpLanguageSo=fopBuildFolder+'my-languages.so'
fpDotGraphText=fopGithub+'dataPapers/temp.dot'
fpDotGraphImg=fopGithub+'dataPapers/temp.png'
CPP_LANGUAGE = Language(fpLanguageSo, 'cpp')
fpTempCPPFile=fopGithub+'dataPapers/1_2A_42264131_v2.cpp'

parser = Parser()
parser.set_language(CPP_LANGUAGE)

f1=open(fpTempCPPFile,'r')
strCode=f1.read()
arrCodes=strCode.split('\n')
f1.close()

tree= parser.parse(bytes(strCode,'utf8'))
cursor = tree.walk()
node=cursor.node
print(type(tree))
print(str(node))
print(str(len(node.children)))
# for property, value in vars(cursor).items():
#     print(property, ":", value)
# print(vars(tree))
lstId=[]
dictJson=walkTreeAndReturnJSonObject(node,arrCodes,lstId)
print(str(dictJson))
ind=1
graph=pgv.AGraph(directed=True)
dictLabel={}
getDotGraph(dictJson,dictLabel,graph)
graph.write(fpDotGraphText)
graph.layout(prog='dot')
graph.draw(fpDotGraphImg)
