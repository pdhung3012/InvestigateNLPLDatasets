import operator;
import csv;
import pandas as pd;
import sys, os
import traceback
import operator
sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist

fopDataFolder='/home/hung/git/dataPapers/'
fopInputSPOCData=fopDataFolder+'/SPOCDataset/spoc/'
fopTrainTestSplit=fopDataFolder + '/parallelCorpus/'
fopOutputTrainSPOCNested= fopDataFolder + '/outputTrainSPOCNested/'
fopOutputTrainSPOCPlain= fopDataFolder + '/outputTrainSPOCPlain/'
fopOutputEvalSPOCNested= fopDataFolder + '/outputEvalSPOCNested/'
fopOutputEvalSPOCPlain= fopDataFolder + '/outputEvalSPOCPlain/'
fopOutputTestSPOCNested= fopDataFolder + '/outputTestSPOCNested/'
fopOutputTestSPOCPlain= fopDataFolder + '/outputTestSPOCPlain/'

fpOutputTrainText=fopTrainTestSplit+'train.s'
fpOutputTrainCode=fopTrainTestSplit+'train.t'
fpOutputEvalText=fopTrainTestSplit+'valid.s'
fpOutputEvalCode=fopTrainTestSplit+'valid.t'
fpOutputTestText=fopTrainTestSplit+'test.s'
fpOutputTestCode=fopTrainTestSplit+'test.t'


fpTrainData=fopInputSPOCData+'train/split/spoc-train-train.tsv'
fpTestData=fopInputSPOCData+'train/split/spoc-train-test.tsv'
fpEvalData=fopInputSPOCData+'train/split/spoc-train-eval.tsv'


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
    return strTotalText,strTotalCode,strTotalLine,lstText,lstCode


def createTrainTestSplitData(fpData,fopNest,fopPlain,fpSource,fpTarget):
    createDirIfNotExist(fopPlain)
    createDirIfNotExist(fopNest)

    tsv_file = open(fpData)
    df = pd.read_csv(tsv_file, delimiter="\t")
    df_grouped=df.groupby(['subid','probid','workerid'])
    # iterate over each group
    index=0
    lenGrouped=len(df_grouped)
    lstTotalText=[]
    lstTotalCode=[]
    for group_name, df_group in df_grouped:

        #print('\nCREATE TABLE {}('.format(group_name))
        #print('aaa {} {}'.format(type(df_group),group_name))
        index=index+1
        try:
            strTotalText, strTotalCode,strTotalLine,lstText,lstCode=getPseudoCodeAndCode(df_group)
            for item in lstText:
                lstTotalText.append(item)
            for item in lstCode:
                lstTotalCode.append(item)
           # print('type {}'.format(df_group['workerid']))
          #  row0=df_group.itertuples()[0]
            workId=df_group['workerid'].iloc[0]
            probId=df_group['probid'].iloc[0]
            subId=df_group['subid'].iloc[0]
            fpPlainText='{}/{}_{}_{}_text.txt'.format(fopPlain, workId, probId, subId)
            fpPlainCode = '{}/{}_{}_{}_code.txt'.format(fopPlain, workId, probId, subId)
            fpPlainLine = '{}/{}_{}_{}_line.txt'.format(fopPlain, workId, probId, subId)
            fopInsideNest= fopNest + '/' + str(workId) + '/' + str(probId) + '/' + str(subId) + '/'
            createDirIfNotExist(fopInsideNest)
            fpNestText = '{}/{}_{}_{}_text.txt'.format(fopInsideNest, workId, probId, subId)
            fpNestCode = '{}/{}_{}_{}_code.txt'.format(fopInsideNest, workId, probId, subId)
            fpNestLine = '{}/{}_{}_{}_line.txt'.format(fopInsideNest, workId, probId, subId)

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

    fff = open(fpSource, 'w')
    fff.write('\n'.join(lstTotalText))
    fff.close()
    fff = open(fpTarget, 'w')
    fff.write('\n'.join(lstTotalCode))
    fff.close()

createDirIfNotExist(fopTrainTestSplit)
createTrainTestSplitData(fpTrainData,fopOutputTrainSPOCNested,fopOutputTrainSPOCPlain,fpOutputTrainText,fpOutputTrainCode)
createTrainTestSplitData(fpEvalData,fopOutputEvalSPOCNested,fopOutputEvalSPOCPlain,fpOutputEvalText,fpOutputEvalCode)
createTrainTestSplitData(fpTestData,fopOutputTestSPOCNested,fopOutputTestSPOCPlain,fpOutputTestText,fpOutputTestCode)

