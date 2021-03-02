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
fopOutputSPOCNested=fopDataFolder+'/outputSPOCNested/'
fopOutputSPOCPlain=fopDataFolder+'/outputSPOCPlain/'
fpTrainData=fopInputSPOCData+'train/spoc-train.tsv'

createDirIfNotExist(fopOutputSPOCNested)
createDirIfNotExist(fopOutputSPOCPlain)

def getPseudoCodeAndCode(df):
    lstText=[]
    lstCode=[]
    for row_index, row in df_group.iterrows():
        strCode=str(row['code'])
        strText = str(row['text'])
        lstText.append(strText)
        indent=int(row['indent'])
        lstIndent=[]
        for i in range(0,indent):
            lstIndent.append('\t')
        strIndent=''.join(lstIndent)
        strCode=''.join([strIndent,strCode])
        lstCode.append(strCode)
    strTotalText='\n'.join(lstText)
    strTotalCode='\n'.join(lstCode)
    return strTotalText,strTotalCode



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
        strTotalText, strTotalCode=getPseudoCodeAndCode(df_group)
       # print('type {}'.format(df_group['workerid']))
      #  row0=df_group.itertuples()[0]
        workId=df_group['workerid'].iloc[0]
        probId=df_group['probid'].iloc[0]
        subId=df_group['subid'].iloc[0]
        fpPlainText='{}/{}_{}_{}_text.txt'.format(fopOutputSPOCPlain,workId,probId,subId)
        fpPlainCode = '{}/{}_{}_{}_code.txt'.format(fopOutputSPOCPlain, workId, probId, subId)
        fopNest=fopOutputSPOCNested+'/'+str(workId)+'/'+str(probId)+'/'+str(subId)+'/'
        createDirIfNotExist(fopNest)
        fpNestText = '{}/{}_{}_{}_text.txt'.format(fopNest, workId, probId, subId)
        fpNestCode = '{}/{}_{}_{}_code.txt'.format(fopNest, workId, probId, subId)

        fff=open(fpPlainText,'w')
        fff.write(strTotalText)
        fff.close()
        fff=open(fpPlainCode,'w')
        fff.write(strTotalCode)
        fff.close()
        fff=open(fpNestText,'w')
        fff.write(strTotalText)
        fff.close()
        fff=open(fpNestCode,'w')
        fff.write(strTotalCode)
        fff.close()
    except Exception as e:
        print('{}\n{}'.format(str(e),traceback.format_exc()))
    print('Index {}/{}'.format(index,lenGrouped))

