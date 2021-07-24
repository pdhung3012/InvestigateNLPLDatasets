import glob
import sys, os
import operator,traceback
import shutil

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult

def compileMixCCodeAndSave(fopStep1,fopStep2,fopASTInfo,fpLog,numOmit):
    createDirIfNotExist(fopStep2)
    createDirIfNotExist(fopASTInfo)

    f1 = open(fpLog, 'w')
    f1.write('')
    f1.close()

    lstCFilesStep1=glob.glob(fopStep1+'*.cpp')
    for i in range(0,len(lstCFilesStep1)):
        fpMixFileCPP=lstCFilesStep1[i]
        nameOfFile=os.path.basename(fpMixFileCPP)
        fpCompiledCPP=fopStep2+nameOfFile
        fpASTItem = fopASTInfo + nameOfFile.replace('.cpp', '_ast.txt')
        isRunOK=False
        try:

            jsonObject = runASTGenAndSeeResult(fpMixFileCPP, fpASTItem, numOmit)
            # strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
            print('{} {}'.format(i, fpMixFileCPP))
            if str(jsonObject)!='Error' or str(jsonObject)!='None':
                # arrContentOfFile=strContentOfFile.split('\n')
                strContentAppend = '\n'.join([nameOfFile, str(jsonObject), '\n\n\n'])
                f1 = open(fpASTItem, 'w')
                f1.write(strContentAppend)
                f1.close()
                shutil.copyfile(fpMixFileCPP, fopStep2+nameOfFile)
                f1 = open(fpLog, 'a')
                f1.write('{}\t{}\n'.format(nameOfFile,'True'))
                f1.close()
                iwRunOK=True
            else:
                f1 = open(fpLog, 'a')
                f1.write('{}\t{}\n'.format(nameOfFile, 'False'))
                f1.close()
        except:
            print("Exception in user code:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            print('Error: {} {}'.format(i,fpMixFileCPP))

fopData='../../../../dataPapers/textInSPOC/'

fopMixFiles=fopData+'mix_step1/'
fopASTFiles=fopData+'mix_step3/'
fopCompiledFiles=fopData+'mix_step2/'
fopStep1TrainMixFiles=fopMixFiles+'train/'
fopStep1TestPMixFiles=fopMixFiles+'testP/'
fopStep1TestWMixFiles=fopMixFiles+'testW/'
fopStep2TrainMixFiles=fopCompiledFiles+'train/'
fopStep2TestPMixFiles=fopCompiledFiles+'testP/'
fopStep2TestWMixFiles=fopCompiledFiles+'testW/'
fopStep3TrainMixFiles=fopASTFiles+'train/'
fopStep3TestPMixFiles=fopASTFiles+'testP/'
fopStep3TestWMixFiles=fopASTFiles+'testW/'
fpLogTrain=fopCompiledFiles+'log_train.txt'
fpLogTestP=fopCompiledFiles+'log_testP.txt'
fpLogTestW=fopCompiledFiles+'log_testW.txt'
numOmit=30
compileMixCCodeAndSave(fopStep1TestPMixFiles,fopStep2TestPMixFiles,fopStep3TestPMixFiles,fpLogTestP,numOmit)


