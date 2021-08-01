import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import pygraphviz as pgv
import pylab,traceback
from pyparsing import OneOrMore, nestedExpr
from ExtractASTsFromJavaProjects import getJsonDict

def logFileLocationForEachJavaProjects(fopItemAlonCorpus,fopItemJsonData,fpLogTotalProject,parser,isCollectFromStart):
    createDirIfNotExist(fopItemAlonCorpus)
    createDirIfNotExist(fopItemJsonData)
    lstProjectNames=glob.glob(fopItemAlonCorpus+'*/')
    dictFilesPerProject={}
    dictAlreadyDownloadProject={}
    if isCollectFromStart:
        f1=open(fpLogTotalProject,'w')
        f1.write('')
        f1.close()
    else:
        f1 = open(fpLogTotalProject, 'r')
        arrAlready=f1.read().strip().split('\n')
        f1.close()
        for item in arrAlready:
            arrTabs=item.split('\t')
            if len(arrTabs)>=4:
                dictAlreadyDownloadProject[arrTabs[0]]=1
    for i in range(0,len(lstProjectNames)):
        try:
            fopProjectItem=lstProjectNames[i]
            arrFopItem=fopProjectItem.split('/')
            projectFolderName=arrFopItem[len(arrFopItem)-2]
            if projectFolderName in dictAlreadyDownloadProject.keys():
                continue
            # print('folder name {}'.format(projectFolderName))
            fpItemDataAPICalls=fopItemJsonData+projectFolderName+'.txt'
            lstJavaFiles=glob.glob(fopProjectItem+'/**/*.java',recursive=True)
            # print('{} len {}'.format(fopProjectItem,len(lstJavaFiles)))
            dictFilesPerProject[projectFolderName]=len(lstJavaFiles)
            dictJavaFiles={}
            for j in range(0,len(lstJavaFiles)):
                fpItemJava=lstJavaFiles[j]
                key=str(j+1)
                dictJavaFiles[key]=fpItemJava
            lstWriteToFiles=[]
            for key in dictJavaFiles.keys():
                lstWriteToFiles.append('{}\t{}'.format(key,dictJavaFiles[key]))
            f1=open(fpItemDataAPICalls,'w')
            f1.write('\n'.join(lstWriteToFiles))
            f1.close()


            print('{} Prepare get ast project {} with {} files'.format((i+1),fopProjectItem,len(lstJavaFiles)))
            fopASTItemFather=fopItemJsonData+projectFolderName+'/'
            createDirIfNotExist(fopASTItemFather)
            numProjectRunOK=0
            for key in dictJavaFiles.keys():
                try:
                    fpItemJavaFiles = dictJavaFiles[key]
                    jsonObject = getJsonDict(fpItemJavaFiles, parser)
                    if (jsonObject is not None):
                        fpJson = fopASTItemFather + str(key) + '_ast.txt'
                        f1 = open(fpJson, 'w')
                        f1.write(str(jsonObject))
                        f1.close()
                        numProjectRunOK=numProjectRunOK+1
                except:
                    traceback.print_exc()
            print('{} End get ast project {} with {} files'.format((i+1),fopProjectItem, len(lstJavaFiles)))
            f1 = open(fpLogTotalProject, 'a')
            f1.write('{}\t{}\t{}\t{}\n'.format(projectFolderName,numProjectRunOK,len(dictJavaFiles.keys()),dictFilesPerProject[projectFolderName]))
            f1.close()
        except:
            traceback.print_exc()

fopDataPapers='../../../../dataPapers/'
fopAlonCorpus=fopDataPapers+'java-large/'
fopDataAPICalls=fopDataPapers+'apiCallPapers/'
fopJsonData=fopDataPapers+'apiCallPapers/AlonJsonData/'
# fopFilesPerProjectData=fopDataPapers+'apiCallPapers/AlonFilesPerProject/'

fopDataRoot='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopDataRoot+'build-tree-sitter/'
fpLanguageSo=fopBuildFolder+'my-languages.so'


createDirIfNotExist(fopJsonData)
# createDirIfNotExist(fopFilesPerProjectData)
lstFopAlonCorpus=[]
lstFopJsonData=[]
lstFpLogAPICalls=[]
lstFopFilesPerProjectData=[]

lstFolderNames=['training','test','validation']

JAVA_LANGUAGE = Language(fpLanguageSo, 'java')
parser = Parser()
parser.set_language(JAVA_LANGUAGE)
isCollectFromStart=False


for i in range(0,len(lstFolderNames)):
    folderName=lstFolderNames[i]
    lstFopJsonData.append(fopJsonData+folderName+'/')
    lstFopAlonCorpus.append(fopAlonCorpus+folderName+'/')
    lstFpLogAPICalls.append(fopDataAPICalls+'log_projects_'+folderName+'.txt')
    # lstFopFilesPerProjectData.append(fopFilesPerProjectData+folderName+'/')

for i in range(0,len(lstFolderNames)):
    logFileLocationForEachJavaProjects(lstFopAlonCorpus[i], lstFopJsonData[i],
                                        lstFpLogAPICalls[i], parser,isCollectFromStart)



