import glob
import sys, os
import operator
import clang.cindex

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from CASTWalker import  Walker

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolderTestP=fopData+'textInSPOC/testPOnlyC/'
fpCombineASTsTestP= fopTextInSPoC + 'combineASTs_TestP.txt'
fopStatisticFolderTestW=fopData+'textInSPOC/testWOnlyC/'
fpCombineASTsTestW= fopTextInSPoC + 'combineASTs_TestW.txt'



lstFiles=sorted(glob.glob(fopStatisticFolderTestP+ "*_code.cpp"))
dictCountWords={}
f1=open(fpCombineASTsTestP, 'w')
f1.write('')
f1.close()
walker = Walker('')
for index in range(0,len(lstFiles)):
    fpCodeFileCPP=lstFiles[index]
    fineName=os.path.basename(fpCodeFileCPP)
    # fFile=open(fpCodeFileCPP, 'r')
    # strContentOfFile=fFile.read().strip()
    # fFile.close()
    indexTu = clang.cindex.Index.create()

    strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
    print('{} {}'.format(index, fpCodeFileCPP))

    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend='\n'.join([fineName,strASTOfFile,'\n\n\n'])
    f1 = open(fpCombineASTsTestP, 'a')
    f1.write(strContentAppend)
    f1.close()

lstFiles=sorted(glob.glob(fopStatisticFolderTestW+ "*_code.cpp"))
dictCountWords={}
f1=open(fpCombineASTsTestW, 'w')
f1.write('')
f1.close()
walker = Walker('')
for index in range(0,len(lstFiles)):
    fpCodeFileCPP=lstFiles[index]
    fineName=os.path.basename(fpCodeFileCPP)
    # fFile=open(fpCodeFileCPP, 'r')
    # strContentOfFile=fFile.read().strip()
    # fFile.close()
    indexTu = clang.cindex.Index.create()

    strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
    print('{} {}'.format(index, fpCodeFileCPP))

    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend='\n'.join([fineName,strASTOfFile,'\n\n\n'])
    f1 = open(fpCombineASTsTestW, 'a')
    f1.write(strContentAppend)
    f1.close()



























