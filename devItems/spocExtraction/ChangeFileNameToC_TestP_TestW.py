import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopTestPFolder=fopTextInSPoC+'testPSPOCPlain/'
fopTestPFolderOnlyC=fopTextInSPoC+'testPPOnlyC/'
lstFiles=sorted(glob.glob(fopTestPFolder+ "*_code.txt"))
createDirIfNotExist(fopTestPFolderOnlyC)
for i in range(0,len(lstFiles)):
    f1=open(lstFiles[i],'r')
    fileName=os.path.basename(lstFiles[i])
    newFileName=fileName.replace('.txt','.cpp')
    fpOutpurItem=fopTestPFolderOnlyC+newFileName
    strContent=f1.read()
    f1.close()
    strNewContent='\n'.join(['using namespace std;\n',strContent])
    f1=open(fpOutpurItem,'w')
    f1.write(strNewContent)
    f1.close()

fopTestWFolder=fopTextInSPoC+'TestWSPOCPlain/'
fopTestWFolderOnlyC=fopTextInSPoC+'testWPOnlyC/'
lstFiles=sorted(glob.glob(fopTestWFolder+ "*_code.txt"))
createDirIfNotExist(fopTestWFolderOnlyC)
for i in range(0,len(lstFiles)):
    f1=open(lstFiles[i],'r')
    fileName=os.path.basename(lstFiles[i])
    newFileName=fileName.replace('.txt','.cpp')
    fpOutpurItem=fopTestWFolderOnlyC+newFileName
    strContent=f1.read()
    f1.close()
    strNewContent='\n'.join(['using namespace std;\n',strContent])
    f1=open(fpOutpurItem,'w')
    f1.write(strNewContent)
    f1.close()


print('done')

