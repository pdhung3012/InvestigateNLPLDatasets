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
import  gzip,json
import ast

def generateScript(fpDictRepo, fopMetadata,fopCommitMessage,fopRepoExtract,fopRepoZip,fpLogCommandDownload,fpLogCommandExtract,fpLogCommandCommit):
    try:
        f1=open(fpDictRepo,'r')
        arrDicts=f1.read().strip().split('\n')
        f1.close()
        createDirIfNotExist(fopMetadata)
        createDirIfNotExist(fopCommitMessage)
        createDirIfNotExist(fopRepoZip)
        createDirIfNotExist(fopRepoExtract)

        if not os.path.exists(fpLogCommandDownload):
            f1=open(fpLogCommandDownload,'w')
            f1.write('')
            f1.close()
        if not os.path.exists(fpLogCommandExtract):
            f1 = open(fpLogCommandExtract, 'w')
            f1.write('')
            f1.close()
        if not os.path.exists(fpLogCommandCommit):
            f1 = open(fpLogCommandCommit, 'w')
            f1.write('')
            f1.close()

        lstCommandDownloads=[]
        lstCommandExtract = []
        lstCommandCommitMessage = []
        for i in range(0,len(arrDicts)):
            try:
                arrItem=arrDicts[i].strip().split('\t')
                if len(arrItem)>=2:
                    strAuthor=arrItem[0].split('__')[0]
                    strRepo = arrItem[0].split('__')[1]
                    strSHA=''
                    strZipDownload='https://github.com/{}/{}/tree/{}'.format(strAuthor,strRepo,strSHA)
                    fopZipLocation=fopRepoZip+strAuthor+'/'+strRepo+'/'
                    createDirIfNotExist(fopZipLocation)
                    fpZipLocation=fopZipLocation+strSHA+'.zip'
                    commandDownload='wget {} -O {}'.format(strZipDownload,fpZipLocation)
                    # print(fopRepoZip)
                    commandExtract='unzip {} -d {}'.format(fpZipLocation,fopRepoExtract)

                    createDirIfNotExist(fopMetadata+strAuthor+'/')
                    fopLocalMeta=fopMetadata+strAuthor+'/'+strRepo+'/'
                    fpLogMessage=fopCommitMessage+strAuthor+'__'+strRepo+'.txt'
                    commandFirstRemove='rm -rf {}'.format(fopLocalMeta)
                    commandCommitMessage1 ='cd {}'.format(fopMetadata+strAuthor+'/')
                    commandCommitMessage2='git clone --no-checkout https://github.com/{}/{}/'.format(strAuthor,strRepo)
                    commandCommitMessage3 = 'cd {}'.format(fopLocalMeta)
                    commandCommitMessage4 = 'git log >{}'.format(fpLogMessage)
                    commandCommitMessage5 = 'cd {}'.format(fopCommitMessage)

                    lstCommandDownloads.append(commandDownload)
                    lstCommandExtract.append(commandExtract)
                    lstCommandCommitMessage.append(commandFirstRemove)
                    lstCommandCommitMessage.append(commandCommitMessage1)
                    lstCommandCommitMessage.append(commandCommitMessage2)
                    lstCommandCommitMessage.append(commandCommitMessage3)
                    lstCommandCommitMessage.append(commandCommitMessage4)
                    lstCommandCommitMessage.append(commandCommitMessage5)
            except:
                traceback.print_exc()
        f1=open(fpLogCommandDownload,'a')
        f1.write('\n'.join(lstCommandDownloads)+'\n')
        f1.close()
        f1 = open(fpLogCommandExtract, 'a')
        f1.write('\n'.join(lstCommandExtract) + '\n')
        f1.close()
        f1 = open(fpLogCommandCommit, 'a')
        f1.write('\n'.join(lstCommandCommitMessage) + '\n')
        f1.close()

    except:
        traceback.print_exc()

fopLocalDataPapers='../../../../dataPapers/'
fopExternalDataPapers='/home/hungphd/media/dataPapersExternal/'
fopDataAlon=fopLocalDataPapers+'apiCallPapers/'
# fopExtractedJson=fopLocalDataPapers+'extractedJson_Alon/'
fopCSNGithubProjects=fopExternalDataPapers+'Alon_githubProjects/'
fpTotalBashDownload=fopCSNGithubProjects+'alon_downloads.sh'
fpTotalBashExtract=fopCSNGithubProjects+'alon_extract.sh'
fpTotalBashCommit=fopCSNGithubProjects+'alon_commit.sh'
fopMetadata=fopCSNGithubProjects+'metadata/'
fopGitMessage=fopCSNGithubProjects+'commitMessage/'
fopGitRepoExtract=fopCSNGithubProjects+'repoExtract/'
fopGitRepoZip=fopCSNGithubProjects+'repoZip/'
fopSubPath='/final/jsonl/'
# lstLanguages=['java','python','go','php','javascript','ruby']
lstFolderNames=['training','validation','test']
lstFpLogDict=[]
lstFopMetadata=[]
lstFopGitMessage=[]
lstFopGitRepoExtract=[]
lstFopGitRepoZip=[]


# for i in range(0,len(lstLanguages)):
for j in range(0,len(lstFolderNames)):
    lstFpLogDict.append(fopDataAlon+'/'+'/log_projects_'+lstFolderNames[j]+'.txt')
    lstFopMetadata.append(fopMetadata+'/'+lstFolderNames[j]+'/')
    lstFopGitMessage.append(fopGitMessage+'/'+lstFolderNames[j]+'/')
    lstFopGitRepoExtract.append(fopGitRepoExtract+'/'+lstFolderNames[j]+'/')
    lstFopGitRepoZip.append(fopGitRepoZip+'/'+lstFolderNames[j]+'/')

for i in range(0,len(lstFpLogDict)):
    generateScript(lstFpLogDict[i], lstFopMetadata[i], lstFopGitMessage[i], lstFopGitRepoExtract[i], lstFopGitRepoZip[i], fpTotalBashDownload,
                   fpTotalBashExtract, fpTotalBashCommit)
