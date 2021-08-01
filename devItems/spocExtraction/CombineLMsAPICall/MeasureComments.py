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
from ExtractASTsFromJavaProjects import getTerminalValue,getPrefixId

def lookUpCommentsInJsonObject(dictJson,lstComments,dictImports,arrCodes):
    if dictJson['type']=='comment':
        startLine=dictJson['startLine']
        startOffset=dictJson['startOffset']
        endLine=dictJson['endLine']
        endOffset=dictJson['endOffset']
        strTerminal = getTerminalValue(startLine, startOffset, endLine, endOffset, arrCodes)
        tup=(getPrefixId(startLine,startOffset,endLine,endOffset),strTerminal)
        lstComments.append(tup)
    elif dictJson['type']=='import_declaration':
        startLine=dictJson['startLine']
        startOffset=dictJson['startOffset']
        endLine=dictJson['endLine']
        endOffset=dictJson['endOffset']
        strTerminal = getTerminalValue(startLine, startOffset, endLine, endOffset, arrCodes)
        strImport=strTerminal.replace('import','').replace(';','').strip().replace('.','_DOT_').replace('*','_STAR_')
        # tup=(getPrefixId(startLine,startOffset,endLine,endOffset),strTerminal)
        # lstComments.append(tup)
        if strImport not in dictJson.keys():
            dictImports[strImport]=1
        else:
            dictImports[strImport]=dictImports[strImport]+1
    elif 'children' in dictJson.keys():
        lstChildren=dictJson['children']
        for child in lstChildren:
            lookUpCommentsInJsonObject(child,lstComments,dictImports,arrCodes)

def statisticComment(fopInputJson,fopComment,fpLogComment,fopImport):
    createDirIfNotExist(fopInputJson)
    createDirIfNotExist(fopComment)
    createDirIfNotExist(fopImport)
    lstProjectNames = glob.glob(fopInputJson + '*/')

    f1 = open(fpLogComment, 'w')
    f1.write('')
    f1.close()

    for i in range(0, len(lstProjectNames)):
        try:
            fopProjectItem = lstProjectNames[i]
            arrFopItem = fopProjectItem.split('/')
            projectFolderName = arrFopItem[len(arrFopItem) - 2]
            lstFpASTInfos=glob.glob(fopProjectItem+'*.txt')
            fpDictFileJavaLocation =fopInputJson+projectFolderName+'.txt'
            dictKeyAndJavaFiles={}
            f1=open(fpDictFileJavaLocation,'r')
            arrDictJavas=f1.read().strip().split('\n')
            f1.close()

            for item in arrDictJavas:
                arrItem=item.strip().split('\t')
                if (len(arrItem)>=2):
                    dictKeyAndJavaFiles[arrItem[0]]=arrItem[1]
            numRunOK = 0
            print('begin {} {} {}'.format(i,projectFolderName,len(lstFpASTInfos)))
            dictKeyAndImport={}
            for j in range(0,len(lstFpASTInfos)):
                try:
                    fpItemASTInfo = lstFpASTInfos[j]
                    itemNameAST = os.path.basename(fpItemASTInfo).replace('_ast.txt', '_comment.txt')
                    strKeyAST = os.path.basename(fpItemASTInfo).replace('_ast.txt', '')
                    fpItemLogComment=fopComment+itemNameAST
                    fpJavaFile=dictKeyAndJavaFiles[strKeyAST]
                    f1=open(fpJavaFile,'r')
                    arrCodes=f1.read().strip().split('\n')
                    f1.close()
                    f1=open(fpItemASTInfo,'r')
                    strJson=f1.read().strip()
                    f1.close()
                    jsonObject = ast.literal_eval(strJson)
                    lstComments =[]
                    lookUpCommentsInJsonObject(jsonObject,lstComments,dictKeyAndImport,arrCodes)
                    lstStrComments=[]
                    for item in lstComments:
                        # print('comment {}'.format(item))
                        lstStrComments.append('{}\t{}'.format(item[0],item[1].replace('\t',' TABCHAR ').replace('\n',' ENDLINE ')))
                    f1=open(fpItemLogComment,'w')
                    f1.write('\n'.join(lstStrComments))
                    f1.close()
                    numRunOK=numRunOK+len(lstComments)
                except:
                    traceback.print_exc()
            for keyImport in dictKeyAndImport.keys():
                fpItemImport = fopImport + keyImport+'.txt'
                if not os.path.exists(fpItemImport):
                    f1=open(fpItemImport,'w')
                    f1.write('{}\t{}\n'.format(projectFolderName,dictKeyAndImport[keyImport]))
                    f1.close()
                else:
                    f1 = open(fpItemImport, 'a')
                    f1.write('{}\t{}\n'.format(projectFolderName, dictKeyAndImport[keyImport]))
                    f1.close()
            f1 = open(fpLogComment, 'a')
            f1.write('{}\t{}\t{}\n'.format(projectFolderName,numRunOK,len(lstFpASTInfos)))
            f1.close()
            print('end {} {} {}'.format(i, projectFolderName,len(lstFpASTInfos)))
        except:
            traceback.print_exc()


fopDataPapers='../../../../dataPapers/'
fopAlonCorpus=fopDataPapers+'java-large/'
fopDataAPICalls=fopDataPapers+'apiCallPapers/'
fopJsonData=fopDataAPICalls+'AlonJsonData/'
fopCommentExtraction=fopDataAPICalls+'AlonCommentExtraction/'
fopImpportExtraction=fopDataAPICalls+'AlonImportExtraction/'
createDirIfNotExist(fopJsonData)
createDirIfNotExist(fopCommentExtraction)

lstFopJsonData=[]
lstFopComment=[]
lstFpLogComment=[]
lstFopImport=[]
lstFolderNames=['training','validation','test']

for i in range(0,len(lstFolderNames)):
    folderName=lstFolderNames[i]
    lstFopComment.append(fopCommentExtraction+folderName+'/')
    lstFpLogComment.append(fopCommentExtraction+'log_'+folderName+'.txt')
    lstFopImport.append(fopImpportExtraction+folderName+'/')
    lstFopJsonData.append(fopJsonData+folderName+'/')

for i in range(0,len(lstFolderNames)):
    statisticComment(lstFopJsonData[i], lstFopComment[i], lstFpLogComment[i],lstFopImport[i])




