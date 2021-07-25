import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

def checkComplicatedPseudoCodeAndCode(strPseudoCode,strCode):
    isCom=True
    arrPseudoCode=strPseudoCode.strip().split()
    arrCode = strCode.strip().split()
    if (len(arrCode)<=3 or len(arrPseudoCode)<=3):
        isCom=False
    elif 'main' in strPseudoCode or 'nan' in strPseudoCode or 'return' in strPseudoCode:
        isCom=False

    return isCom

def getMostComplicatedPseudocode(arrPseudoCode,arrCode,distanceHeader,topN):
    dictLen={}
    for i in range(0,len(arrPseudoCode)):
        item=arrPseudoCode[i].strip()
        numItem=len(item.split())
        dictLen[i]=numItem

    dictSortedByNum=dict(sorted(dictLen.items(), key=lambda item: item[1]))
    indxValue=0
    lstReturn=[]
    for key in dictSortedByNum.keys():
        if checkComplicatedPseudoCodeAndCode(arrPseudoCode[key],arrCode[key-distanceHeader]):
            lstReturn.append(key)
            indxValue=indxValue+1
        if( indxValue==topN):
            break
    return lstReturn




def generateMixFiles(fopPseudoCode,fopCodeFile,fopOutputMix):
    createDirIfNotExist(fopOutputMix)
    lstFileItemSPoC=glob.glob(fopCodeFile+'*_code.cpp')
    indexFile=-1
    for index in range(0,len(lstFileItemSPoC)):
        fpCodeFile=lstFileItemSPoC[index]
        indexFile=indexFile+1
        nameOfSubmission=os.path.basename(fpCodeFile).replace('_code.cpp','')
        fpPseudoCode=fopPseudoCode+nameOfSubmission+'_text.txt'
        f1=open(fpCodeFile,'r')
        arrCodeLines=f1.read().strip().split('\n')
        f1.close()
        f1 = open(fpPseudoCode, 'r')
        arrPseudoLines = f1.read().strip().split('\n')
        f1.close()

        lstIndexes=getMostComplicatedPseudocode(arrPseudoLines,arrCodeLines,distanceHeader,4)
    #     replace pseudocode to code
        for indPseudoCode in range(0,len(lstIndexes)):
            if not checkComplicatedPseudoCodeAndCode(arrPseudoLines[indPseudoCode].strip(),arrCodeLines[indPseudoCode+distanceHeader].strip()) :
                continue
            lstStrCodeCombine=[]
            for ind in range(0,distanceHeader):
                lstStrCodeCombine.append(arrCodeLines[ind])
            for ind in range(distanceHeader,len(arrCodeLines)):
                indInCode=ind-distanceHeader
                if indInCode==indPseudoCode:
                    strLinePseudo='// {}'.format(arrPseudoLines[indPseudoCode])
                    lstStrCodeCombine.append(strLinePseudo)
                else:
                    lstStrCodeCombine.append(arrCodeLines[ind])
            fpVersion=fopOutputMix+nameOfSubmission+'_v'+str(indPseudoCode+1)+'.cpp'
            f1=open(fpVersion,'w')
            f1.write('\n'.join(lstStrCodeCombine))
            f1.close()
        print('complete {}/{} {}'.format(index,len(lstFileItemSPoC),fpCodeFile))

fopData='../../../../dataPapers/textInSPOC/'
fopTrainDataCFiles=fopData+'trainOnlyC/'
fopTestWDataCFiles=fopData+'testWOnlyC/'
fopTestPDataCFiles=fopData+'testPOnlyC/'
fopTrainPseudocode=fopData+'trainSPOCPlain/'
fopTestPPseudocode=fopData+'testPSPOCPlain/'
fopTestWPseudocode=fopData+'testWSPOCPlain/'

fopMixFiles=fopData+'mix_step1/'
fopOutputTrainMixFiles=fopMixFiles+'train/'
fopOutputTestPMixFiles=fopMixFiles+'testP/'
fopOutputTestWMixFiles=fopMixFiles+'testW/'
distanceHeader=33
generateMixFiles(fopTestPPseudocode,fopTestPDataCFiles,fopOutputTestPMixFiles)
generateMixFiles(fopTestWPseudocode,fopTestWDataCFiles,fopOutputTestWMixFiles)
generateMixFiles(fopTrainPseudocode,fopTrainDataCFiles,fopOutputTrainMixFiles)




