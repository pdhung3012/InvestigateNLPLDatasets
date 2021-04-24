import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopTrainFolder=fopTextInSPoC+'trainSPOCPlain/'
fopTrainFolderOnlyC=fopTextInSPoC+'trainOnlyC/'
lstFiles=sorted(glob.glob(fopTrainFolder+ "*_code.txt"))
createDirIfNotExist(fopTrainFolderOnlyC)
for i in range(0,len(lstFiles)):
    f1=open(lstFiles[i],'r')
    fileName=os.path.basename(lstFiles[i])
    newFileName=fileName.replace('.txt','.cpp')
    fpOutpurItem=fopTrainFolderOnlyC+newFileName
    strContent=f1.read()
    f1.close()
    strNewContent='\n'.join(['using namespace std;\n',strContent])
    f1=open(fpOutpurItem,'w')
    f1.write(strNewContent)
    f1.close()

print('done')

