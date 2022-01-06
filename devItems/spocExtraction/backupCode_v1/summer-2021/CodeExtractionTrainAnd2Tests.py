import operator;
import csv;
import pandas as pd;
import sys, os
import traceback
import operator
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist

fopDataFolder='/Users/hungphan/git/dataPapers/'
fopInputSPOCData=fopDataFolder+'/SPOCDataset/spoc/'
fopTrainSPOCNested= fopDataFolder + '/trainSPOCNest/'
fopTrainSPOCPlain= fopDataFolder + '/trainSPOCPlain/'
fpTrainData=fopInputSPOCData+'train/spoc-train.tsv'

fopTestPSPOCNested= fopDataFolder + '/testPSPOCNest/'
fopTestPSPOCPlain= fopDataFolder + '/testPSPOCPlain/'
fpTestPData=fopInputSPOCData+'test/spoc-testp.tsv'

fopTestWSPOCNested= fopDataFolder + '/testWSPOCNest/'
fopTestWSPOCPlain= fopDataFolder + '/testWSPOCPlain/'
fpTestWData=fopInputSPOCData+'test/spoc-testw.tsv'


createDirIfNotExist(fopTrainSPOCNested)
createDirIfNotExist(fopTrainSPOCPlain)
createDirIfNotExist(fopTestPSPOCNested)
createDirIfNotExist(fopTestPSPOCPlain)
createDirIfNotExist(fopTestWSPOCNested)
createDirIfNotExist(fopTestWSPOCPlain)

def getPseudoCodeAndCode(df):
    lstText=[]
    lstCode=[]
    lstLine=[]
    for row_index, row in df.iterrows():
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


def extractTextFiles(fpData,fopSPOCPlain,fopSPOCNested):
    tsv_file = open(fpData)
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
            fpPlainText='{}/{}_{}_{}_text.txt'.format(fopSPOCPlain, workId, probId, subId)
            fpPlainCode = '{}/{}_{}_{}_code.txt'.format(fopSPOCPlain, workId, probId, subId)
            fpPlainLine = '{}/{}_{}_{}_line.txt'.format(fopSPOCPlain, workId, probId, subId)
            fopNest= fopSPOCNested + '/' + str(workId) + '/' + str(probId) + '/' + str(subId) + '/'
            createDirIfNotExist(fopNest)
            fpNestText = '{}/{}_{}_{}_text.txt'.format(fopNest, workId, probId, subId)
            fpNestCode = '{}/{}_{}_{}_code.txt'.format(fopNest, workId, probId, subId)
            fpNestLine = '{}/{}_{}_{}_line.txt'.format(fopNest, workId, probId, subId)

            fff=open(fpPlainText,'w')
            fff.write(strTotalText)
            fff.close()
            fff=open(fpPlainCode,'w')
            fff.write(strTotalCode)
            fff.close()
            fff=open(fpPlainLine,'w')
            fff.write(strTotalLine)
            fff.close()
            fff=open(fpNestText,'w')
            fff.write(strTotalText)
            fff.close()
            fff=open(fpNestCode,'w')
            fff.write(strTotalCode)
            fff.close()
            fff=open(fpNestLine,'w')
            fff.write(strTotalLine)
            fff.close()
        except Exception as e:
            print('{}\n{}'.format(str(e),traceback.format_exc()))
        print('Index {}/{}'.format(index,lenGrouped))

extractTextFiles(fpTrainData,fopTrainSPOCPlain,fopTrainSPOCNested)
extractTextFiles(fpTestPData,fopTestPSPOCPlain,fopTestPSPOCNested)
extractTextFiles(fpTestWData,fopTestWSPOCPlain,fopTestWSPOCNested)