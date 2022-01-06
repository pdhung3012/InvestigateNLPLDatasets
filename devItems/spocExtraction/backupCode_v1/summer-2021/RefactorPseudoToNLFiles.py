import operator;
import csv;
import pandas as pd;
import sys, os
import traceback
import operator
import shutil
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist

fopDataFolder='/Users/hungphan/git/dataPapers/'
fopCombine=fopDataFolder+'/Hung_check100/combinePseudo-Code/'
fopNL=fopDataFolder+'/Hung_check100/NL/'
fopPseudo=fopDataFolder+'/Hung_check100/Pseudo/'
fpLogDifference=fopDataFolder+'/Hung_check100/logNLPseudoCodeDiff.txt'

list_dir = os.listdir(fopCombine)  # Convert to lower case
list_dir = sorted(list_dir)

lstLog=[]
for filename in list_dir:
    if not 'pseudo' in filename:
        continue

    nameNL=filename.replace('pseudo','nl')
    fpPseudo=fopCombine+filename
    fpOldPseudo=fopPseudo+filename
    fpNL=fopNL+nameNL
    shutil.copy2(fpPseudo,fpNL)

    fff=open(fpOldPseudo,'r')
    arrPseudos=fff.read().split('\n')
    fff.close()
    fff=open(fpNL,'r')
    arrNLs=fff.read().split('\n')
    fff.close()
    lstLog.append(nameNL)
    for i in range(0,len(arrPseudos)):
        itPseudo=arrPseudos[i].strip()
        itNL=arrNLs[i].strip()

        if itPseudo != itNL:

            strItem='Line {} Pseudo: {}\nLine {}     NL: {}'.format((i+1),itPseudo,(i+1),itNL)
            print(strItem)
            lstLog.append(strItem)
    lstLog.append('\n\n')

fff=open(fpLogDifference,'w')
fff.write('\n'.join(lstLog))
fff.close()





