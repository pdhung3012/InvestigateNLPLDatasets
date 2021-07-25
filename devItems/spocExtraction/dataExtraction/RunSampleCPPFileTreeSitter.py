import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser

def getJsonDict(fpCPP,parser):
    dictJson=None
    try:
        f1 = open(fpCPP, 'r')
        strCode = f1.read()
        f1.close()
        parser.parse(bytes(strCode, 'utf8'))
        cursor = tree.walk()
        node = cursor.node
        dictJson=walkTreeAndReturnJSonObject(node)
    except:
        dictJson=None
    return dictJson

def walkTreeAndReturnJSonObject(node):
    dictJson={}
    dictJson['type']=str(node.type)
    dictJson['start_point']=str(node.start_point)
    dictJson['end_point'] = str(node.end_point)
    listChildren=node.children

    if listChildren is not None and len(listChildren)>0:
        dictJson['children'] = []
        for i in range(0,len(listChildren)):
            childNode=walkTreeAndReturnJSonObject(listChildren[i])
            dictJson['children'].append(childNode)
    return dictJson

fopData='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopData+'build-tree-sitter/'
fpLanguageSo=fopBuildFolder+'my-languages.so'

CPP_LANGUAGE = Language(fpLanguageSo, 'cpp')
fpTempCPPFile='/home/hungphd/git/dataPapers/textInSPOC/mix_step2_v2/testP/1_2A_42264131_v2.cpp'

parser = Parser()
parser.set_language(CPP_LANGUAGE)

f1=open(fpTempCPPFile,'r')
strCode=f1.read()
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

dictJson=walkTreeAndReturnJSonObject(node)
print(str(dictJson))
