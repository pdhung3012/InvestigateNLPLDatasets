import glob
import sys, os
import operator
import clang.cindex
import json

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText


strConstError='Error_Val'
strConstSplitWord=' ABA '
def getJsonValueCatchError(jsonObj,listKeys):
    strValue='Error_Val'
    try:
        obj=jsonObj
        for item in listKeys:
            obj=obj[item]
        strValue=obj
    except:
        strValue = 'Error_Val'
        print('error here')
    return strValue

def traverseJsonObjectAndKeepTrackVariablesAndLiterals(jsonObject,lstVars,splitWord):
    if 'kind' in jsonObject:
        strKind=jsonObject['kind']
        if jsonObject['kind']=='VarDecl':
            strName=getJsonValueCatchError(jsonObject,['name'])
            strType = getJsonValueCatchError(jsonObject, ['type','qualType'])
            if strName!=strConstError and strType!=strConstError:
                strItem='{}{}{}{}{}'.format(strName,splitWord,strKind,splitWord,strType)
                lstVars.append(strItem)
        # elif jsonObject['kind']=='referencedDecl':
        #     strName=getJsonValueCatchError(jsonObject,['name'])
        #     strType = getJsonValueCatchError(jsonObject, ['type','qualType'])
        #     if strName!=strConstError and strType!=strConstError:
        #         strItem='{}{}{}{}{}'.format(strName,splitWord,strKind,splitWord,strType)
        #         lstVars.append(strItem)
        elif jsonObject['kind'].endswith('Literal'):
            strName=getJsonValueCatchError(jsonObject,['value'])
            strType = getJsonValueCatchError(jsonObject, ['type','qualType'])
            if jsonObject['kind']=='CharacterLiteral':
                intName=int(strName)
                strName=repr(chr(intName))
                # if strName =='\0':
                #     strName='\\0'
            if strName!=strConstError and strType!=strConstError:
                strItem='{}{}{}{}{}'.format(strName,splitWord,strKind,splitWord,strType)
                lstVars.append(strItem)



    if 'inner' in jsonObject:
        arr=jsonObject['inner']
        for item in arr:
            traverseJsonObjectAndKeepTrackVariablesAndLiterals(item,lstVars,splitWord)



def extractParamInfo(fopCombineASTs, fpParamInfo,splitWord):
    currentKey=''
    dictASTs={}
    lstFiles=sorted(glob.glob(fopCombineASTs+ "*_code.cpp"))
    f1=open(fpParamInfo, 'w')
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
        lstVars=[]
        traverseJsonObjectAndKeepTrackVariablesAndLiterals(jsonObject,lstVars,splitWord)
        lstVars=set(lstVars)
        lstStr=[fileNameItem]
        print('{}\t{}\t{}'.format(i,fpItem,len(lstVars)))
        for key in lstVars:
            strItem='{}'.format(key)
            lstStr.append(strItem)
        lstStr.append('\n\n\n')
        f1 = open(fpParamInfo, 'a')
        f1.write('\n'.join(lstStr))
        f1.close()

    print('finish')

fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopCombineASTs= fopTextInSPoC + 'trainASTForC/'
fpParamInfo= fopTextInSPoC + 'paramInfoFromCode.txt'
fopCombineASTsTestP= fopTextInSPoC + 'testPASTForC/'
fpParamInfoTestP= fopTextInSPoC + 'paramInfoFromCode_TestP.txt'
fopCombineASTsTestW= fopTextInSPoC + 'testWASTForC/'
fpParamInfoTestW= fopTextInSPoC + 'paramInfoFromCode_TestW.txt'

extractParamInfo(fopCombineASTs, fpParamInfo,strConstSplitWord)
extractParamInfo(fopCombineASTsTestP, fpParamInfoTestP,strConstSplitWord)
extractParamInfo(fopCombineASTsTestW, fpParamInfoTestW,strConstSplitWord)






