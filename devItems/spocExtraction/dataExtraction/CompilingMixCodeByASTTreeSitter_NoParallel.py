import glob
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
from LibForGraphExtractionFromMixCode import getJsonDict

def checkAndGenerateAST(i, lstCFilesStep1, fopStep2,fopASTInfo,fopStep4GraphAll,fopStep4GraphSimplify,fpLog,nlpObj,offsetContext,isSaveGraph):
    fpMixFileCPP = lstCFilesStep1[i]
    lenFile=len(lstCFilesStep1)
    nameOfFile = os.path.basename(fpMixFileCPP)
    nameWithoutExtension=nameOfFile.replace('.cpp','')
    fpCompiledCPP = fopStep2 + nameOfFile
    fpASTItem = fopASTInfo + nameOfFile.replace('.cpp', '_ast.txt')
    isRunOK = False
    try:
        parser = Parser()
        parser.set_language(CPP_LANGUAGE)
        # getJsonDict(fpCPP, fpDotGraphAllText, fpDotGraphAllImage, fpDotGraphSimplifyText, fpDotGraphSimplifyImage,
        #             parser, offsetContext)
        fpDotGraphAllText=fopStep4GraphAll+nameWithoutExtension+'_all.dot'
        fpDotGraphAllImage = fopStep4GraphAll + nameWithoutExtension + '_all.png'
        fpDotGraphSimplifyText = fopStep4GraphSimplify + nameWithoutExtension + '_simplify.dot'
        fpDotGraphSimplifyImage = fopStep4GraphSimplify + nameWithoutExtension + '_simplify.png'
        jsonObject = getJsonDict(fpMixFileCPP,fpDotGraphAllText, fpDotGraphAllImage, fpDotGraphSimplifyText, fpDotGraphSimplifyImage,parser,nlpObj,offsetContext,isSaveGraph)
        # strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)

        if str(jsonObject) != 'Error' or str(jsonObject) != 'None':
            # arrContentOfFile=strContentOfFile.split('\n')
            strContentAppend = '\n'.join([nameOfFile, str(jsonObject), '\n\n\n'])
            f1 = open(fpASTItem, 'w')
            f1.write(strContentAppend)
            f1.close()
            shutil.copyfile(fpMixFileCPP, fopStep2 + nameOfFile)
            f1 = open(fpLog, 'a')
            f1.write('{}\t{}\n'.format(nameOfFile, 'True'))
            f1.close()
            isRunOK = True
            # print('{}\t{}'.format(strCommand,isRunOK))
        else:
            f1 = open(fpLog, 'a')
            f1.write('{}\t{}\n'.format(nameOfFile, 'False'))
            f1.close()
            # print('{}\t{}'.format(strCommand,isRunOK))
        print('OK {}/{} {}'.format(i, len(lstCFilesStep1), fpMixFileCPP))
    except:
        print("Exception in user code:")
        print("-" * 60)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
        print('Error: {} {}'.format(i, fpMixFileCPP))
        print('Error {}/{} {}'.format(i, len(lstCFilesStep1), fpMixFileCPP))
    return i


def compileMixCCodeAndSave(fopStep1,fopStep2,fopASTInfo,fopStep4GraphAll,fopStep4GraphSimplify,fpLog,nlpObj,offsetContext,isSaveGraph):
    createDirIfNotExist(fopStep2)
    createDirIfNotExist(fopASTInfo)
    createDirIfNotExist(fopStep4GraphAll)
    createDirIfNotExist(fopStep4GraphSimplify)

    f1 = open(fpLog, 'w')
    f1.write('')
    f1.close()

    lstCFilesStep1=glob.glob(fopStep1+'*.cpp')

    # t = time.time()
    # Parallel(n_jobs=8)(delayed(checkAndGenerateAST)(i,lstCFilesStep1, fopStep2, fopASTInfo,fpLog) for i in range(0,len(lstCFilesStep1)))
    for i in range(0, len(lstCFilesStep1)):
        # if i!=2:
        #     continue
        checkAndGenerateAST(i, lstCFilesStep1, fopStep2, fopASTInfo,fopStep4GraphAll,fopStep4GraphSimplify,fpLog,nlpObj,offsetContext,isSaveGraph)

        # break
    # print(time.time() - t)

    # for i in range(0,len(lstCFilesStep1)):
    #     checkAndGenerateAST( i,)


fopData='../../../../dataPapers/textInSPOC/mixCode/'

fopMixFiles=fopData+'step1/'
fopASTFiles=fopData+'step3_treesitter/'
fopCompiledFiles=fopData+'step2/'
fopStep4GraphAll=fopData+'step4_graphAll/'
fopStep4GraphSimplify=fopData+'step4_graphSimplify/'
fopStep1TrainMixFiles=fopMixFiles+'train/'
fopStep1TestPMixFiles=fopMixFiles+'testP/'
fopStep1TestWMixFiles=fopMixFiles+'testW/'
fopStep2TrainMixFiles=fopCompiledFiles+'train/'
fopStep2TestPMixFiles=fopCompiledFiles+'testP/'
fopStep2TestWMixFiles=fopCompiledFiles+'testW/'
fopStep3TrainMixFiles=fopASTFiles+'train/'
fopStep3TestPMixFiles=fopASTFiles+'testP/'
fopStep3TestWMixFiles=fopASTFiles+'testW/'

fopStep4GraphAllTestP=fopStep4GraphAll+'testP/'
fopStep4GraphAllTestW=fopStep4GraphAll+'testW/'
fopStep4GraphAllTrain=fopStep4GraphAll+'train/'
fopStep4GraphSimplifyTestP=fopStep4GraphSimplify+'testP/'
fopStep4GraphSimplifyTestW=fopStep4GraphSimplify+'testW/'
fopStep4GraphSimplifyTrain=fopStep4GraphSimplify+'train/'




fpLogTrain=fopCompiledFiles+'log_train.txt'
fpLogTestP=fopCompiledFiles+'log_testP.txt'
fpLogTestW=fopCompiledFiles+'log_testW.txt'

fopDataRoot='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopDataRoot+'build-tree-sitter/'
fpLanguageSo=fopBuildFolder+'my-languages.so'

from pycorenlp import StanfordCoreNLP
nlpObj = StanfordCoreNLP('http://localhost:9000')

CPP_LANGUAGE = Language(fpLanguageSo, 'cpp')
parser = Parser()
parser.set_language(CPP_LANGUAGE)



numOmit=30
offsetContext=3
compileMixCCodeAndSave(fopStep1TestPMixFiles,fopStep2TestPMixFiles,fopStep3TestPMixFiles,fopStep4GraphAllTestP,fopStep4GraphSimplifyTestP,fpLogTestP,nlpObj,offsetContext,False)
compileMixCCodeAndSave(fopStep1TestWMixFiles,fopStep2TestWMixFiles,fopStep3TestWMixFiles,fopStep4GraphAllTestW,fopStep4GraphSimplifyTestW,fpLogTestW,nlpObj,offsetContext,False)
compileMixCCodeAndSave(fopStep1TrainMixFiles,fopStep2TrainMixFiles,fopStep3TrainMixFiles,fopStep4GraphAllTrain,fopStep4GraphSimplifyTrain,fpLogTrain,nlpObj,offsetContext,False)


