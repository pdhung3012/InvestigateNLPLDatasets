import glob
import sys, os
import operator
import clang.cindex
from nltk.parse import stanford
from nltk.tree import Tree
import json
import os
import sys,traceback
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')


sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText,runASTGenAndSeeResult

def textToJson(strText):
  try:
    output = nlp.annotate(strText, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
    })
    # print(str(output))
    # jsonTemp = json.loads(output)
    strJsonObj = json.dumps(output, indent=1)
  except:
    # strResult = str(sys.exc_info()[0])
    print("Exception in user code:")
    print("-" * 60)
    traceback.print_exc(file=sys.stdout)
    print("-" * 60)
    strJsonObj='Error'
  return strJsonObj




def genGraph(fpPseudoCode,fopGraph):
    createDirIfNotExist(fopGraph)
    f1=open(fpPseudoCode)
    strPseudoCodes=f1.read()
    f1.close()
    dictPseudoCodes={}
    arrPseudoCodes=strPseudoCodes.split('\n')
    for i in range(0,len(arrPseudoCodes)):
        strTrim=arrPseudoCodes[i].strip()
        if strTrim.endswith('_text.txt'):
            currentKey=strTrim
            lstPseudoCodes=[]
            dictPseudoCodes[currentKey]=lstPseudoCodes
            # print(currentKey)
        else:
            dictPseudoCodes[currentKey].append(arrPseudoCodes[i])
    index=0
    for key in dictPseudoCodes.keys():
        index=index+1
        pseudoCodeName=key.replace('_text.txt','')
        lstPseudoCodes=dictPseudoCodes[key]
        strPseudo='\n'.join(lstPseudoCodes).strip().replace('.',' PUNC_CHAR ')
        strPseudo =strPseudo.replace('\n',' . ')
        # lstPseudoCodes='\n'.join(lstPseudoCodes).strip().split('\n')
        fpItemPseudoCode=fopGraph+pseudoCodeName+'_graphNL.txt'
        # createDirIfNotExist(fopItemPseudoCode)
        print('{}\t{}'.format(index,fpItemPseudoCode))
        strJson = textToJson(strPseudo)
        f1 = open(fpItemPseudoCode, 'w')
        f1.write(strJson)
        f1.close()
        # for i in range(0,len(lstPseudoCodes)):
        #     strI=str(i+1)+'.txt'
        #     strJson=textToJson(lstPseudoCodes[i].strip())
        #     fpI=fopItemPseudoCode+strI
        #
        #     f1=open(fpI,'w')
        #     f1.write(strJson)
        #     f1.close()
fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fpPseudoCodeTestP= fopTextInSPoC + 'combinePseudoCode_TestP.txt'
fopNLGraphTestP=fopTextInSPoC+'nlGraphInSPOC_TestP/'
fpPseudoCodeTestW= fopTextInSPoC + 'combinePseudoCode_TestW.txt'
fopNLGraphTestW=fopTextInSPoC+'nlGraphInSPOC_TestW/'
fpPseudoCode= fopTextInSPoC + 'combinePseudoCode.txt'
fopNLGraph=fopTextInSPoC+'nlGraphInSPOC/'

genGraph(fpPseudoCodeTestP,fopNLGraphTestP)
genGraph(fpPseudoCodeTestW,fopNLGraphTestW)
genGraph(fpPseudoCode,fopNLGraph)

print('finish')
