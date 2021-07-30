import glob
import json
import sys, os
import operator,traceback
import shutil
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import glob
import ast

def lookUpJSonObjectWithLine(dictJson,lineNumber):
    if dictJson['startLine']==lineNumber:
        strType=dictJson['type']
        strOffset= dictJson['endLine']- dictJson['startLine']+1
        return strType,strOffset,True
    elif 'children' in dictJson.keys():
        lstChildren=dictJson['children']
        for child in lstChildren:
            strType,strOffset,isFound=lookUpJSonObjectWithLine(child,lineNumber)
            if isFound:
                return strType,strOffset,isFound
    return 'NONE','NONE',False



def generateLabelsForMixCodeFromCorrectCode(fopMixCodeStep2,fopCorrectCodeCPP,fopCorrectCodeJson,fpLabel):
    createDirIfNotExist(fopMixCodeStep2)
    createDirIfNotExist(fopCorrectCodeCPP)
    createDirIfNotExist(fopCorrectCodeJson)
    lstMixCodeStep2Files=glob.glob(fopMixCodeStep2+'*.cpp')
    print(fopMixCodeStep2)
    f1=open(fpLabel,'w')
    f1.write('')
    f1.close()
    for fpMixCodeCpp in lstMixCodeStep2Files:
        nameOfMixVersion=os.path.basename(fpMixCodeCpp).replace('.cpp','')
        nameOfCpp = nameOfMixVersion.split('_v')[0]
        nameOfCode=nameOfCpp+'_code.cpp'
        nameOfASTCorrectVerion=nameOfCpp+'_code_ast.txt'
        fpJSonASTCorrectVersion=fopCorrectCodeJson+nameOfASTCorrectVerion
        fpCorrectCode=fopCorrectCodeCPP+nameOfCode
        # print(nameOfMixVersion)
        try:
            f1=open(fpMixCodeCpp,'r')
            strMixCode=f1.read()
            arrMixCode=strMixCode.split('\n')
            f1.close()

            f1 = open(fpJSonASTCorrectVersion, 'r')
            strJSonCorrect = f1.read().split('\n')[1].strip()
            # print('json here: {}'.format(strJSonCorrect))

            f1.close()

            indexComment=-1
            for i in range(0,len(arrMixCode)):
                strTrim=arrMixCode[i].strip()
                if strTrim.startswith('//'):
                    indexComment=i
                    break
            jsonOfCorrectVersion=ast.literal_eval(strJSonCorrect)
            strType, strOffset, isFound=lookUpJSonObjectWithLine(jsonOfCorrectVersion,indexComment)
            if isFound:
                strAppend='{}\t{}\t{}\t{}\n'.format(nameOfMixVersion,(indexComment+1),strType,strOffset)
                f1=open(fpLabel,'a')
                f1.write(strAppend)
                f1.close()

        except:
            traceback.print_exc()
            strAppend = '{}\t{}\t{}\t{}\n'.format(nameOfMixVersion,(indexComment+1), 'UNK', 'UNK')
            f1 = open(fpLabel, 'a')
            f1.write(strAppend)
            f1.close()







fopRoot='../../../../dataPapers/textInSPOC/'
fopRootCorrectCodeJson=fopRoot+'correctCodeJson/step3_treesitter/'
fopRootCorrectCodeCPP=fopRoot+'correctCodeJson/step2/'
fopRootMixCodeStep2=fopRoot+'mixCodeJson/step2/'
fopRootMixCodeStep5=fopRoot+'mixCodeJson/step5/'
createDirIfNotExist(fopRootMixCodeStep5)
fopRootCPPCode=fopRoot+'CppCode/'
lstFolderNames=['testW','testP','train']
lstRootCorrectCodeJson=[]
lstRootCorrectCodeCPP=[]
lstRootMixCode=[]
lstRootCPPCode=[]
lstFpRootMixCodeStep5=[]
for name in lstFolderNames:
    lstRootCorrectCodeJson.append(fopRootCorrectCodeJson+name+'/')
    lstRootCorrectCodeCPP.append(fopRootCorrectCodeCPP+name+'/')
    lstRootMixCode.append(fopRootMixCodeStep2+name+'/')
    lstRootCPPCode.append(fopRootCPPCode+name+'/')
    lstFpRootMixCodeStep5.append(fopRootMixCodeStep5+name+'_label.txt')

for i in range(0,3):
    generateLabelsForMixCodeFromCorrectCode(lstRootMixCode[i], lstRootCorrectCodeCPP[i], lstRootCorrectCodeJson[i], lstFpRootMixCodeStep5[i])








