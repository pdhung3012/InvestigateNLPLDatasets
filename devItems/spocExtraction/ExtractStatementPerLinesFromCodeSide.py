import glob
import sys, os
import operator
import clang.cindex
import json

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

def traverseJsonObject(jsonObject,dictLines):
    if 'loc' in jsonObject and 'line' in jsonObject['loc']:
        # strName=jsonObject['na']
        strKind=jsonObject['kind']
        # print(strKind)
        beginLine=jsonObject['loc']['line']
        if beginLine not in dictLines:
            lstItem=[]
            lstItem.append(strKind)
            dictLines[beginLine]=lstItem
        else:
            dictLines[beginLine].append(strKind)
    if 'inner' in jsonObject:
        arr=jsonObject['inner']
        for item in arr:
            traverseJsonObject(item,dictLines)



fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopCombineASTs= fopTextInSPoC + 'trainASTForC/'
fpStatementLine= fopTextInSPoC + 'statementLabelFromCode.txt'

# lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.cpp"))

dictCountWords={}

# f1=open(fpCombineASTs, 'r')
# strCombineASTs=f1.read()
# f1.close()
currentKey=''
dictASTs={}
# arrCombineASTs=strCombineASTs.split('\n')
# for i in range(0,len(arrCombineASTs)):
#     strTrim=arrCombineASTs[i].strip()
#     if strTrim.endswith('.cpp'):
#         currentKey=strTrim
#         listASTs=[]
#         dictASTs[currentKey]=listASTs
#         # print(currentKey)
#     else:
#         dictASTs[currentKey].append(arrCombineASTs[i])
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











# print('finish listASTs {}'.format(len(dictASTs.keys())))


# for key in dictASTs.keys():
#     lstItemASTs=dictASTs[key]
#     lstOutputItem = []
#     for i in range(0,len(lstItemASTs)):
#         strItem=lstItemASTs[i].strip()
#         arrItem=strItem.split('\t')
#         # print(strItem)
#         if len(arrItem)>=3 and arrItem[1] == 'CursorKind.FUNCTION_DECL':
#             strFuncInfo='{}\t{}'.format(arrItem[2],arrItem[0])
#             lstOutputItem.append(strFuncInfo)
#
#
#     strContentToAdd='\n'.join(lstOutputItem)
#     strContentItem='\n'.join([key,strContentToAdd,'\n\n\n'])
#     f1 = open(fpSignatures, 'a')
#     f1.write(strContentItem)
#     f1.close()
#
# print('finish')







