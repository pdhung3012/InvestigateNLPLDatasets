import glob
import sys, os
import operator
import clang.cindex

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
from CASTWalker import  Walker

fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolder=fopData+'textInSPOC/trainOnlyC/'
fopASTForC=fopData+'textInSPOC/trainASTForC/'
fpCombineASTs= fopTextInSPoC + 'combineASTs.txt'

lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.cpp"))

createDirIfNotExist(fopASTForC)

dictCountWords={}

f1=open(fpCombineASTs, 'w')
f1.write('')
f1.close()


# walker = Walker('')
numOmit=30

for index in range(0,len(lstFiles)):
    fpCodeFileCPP=lstFiles[index]
    fineName=os.path.basename(fpCodeFileCPP)
    fpASTItem=fopASTForC+fineName.replace('_code.txt','_ast.txt')
    # fFile=open(fpCodeFileCPP, 'r')
    # strContentOfFile=fFile.read().strip()
    # fFile.close()
    # indexTu = clang.cindex.Index.create()
    jsonObject=runASTGenAndSeeResult(fpCodeFileCPP,fpASTItem,numOmit)
    # strASTOfFile=walker.getRepresentASTFromFile(fpCodeFileCPP,indexTu)
    print('{} {}'.format(index, fpCodeFileCPP))

    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend='\n'.join([fineName,str(jsonObject),'\n\n\n'])
    f1 = open(fpCombineASTs, 'a')
    f1.write(strContentAppend)
    f1.close()




























