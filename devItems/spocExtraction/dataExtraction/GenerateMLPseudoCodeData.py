import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

from tree_sitter import Language, Parser
from LibForGraphExtractionFromRawCode import getJsonDict,getTerminalValue
import ast
import re

fopRoot='../../../../dataPapers/textInSPOC/correctCodeRaw/'
fopMixVersion=fopRoot+'step4_mixCode/'
fopMixDataAndLabel=fopRoot+'step5_data_mixCode/'
createDirIfNotExist(fopMixDataAndLabel)
lstSubFolder=glob.glob(fopMixVersion+'*/')

def scoreName(percentage):
    scoreLevel='1'
    if percentage <=10:
        scoreLevel='1'
    elif percentage>10 and percentage<=20:
        scoreLevel='2'
    elif percentage>20 and percentage<=30:
        scoreLevel='3'
    elif percentage>30 and percentage<=40:
        scoreLevel='4'
    elif percentage>40 and percentage<=50:
        scoreLevel='5'
    elif percentage>50 and percentage<=60:
        scoreLevel='6'
    elif percentage>60 and percentage<=70:
        scoreLevel='7'
    elif percentage>70 and percentage<=80:
        scoreLevel='8'
    elif percentage>80 and percentage<=90:
        scoreLevel='9'
    else:
        scoreLevel='10'
    return scoreLevel
for fopTrain2Test in lstSubFolder:
    arrTemps=fopTrain2Test.split('/')
    fonTrain2Test=arrTemps[len(arrTemps)-2]
    print(fonTrain2Test)
    fnLocation=fonTrain2Test+'.location.txt'
    fnLabelCodeClass = fonTrain2Test + '.label.codeClass.txt'
    fnLabelNumStmts = fonTrain2Test + '.label.numStmt.txt'
    fnLabelPercentageAppear = fonTrain2Test + '.label.percentAppear.txt'
    fnDetailsNumStmts = fonTrain2Test + '.label.numStmtDetails.txt'
    fnInputPseudo = fonTrain2Test + '.input.pseudo.txt'
    fnInputPrefix = fonTrain2Test + '.input.prefix.txt'
    fnInputPostfix = fonTrain2Test + '.input.postfix.txt'
    fnOutputAppearInCode = fonTrain2Test + '.output.appear.txt'

    fpLocation=fopMixDataAndLabel+fnLocation
    fpLabelCodeClass = fopMixDataAndLabel+fnLabelCodeClass
    fpLabelNumStmts = fopMixDataAndLabel + fnLabelNumStmts
    fpLabelPercentageAppear = fopMixDataAndLabel + fnLabelPercentageAppear
    fpDetailsNumStmts = fopMixDataAndLabel + fnDetailsNumStmts
    fpInputPseudo = fopMixDataAndLabel + fnInputPseudo
    fpInputPrefix = fopMixDataAndLabel + fnInputPrefix
    fpInputPostfix = fopMixDataAndLabel + fnInputPostfix
    fpOutputAppearInCode = fopMixDataAndLabel + fnOutputAppearInCode


    lstLocation=[]
    lstLabelCodeClass = []
    lstLabelNumStmts = []
    lstLabelPercentAppear = []
    lstDetailsNumStmts = []
    lstInputPseudo = []
    lstInputPrefix = []
    lstInputPostfix = []
    lstOutputAppearInCode = []

    lstFopIdCode=glob.glob(fopTrain2Test+'/*/')

    for fopItemIdCode in lstFopIdCode:
        idCode=os.path.dirname(fopItemIdCode)
        lstFpItemLabels=glob.glob(fopItemIdCode+'/v_*_label.txt')

        try:
            f1 = open(fopItemIdCode + '/_a_code.cpp')
            arrCodes = f1.read().strip().split('\n')
            f1.close()

            for fpItemLbl in lstFpItemLabels:
                try:
                    itemVersionName = os.path.basename(fpItemLbl).replace('_label.txt', '')
                    f1 = open(fpItemLbl, 'r')
                    arrLblLine = f1.read().strip().split('\n')
                    f1.close()
                    lstLabelCodeClass.append(arrLblLine[0])
                    lstLabelNumStmts.append(arrLblLine[2])
                    lstDetailsNumStmts.append(arrLblLine[4])
                    startLineMainStmt = int(arrLblLine[1].split('-')[0])
                    endLineMainStmt = int(arrLblLine[1].split('-')[2])
                    lstInputPrefix.append(arrCodes[startLineMainStmt-1])
                    lstInputPostfix.append(arrCodes[endLineMainStmt+1])
                    lstOutputAppearInCode.append(arrLblLine[9])
                    lstInputPseudo.append(arrLblLine[8])
                    arrLastLines=arrLblLine[10].split('\t')
                    lstLabelPercentAppear.append(scoreName(float(arrLastLines[2])*100))
                    strItemLoc = '{}\t{}'.format(idCode, itemVersionName)
                    lstLocation.append(strItemLoc)
                    # print('len {}'.format(len(lstLocation)))
                except:
                    traceback.print_exc()
        except:
            traceback.print_exc()

    f1=open(fpLocation,'w')
    f1.write('\n'.join(lstLocation))
    f1.close()
    f1=open(fpLabelCodeClass,'w')
    f1.write('\n'.join(lstLabelCodeClass))
    f1.close()
    f1=open(fpLabelNumStmts,'w')
    f1.write('\n'.join(lstLabelNumStmts))
    f1.close()
    f1=open(fpDetailsNumStmts,'w')
    f1.write('\n'.join(lstDetailsNumStmts))
    f1.close()
    f1=open(fpInputPseudo,'w')
    f1.write('\n'.join(lstInputPseudo))
    f1.close()
    f1=open(fpInputPrefix,'w')
    f1.write('\n'.join(lstInputPrefix))
    f1.close()
    f1=open(fpInputPostfix,'w')
    f1.write('\n'.join(lstInputPostfix))
    f1.close()
    f1=open(fpOutputAppearInCode,'w')
    f1.write('\n'.join(lstOutputAppearInCode))
    f1.close()
    f1=open(fpLabelPercentageAppear,'w')
    f1.write('\n'.join(lstLabelPercentAppear))
    f1.close()
    print('end {}'.format(fopTrain2Test))
