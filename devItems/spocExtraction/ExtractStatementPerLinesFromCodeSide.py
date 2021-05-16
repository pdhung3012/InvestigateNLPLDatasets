import glob
import sys, os
import operator
import clang.cindex
import json

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

def traverseJsonObject(jsonObject,dictLines):
    beginLine=-1
    endLine=-1
    try:
        beginLine=jsonObject['loc']['line']
    except :
        beginLine=-1
    if( beginLine ==-1):
        try:
            beginLine=jsonObject['range']['begin']['line']
        except :
            beginLine=-1
    try:
        endLine=jsonObject['range']['end']['line']
    except :
        endLine=-1
    if beginLine>0:
        # strName=jsonObject['na']
        strKind=jsonObject['kind']
        # print(strKind)
        # beginLine=jsonObject['loc']['line']
        strKey = '{}'.format(beginLine)
        if(endLine>0):
            strKey='{}-{}'.format(beginLine,endLine)
        if strKey not in dictLines:
            lstItem=[]
            lstItem.append(strKind)
            dictLines[strKey]=lstItem
        else:
            dictLines[strKey].append(strKind)
    if 'inner' in jsonObject:
        arr=jsonObject['inner']
        for item in arr:
            traverseJsonObject(item,dictLines)



def extractStatementLineAlignment(fopCombineASTs,fpStatementLine):
    currentKey=''
    dictASTs={}
    lstFiles=sorted(glob.glob(fopCombineASTs+ "*_code.cpp"))
    f1=open(fpStatementLine, 'w')
    f1.write('')
    f1.close()

    for i in range(0,len(lstFiles)):
        fpItem=lstFiles[i]
        fileNameItem=os.path.basename(lstFiles[i])
        f1=open(fpItem,'r')
        strJson=f1.read()
        f1.close()
        jsonObject = json.loads(strJson)
        # print(str(jsonObject))
        dictLines={}
        traverseJsonObject(jsonObject,dictLines)
        lstStr=[fileNameItem]
        print('{}\t{}\t{}'.format(i,fpItem,len(dictLines.keys())))
        for key in sorted(dictLines.keys()):
            lstItem=dictLines[key]
            strItem='{}\t{}'.format(key,','.join(lstItem))
            lstStr.append(strItem)
        lstStr.append('\n\n\n')
        f1 = open(fpStatementLine, 'a')
        f1.write('\n'.join(lstStr))
        f1.close()

    print('finish')

fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopCombineASTs= fopTextInSPoC + 'trainASTForC/'
fpStatementLine= fopTextInSPoC + 'statementLabelFromCode.txt'
fopCombineASTsTestP= fopTextInSPoC + 'testPASTForC/'
fpStatementLineTestP= fopTextInSPoC + 'statementLabelFromCode_TestP.txt'
fopCombineASTsTestW= fopTextInSPoC + 'testWASTForC/'
fpStatementLineTestW= fopTextInSPoC + 'statementLabelFromCode_TestW.txt'

extractStatementLineAlignment(fopCombineASTs,fpStatementLine)
extractStatementLineAlignment(fopCombineASTsTestP,fpStatementLineTestP)
extractStatementLineAlignment(fopCombineASTsTestW,fpStatementLineTestW)






