import glob
import sys, os
import operator
import clang.cindex
import json

sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

def findAllFuncDecl(jsonObject):
    arrObj=jsonObject["inner"]
    lstResults=[]
    for item in arrObj:
        if item["kind"]=='FunctionDecl':
            lstResults.append(item)
    return lstResults

fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopCombineASTs= fopTextInSPoC + 'trainASTForC/'
fpSignatures= fopTextInSPoC + 'signatureFromCode.txt'

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
f1=open(fpSignatures, 'w')
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
    lstFuncDecl=findAllFuncDecl(jsonObject)
    if(len(lstFuncDecl)>0):
        lstStr=[]
        print('{}\t{}'.format(i, fpItem))
        for item in lstFuncDecl:
            name=item["name"]
            print(name)
            lineBegin=item["loc"]["line"]
            lineEnd=lineBegin
            if 'line' in item["range"]["end"]:
                lineEnd = item["range"]["end"]["line"]
            lstStr.append('{}\t{}\t{}'.format(name,lineBegin,lineEnd))
        strAddToFile='\n'.join(lstStr)
        strAddTotal='\n'.join([fileNameItem,strAddToFile,'\n\n\n'])
        f1=open(fpSignatures,'a')
        f1.write(strAddTotal)
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







