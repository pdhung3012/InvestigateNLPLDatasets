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
import  gzip,json
import ast
from shutil import copyfile




fopLocalDataPapers='../../../../dataPapers/'
fopExternalDataPapers='/home/hungphd/media/dataPapersExternal/'
fopDataCSN=fopExternalDataPapers+'data_CSN/'
fopExtractedJson=fopExternalDataPapers+'extractedJson_CSN/'
fopCSContent='/home/hungphd/media/dataPapersExternal/textCorpus/cs/'

lstFiles=glob.glob(fopExtractedJson+'/**/*_comment.txt',recursive=True)
index=0
for i in range(0,len(lstFiles)):
    fpItem=lstFiles[i]
    index=index+1
    fpOutItem=fopCSContent+str(index)+'.txt'
    try:
        copyfile(fpItem, fpOutItem)
    except:
        traceback.print_exc()
