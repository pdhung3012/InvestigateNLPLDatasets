import operator;
import csv;
import pandas as pd;
import sys, os
import traceback
import operator
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist

fopDataFolder='/Users/hungphan/git/dataPapers/'
fopInputSPOCData=fopDataFolder+'/SPOCDataset/spoc/'
fpTrainData=fopInputSPOCData+'train/spoc-train.tsv'

fopOutputSmallData=fopDataFolder+'/outputFirst100NLs/'
fopPlainNL=fopOutputSmallData+'/NL/'
fopPlainPseudoCode=fopOutputSmallData+'/Pseudo/'
fopPlainCode=fopOutputSmallData+'/Code/'

createDirIfNotExist(fopOutputSmallData)
createDirIfNotExist(fopPlainNL)
createDirIfNotExist(fopPlainPseudoCode)
createDirIfNotExist(fopPlainCode)

def getPseudoCodeAndCode(df):
    lstText=[]
    lstCode=[]
    lstLine=[]
    for row_index, row in df_group.iterrows():
        strCode=str(row['code'])
        strText = str(row['text'])
        lstText.append(strText)
        indent=int(row['indent'])
        strLine=str(row['line'])
        lstIndent=[]
        for i in range(0,indent):
            lstIndent.append('\t')
        strIndent=''.join(lstIndent)
        strCode=''.join([strIndent,strCode])
        lstCode.append(strCode)
        lstLine.append(strLine)
    strTotalText='\n'.join(lstText)
    strTotalCode='\n'.join(lstCode)
    strTotalLine='\n'.join(lstLine)
    return strTotalText,strTotalCode,strTotalLine



tsv_file = open(fpTrainData)
df = pd.read_csv(tsv_file, delimiter="\t")
df_grouped=df.groupby(['subid','probid','workerid'])
# iterate over each group
index=0
lenGrouped=len(df_grouped)

for group_name, df_group in df_grouped:

    #print('\nCREATE TABLE {}('.format(group_name))
    #print('aaa {} {}'.format(type(df_group),group_name))
    index=index+1
    try:
        strTotalText, strTotalCode,strTotalLine=getPseudoCodeAndCode(df_group)
       # print('type {}'.format(df_group['workerid']))
      #  row0=df_group.itertuples()[0]
        workId=df_group['workerid'].iloc[0]
        probId=df_group['probid'].iloc[0]
        subId=df_group['subid'].iloc[0]
        strIndex="{:03d}".format(index)
        fpPlainPseudo='{}/{}_pseudo_{}_{}_{}.txt'.format(fopPlainPseudoCode,strIndex,workId,probId,subId)
        fpPlainCode = '{}/{}_code_{}_{}_{}.txt'.format(fopPlainCode,strIndex, workId, probId, subId)
        fpPlainNL = '{}/{}_nl_{}_{}_{}.txt'.format(fopPlainNL,strIndex, workId, probId, subId)

        fff=open(fpPlainPseudo,'w')
        fff.write(strTotalText)
        fff.close()
        fff = open(fpPlainCode, 'w')
        fff.write(strTotalCode)
        fff.close()
        fff = open(fpPlainNL, 'w')
        fff.write('')
        fff.close()




    except Exception as e:
        print('{}\n{}'.format(str(e),traceback.format_exc()))
    print('Index {}/{}'.format(index,lenGrouped))
    if index == 100:
        break

