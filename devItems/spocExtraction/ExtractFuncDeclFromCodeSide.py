import glob
import sys, os
import operator
import clang.cindex

sys.path.append(os.path.abspath(os.path.join('..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from CASTWalker import  Walker

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolder=fopData+'textInSPOC/trainOnlyC/'
fpCombineASTs= fopTextInSPoC + 'combineASTs.txt'
fpSignatures= fopTextInSPoC + 'signatureFromCode.txt'

# lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.cpp"))

dictCountWords={}

f1=open(fpCombineASTs, 'r')
strCombineASTs=f1.read()
f1.close()
currentKey=''
dictASTs={}
arrCombineASTs=strCombineASTs.split('\n')
for i in range(0,len(arrCombineASTs)):
    strTrim=arrCombineASTs[i].strip()
    if strTrim.endswith('.cpp'):
        currentKey=strTrim
        listASTs=[]
        dictASTs[currentKey]=listASTs
        # print(currentKey)
    else:
        dictASTs[currentKey].append(arrCombineASTs[i])


print('finish listASTs {}'.format(len(dictASTs.keys())))

f1=open(fpSignatures, 'w')
f1.write('')
f1.close()

for key in dictASTs.keys():
    lstItemASTs=dictASTs[key]
    lstOutputItem = []
    for i in range(0,len(lstItemASTs)):
        strItem=lstItemASTs[i].strip()
        arrItem=strItem.split('\t')
        # print(strItem)
        if len(arrItem)>=3 and arrItem[1] == 'CursorKind.FUNCTION_DECL':
            strFuncInfo='{}\t{}'.format(arrItem[2],arrItem[0])
            lstOutputItem.append(strFuncInfo)


    strContentToAdd='\n'.join(lstOutputItem)
    strContentItem='\n'.join([key,strContentToAdd,'\n\n\n'])
    f1 = open(fpSignatures, 'a')
    f1.write(strContentItem)
    f1.close()

print('finish')







