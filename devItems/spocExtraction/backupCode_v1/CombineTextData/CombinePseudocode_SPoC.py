from UtilFunctions import *
import glob

fopPseudocode='/home/hungphd/media/dataPapersExternal/mixCodeRaw/step2_pseudo_tokenize/'
fopOutput='/home/hungphd/media/dataPapersExternal/mixCodeRaw/genPseudocode/'
createDirIfNotExist(fopOutput)
fpAllPseudoCode=fopOutput+'pseudocode_all.txt'
lstFpPseudos=sorted(glob.glob(fopPseudocode+'/**/*_text.txt'))
print('len {}'.format(len(lstFpPseudos)))
f1=open(fpAllPseudoCode,'w')
f1.write('')
f1.close()
index=0
for fpItem in lstFpPseudos:
    index=index+1
    f1=open(fpItem,'r')
    strItem=f1.read()
    f1.close()

    f1 = open(fpAllPseudoCode, 'a')
    f1.write(strItem+'\n')
    f1.close()
    print('{} {}'.format(index,fpItem))
