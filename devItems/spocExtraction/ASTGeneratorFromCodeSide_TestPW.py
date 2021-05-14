import glob
import sys, os
import operator
import clang.cindex

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult


fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolderTestP=fopData+'textInSPOC/testPOnlyC/'
fpCombineASTsTestP= fopTextInSPoC + 'combineASTs_TestP.txt'
fopStatisticFolderTestW=fopData+'textInSPOC/testWOnlyC/'
fopASTForCTestW=fopData+'textInSPOC/testWASTForC/'
fopASTForCTestP=fopData+'textInSPOC/testPASTForC/'
fpCombineASTsTestW= fopTextInSPoC + 'combineASTs_TestW.txt'

createDirIfNotExist(fopASTForCTestP)
createDirIfNotExist(fopASTForCTestW)

numOmit=30
lstFiles=sorted(glob.glob(fopStatisticFolderTestP+ "*_code.cpp"))
dictCountWords={}
f1=open(fpCombineASTsTestP, 'w')
f1.write('')
f1.close()

for index in range(0,len(lstFiles)):
    fpCodeFileCPP=lstFiles[index]
    fineName=os.path.basename(fpCodeFileCPP)
    fpASTItem = fopASTForCTestP + fineName.replace('_code.txt', '_ast.txt')
    # fFile=open(fpCodeFileCPP, 'r')
    # strContentOfFile=fFile.read().strip()
    # fFile.close()
    # indexTu = clang.cindex.Index.create()
    jsonObject = runASTGenAndSeeResult(fpCodeFileCPP, fpASTItem, numOmit)
    # strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
    print('{} {}'.format(index, fpCodeFileCPP))

    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend = '\n'.join([fineName, str(jsonObject), '\n\n\n'])
    f1 = open(fpCombineASTsTestP, 'a')
    f1.write(strContentAppend)
    f1.close()

lstFiles=sorted(glob.glob(fopStatisticFolderTestW+ "*_code.cpp"))
dictCountWords={}
f1=open(fpCombineASTsTestW, 'w')
f1.write('')
f1.close()

for index in range(0,len(lstFiles)):
    fpCodeFileCPP=lstFiles[index]
    fineName=os.path.basename(fpCodeFileCPP)
    fpASTItem = fopASTForCTestW + fineName.replace('_code.txt', '_ast.txt')
    # fFile=open(fpCodeFileCPP, 'r')
    # strContentOfFile=fFile.read().strip()
    # fFile.close()
    # indexTu = clang.cindex.Index.create()
    jsonObject = runASTGenAndSeeResult(fpCodeFileCPP, fpASTItem, numOmit)
    # strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
    print('{} {}'.format(index, fpCodeFileCPP))

    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend = '\n'.join([fineName, str(jsonObject), '\n\n\n'])
    f1 = open(fpCombineASTsTestW, 'a')
    f1.write(strContentAppend)
    f1.close()



























