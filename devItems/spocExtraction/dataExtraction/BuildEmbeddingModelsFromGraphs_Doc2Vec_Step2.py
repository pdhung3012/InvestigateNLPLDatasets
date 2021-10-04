import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('..')))
import asyncio
import time
from joblib import Parallel,delayed
from UtilFunctions_RTX3090 import createDirIfNotExist,getPOSInfo,writeDictToFileText
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

import ast
import re
import pygraphviz as pgv
import pydot
from subprocess import check_call
from graphviz import render
import copy
import nltk
from pathlib import Path
nltk.download('punkt')

# create training vector for token: code and text

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopPOSModel=fopRoot+'embeddingModels/d2v/'
fpDictLiterals=fopRoot+'step2_dictLiterals_all.txt'
fopMixVersion=fopRoot+'step4_mixCode/'
fpFileCachedVersion=fopRoot+'cached_fp_mixAndVersion.txt'
fpJsonPseudoAfterPOS=fopRoot+'pseudocode_after_pos.txt'
fpCachedPOS=fopPOSModel+'cached_pos.txt'
fpCachedPseudocode=fopPOSModel+'cached_pseudocode.txt'
fpCachedCode=fopPOSModel+'cached_code.txt'
fpCachedAST=fopPOSModel+'cached_ast.txt'
fpD2VModel=fopPOSModel+'d2v.model.txt'
fpParagraphText=fopPOSModel+'paragraph_text.txt'
fpParagraphEmb=fopPOSModel+'paragraph_emb.txt'
fpTokenText=fopPOSModel+'token_text.txt'
fpTokenEmb=fopPOSModel+'token_emb.txt'

print('before traverse')
lstFpJsonFiles=[]
if not os.path.isfile(fpFileCachedVersion):
    lstFop1=sorted(glob.glob(fopMixVersion+'*/'))
    for fop1 in lstFop1:
        lstFop2=sorted(glob.glob(fop1+'*/'))
        for fop2 in lstFop2:
            lstFop3=sorted(glob.glob(fop2+'v_*_label.txt'))
            # print(fp3)
            for fp3 in lstFop3:
                lstFpJsonFiles.append(fp3)
        print('end {}'.format(fop1))
    # sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
    print('after {} '.format(len(lstFpJsonFiles)))
    f1=open(fpFileCachedVersion,'w')
    f1.write('\n'.join(lstFpJsonFiles))
    f1.close()
else:
    f1=open(fpFileCachedVersion,'r')
    lstFpJsonFiles=f1.read().split('\n')
    f1.close()


f1=open(fpDictLiterals,'r')
arrLits=f1.read().strip().split('\n')
f1.close()
dictLiteralsToValues={}
dictValuesToLiterals={}
for item in arrLits:
    arrTabs=item.split('\t')
    if len(arrTabs)>=2:
        strContent='\t'.join(arrTabs[1:])
        dictLiteralsToValues[arrTabs[0]]=strContent
        dictValuesToLiterals[strContent]=arrTabs[0]

lstDictLiteralKey=sorted(dictValuesToLiterals,reverse=True)
lstProgramText=[]

if not os.path.isfile(fpParagraphText):
    f1=open(fpParagraphText,'w')
    f1.write('')
    f1.close()
    for i in range(0,len(lstFpJsonFiles)):
        try:
            fpItem=lstFpJsonFiles[i]
            fnVersionLabel=os.path.basename(fpItem)
            versionName=fnVersionLabel.replace('_label.txt','')
            fopItemProgram=str(Path(fpItem).parent)
            programName=os.path.basename(fopItemProgram)
            fopItemProgram=fopItemProgram+'/'
            fpItemMixCppCode=fopItemProgram+versionName+'_mix.cpp'
            fpItemLabel=fpItem
        #     get pseudotext

            f1=open(fpItemLabel,'r')
            arrLabels=f1.read().split('\n')
            f1.close()
            strPseudoText=''
            if len(arrLabels)>=10:
                strPseudoText=arrLabels[8].replace('// ', '', 1).strip()

            f1=open(fpItemMixCppCode,'r')
            arrMixCodes=f1.read().split('\n')
            f1.close()

            lstStrItemCode = []
            for j in range(33, len(arrMixCodes)):
                item = arrMixCodes[j]
                for key in lstDictLiteralKey:
                    if key in item:
                        valKey = dictValuesToLiterals[key]
                        item = item.replace(key, valKey)
                lstStrItemCode.append(item)
            strCodeText = ' '.join(lstStrItemCode)
            str2LineToAdd='{}\t{}\t{}\tProgramRoot\t{}\n{}\t{}\t{}\tNLRoot\t{}'.format(fpItemLabel,programName,versionName,strPseudoText,fpItemLabel,programName,versionName,strCodeText)
            lstProgramText.append(str2LineToAdd)
            if (i+1)%1000==0 or (i+1)==len(lstFpJsonFiles):
                f1=open(fpParagraphText,'a')
                f1.write('\n'.join(lstProgramText)+'\n')
                f1.close()
                lstProgramText=[]
        except:
            traceback.print_exc()

modelD2v=Doc2Vec.load(fpD2VModel)
f1=open(fpParagraphText,'r')
arrParagraphText=f1.read().strip().split('\n')
f1.close()
lstEmbeddings=[]
indexPara=0
for i in range(0,len(arrParagraphText)):
    arrTabs=arrParagraphText[i].split('\t')
    if len(arrTabs)>=4:
        strContent=arrTabs[3:]
        vectorItem=modelD2v.infer_vector(word_tokenize(strContent))
        strItem='{}\t{}\t{}\t{}'.format(arrTabs[0],arrTabs[1],arrTabs[2],' '.join(map(str,vectorItem)))
        lstEmbeddings.append(strItem)
    if len(lstEmbeddings)%1000==0 or (i+1)==len(arrParagraphText):
        f1=open(fpParagraphEmb,'a')
        f1.write('\n'.join(lstEmbeddings)+'\n')
        f1.close()

print('End embedding paaragraaphs')

f1=open(fpCachedPseudocode,'r')
arrOutPseudocode=f1.read().split('\n')
f1.close()
f1=open(fpCachedCode,'r')
arrOutCode=f1.read().split('\n')
f1.close()
f1=open(fpCachedAST,'r')
arrOutAST=f1.read().split('\n')
f1.close()
f1=open(fpCachedPOS,'r')
arrOutPOS=f1.read().split('\n')
f1.close()

indexWords=0
lstWordEmbds=[]
lstWordText=[]
lstAllInputTexts=arrOutPseudocode+arrOutCode+arrOutPOS+arrOutPOS

f1=open(fpTokenEmb,'w')
f1.write('')
f1.close()


for i in range(0,len(lstAllInputTexts)):
    arrWordsInLines=lstAllInputTexts[i].split()
    for j in range(0,len(arrWordsInLines)):
        itemWord=arrWordsInLines[j]
        vectorItem = modelD2v.infer_vector(word_tokenize(itemWord))
        strVector=' '.join(map(str,vectorItem))
        strAddLine='{}\t{}'.format(itemWord,s,strVector)
        lstWordEmbds.append(strAddLine)
        lstWordText.append(itemWord)
    if len(lstWordEmbds)%1000==0 or (i+1)==len(arrWordsInLines):
        f1=open(fpTokenEmb,'a')
        f1.write('\n'.join(lstWordEmbds)+'\n')
        f1.close()

lstWordText=sorted(lstWordText)
f1=open(fpTokenText,'w')
f1.write('\n'.join(lstWordText))
f1.close()

print('len all text {}'.format(len(lstAllInputTexts)))






# for item: generaate vector of text and code