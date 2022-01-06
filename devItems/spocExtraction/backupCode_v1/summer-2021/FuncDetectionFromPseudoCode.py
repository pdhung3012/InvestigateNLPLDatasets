import glob
import sys, os
import operator
import clang.cindex

sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from CASTWalker import  Walker

fopData='/Users/hungphan/git/dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopStatisticFolder=fopData+'textInSPOC/trainOnlyC/'
fpCombineASTs= fopTextInSPoC + 'combineASTs.txt'
fpCombinePseudoCodes= fopTextInSPoC + 'combinePseudoCode.txt'
fpCombineCodes= fopTextInSPoC + 'combineCode.txt'

fpFunDeclInPseudoCode= fopTextInSPoC + 'signatureFromPseudoCode.txt'

# lstFiles=sorted(glob.glob(fopStatisticFolder+ "*_code.cpp"))

dictCountWords={}

currentKey=''
dictASTs={}
dictPseudoCodes={}

# f1=open(fpCombineASTs, 'r')
# strCombineASTs=f1.read()
# f1.close()
# arrCombineASTs=strCombineASTs.split('\n')
# for i in range(0,len(arrCombineASTs)):
#     strTrim=arrCombineASTs[i].strip()
#     if strTrim.endswith('.cpp'):
#         currentKey=strTrim
#         listASTs=[]
#         dictASTs[currentKey]=listASTs
#         # print(currentKey)
#     else:
#         dictASTs[currentKey].append(arrCombineASTs[i])
# print('finish listASTs {}'.format(len(dictASTs.keys())))

f1=open(fpCombinePseudoCodes, 'r')
strCombinePseudoCodes=f1.read()
f1.close()
arrCombinePseudoCodes=strCombinePseudoCodes.split('\n')
for i in range(0,len(arrCombinePseudoCodes)):
    strTrim=arrCombinePseudoCodes[i].strip()
    if strTrim.endswith('.cpp'):
        currentKey=strTrim
        listPseudoCodes=[]
        dictPseudoCodes[currentKey]=listPseudoCodes
        # print(currentKey)
    else:
        dictPseudoCodes[currentKey].append(arrCombinePseudoCodes[i])
print('finish listPseudoCodes {}'.format(len(dictPseudoCodes.keys())))




f1=open(fpFunDeclInPseudoCode, 'w')
f1.write('')
f1.close()

for key in dictPseudoCodes.keys():
    lstItemPseudoCodes=dictPseudoCodes[key]
    strContentToPseudoCode='\n'.join(lstItemPseudoCodes).strip()
    lstItemPseudoCodes=strContentToPseudoCode.split('\n')

print('finish')







