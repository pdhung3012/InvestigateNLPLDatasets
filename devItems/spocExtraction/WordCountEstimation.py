import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolder=fopData+'textInSPOC/trainSPOCPlain/'
fpNumLogText=fopTextInSPoC+'numLogText.txt'

lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.txt"))

dictCountWords={}

for index in range(0,len(lstFiles)):
    fpTextFile=lstFiles[index]
    fFile=open(fpTextFile,'r')
    strContentOfFile=fFile.read().strip()
    fFile.close()
    print(fpTextFile)
    arrContentOfFile=strContentOfFile.split('\n')

    for j in range(0,len(arrContentOfFile)):
        lstTexts=arrContentOfFile[j].split(' ')
        for itemText in lstTexts:
            itemText=itemText.strip()
            if itemText == '':
                continue
            if not itemText in dictCountWords.keys():
                dictCountWords[itemText]=1
            else:
                dictCountWords[itemText]= dictCountWords[itemText] + 1


dictCountWords = dict(sorted(dictCountWords.items(), key=lambda item: item[1], reverse=True))
writeDictToFileText(dictCountWords,  fpNumLogText)


























