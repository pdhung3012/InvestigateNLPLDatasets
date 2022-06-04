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
from Util_LibForGraphExtractionFromRawCode import *

fopStanfordCoreNLP='../../../dataPapers/stanford-corenlp-4.2.2/'

strParseResultsType="<class 'pyparsing.ParseResults'>"
strStrType="<class 'str'>"


fopData='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopData+'build-tree-sitter/'
fpLanguageSo=fopBuildFolder+'my-languages.so'
fpDotGraphText=fopGithub+'dataPapers/temp.dot'
fpDotGraphImg=fopGithub+'dataPapers/temp.png'
fpSimpleDotGraphText=fopGithub+'dataPapers/temp_simplify.dot'
fpSimpleDotGraphImg=fopGithub+'dataPapers/temp_simplify.png'

CPP_LANGUAGE = Language(fpLanguageSo, 'cpp')
fpTempCPPFile='/home/hungphd/Downloads/motivationExample/codeWithComment.cpp'
fpOutput1='/home/hungphd/Downloads/motivationExample/output1.json.txt'
fpTempCPPFile='/home/hungphd/Downloads/motivationExample/codeRaw.cpp'
fpOutput1='/home/hungphd/Downloads/motivationExample/outputRaw.json.txt'

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

parser = Parser()
parser.set_language(CPP_LANGUAGE)

f1=open(fpTempCPPFile,'r')
strCode=f1.read()
arrCodes=strCode.split('\n')
f1.close()

lstId=[]
tree= parser.parse(bytes(strCode,'utf8'))
cursor = tree.walk()
node=cursor.node
dictJson=walkTreeAndReturnJSonObject(node,arrCodes,lstId,nlp)
f1=open(fpOutput1,'w')
f1.write(str(dictJson))
f1.close()


