import glob
import sys, os
import operator
import clang.cindex

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from CASTWalker import  Walker

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolder=fopData+'textInSPOC/trainOnlyC/'
fpCombineASTs= fopTextInSPoC + 'combineASTs.txt'

lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.cpp"))

dictCountWords={}

f1=open(fpCombineASTs, 'w')
f1.write('')
f1.close()


walker = Walker('')
indexTu = clang.cindex.Index.create()

for index in range(0,len(lstFiles)):
    fpCodeFileCPP=lstFiles[index]
    fineName=os.path.basename(fpCodeFileCPP)
    fFile=open(fpCodeFileCPP, 'r')
    strContentOfFile=fFile.read().strip()
    fFile.close()



    strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
    print('{} {}'.format(index, fpCodeFileCPP))

    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend='\n'.join([fineName,strASTOfFile,'\n\n\n'])
    f1 = open(fpCombineASTs, 'a')
    f1.write(strContentAppend)
    f1.close()




























