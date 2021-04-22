import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFile

fopData='/Users/hungphan/git/dataPapers/'
fopStatisticFolder=fopData+'textInSPOC/trainSPOCPlain/'
fpTextLogPOS=fopData+'textInSPOC/textLogPOS_train.txt'

lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.txt"))

dictAllPoses={}

for index in range(0,len(lstFiles)):
    fpTextFile=lstFiles[index]
    fFile=open(fpTextFile,'r')
    strContentOfFile=fFile.read().strip()
    fFile.close()
    print(fpTextFile)
    arrContentOfFile=strContentOfFile.split('\n')

    for j in range(0,len(arrContentOfFile)):
        lstPoses=getPOSInfo(arrContentOfFile[j])
        for itemPOS in lstPoses:
            if not itemPOS[1] in dictAllPoses.keys():
                dictAllPoses[itemPOS[1]]=1
            else:
                dictAllPoses[itemPOS[1]]= dictAllPoses[itemPOS[1]] + 1

dictAllPoses = dict(sorted(dictAllPoses.items(), key=lambda item: item[1],reverse=True))
writeDictToFile(dictAllPoses,fpTextLogPOS)


























