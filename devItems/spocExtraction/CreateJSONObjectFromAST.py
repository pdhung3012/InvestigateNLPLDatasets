import glob
import sys, os
import operator
import clang.cindex
import json
import subprocess

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

fpTempAST= 'temp/code1_ast.txt'
fpTempCode= 'temp/code1.cpp'

def runASTGenAndSeeResult(fpTempCode,fpJSon,numOmit):
    stream = os.popen("clang++-11 -Xclang -ast-dump=json temp/code1.cpp -o temp/code1_ast.o | sed -n '/XX_MARKER_XX/,$p' > temp/code1_ast.txt")
    # "clang++ -ast-dump=json /Users/hungphan/git/dataPapers/textInSPOC/temp/code1.cpp -o /Users/hungphan/git/dataPapers/textInSPOC/temp/code1_ast.o | sed -n '/XX_MARKER_XX/,$p' > /Users/hungphan/git/dataPapers/textInSPOC/temp/code1_ast.txt"
    output=stream.read()
    print(output)
    f1=open(fpJSon,'r')
    strJson=f1.read().strip()
    f1.close()
    arrJson=strJson.split('\n')
    lstStr=[]
    lstStr.append('{\n\t"kind": "root",\n\t"inner": [')
    for i in range(numOmit,len(arrJson)):
        lstStr.append(arrJson[i])
    strResult='\n'.join(lstStr)
    # print(strResult)
    jsonObject = json.loads(strResult)
    return jsonObject


def fixJSonProblem(fpJSon,numOmit):
    f1=open(fpJSon,'r')
    strJson=f1.read().strip()
    f1.close()
    arrJson=strJson.split('\n')
    lstStr=[]
    lstStr.append('{\n\t"kind": "root",\n\t"inner": [')
    for i in range(numOmit,len(arrJson)):
        lstStr.append(arrJson[i])
    strResult='\n'.join(lstStr)
    # print(strResult)
    jsonObject = json.loads(strResult)
    return jsonObject

numOmit=30
jsonObject=runASTGenAndSeeResult(fpTempCode,fpTempAST, numOmit)
print('jsonObject {}'.format(jsonObject))

