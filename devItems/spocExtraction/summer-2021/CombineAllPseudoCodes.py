import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolder=fopData+'textInSPOC/trainSPOCPlain/'
fpCombineAllText= fopTextInSPoC + 'combinePseudoCode.txt'
fpCombineAllCode= fopTextInSPoC + 'combineProgram.txt'

lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_text.txt"))

dictCountWords={}

f1=open(fpCombineAllText,'w')
f1.write('')
f1.close()

f1=open(fpCombineAllCode,'w')
f1.write('')
f1.close()

for index in range(0,len(lstFiles)):
    fpTextFile=lstFiles[index]
    fineName=os.path.basename(fpTextFile)
    fpCodeFile=fopStatisticFolder+fineName.replace('text.txt','code.txt')
    fFile=open(fpTextFile,'r')
    strContentOfFile=fFile.read().strip()
    fFile.close()

    fFile = open(fpCodeFile, 'r')
    strContentOfCode = fFile.read().strip()
    fFile.close()


    print(fpTextFile)
    # arrContentOfFile=strContentOfFile.split('\n')
    strContentAppend='\n'.join([fineName,strContentOfFile,'\n\n\n'])
    strCodeAppend = '\n'.join([fineName, strContentOfCode, '\n\n\n'])
    f1 = open(fpCombineAllText, 'a')
    f1.write(strContentAppend)
    f1.close()
    f1 = open(fpCombineAllCode, 'a')
    f1.write(strCodeAppend)
    f1.close()



























