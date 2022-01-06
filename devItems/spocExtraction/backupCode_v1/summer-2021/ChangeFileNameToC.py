import glob
import sys, os
import operator

sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText

fopData='../../../dataPapers/'
fopTextInSPoC=fopData+'textInSPOC/'
fopTrainFolder=fopTextInSPoC+'trainSPOCPlain/'
fopTrainFolderOnlyC=fopTextInSPoC+'trainOnlyC/'
lstFiles=sorted(glob.glob(fopTrainFolder+ "*_code.txt"))
createDirIfNotExist(fopTrainFolderOnlyC)
for i in range(0,len(lstFiles)):
    f1=open(lstFiles[i],'r')
    print(lstFiles[i])
    fileName=os.path.basename(lstFiles[i])
    newFileName=fileName.replace('.txt','.cpp')
    fpOutpurItem=fopTrainFolderOnlyC+newFileName
    strContent=f1.read()
    f1.close()
    lstHeaders=['#include <iostream>','#include<stdio.h>',
'#include <string.h>',
'#include<stdlib.h>',
'#include<math.h>',
'#include<time.h>',
'#include<ctype.h>',
'#include<assert.h>',
'#include<locale.h>',
'#include<signal.h>',
'#include<setjmp.h>',
'#include<stdarg.h>',
'#include<errno.h>',
'#include<iomanip>',
'#include <algorithm>',
'#include <vector>',
'#include <limits.h>',
'#include <map>',
                '#include <set>','#include <list>','#include <stack>','#include <queue>','#include <array>','#include <unordered_map>',
                '#include <unordered_set>','#include <deque>','#include <forward_list>']
    strHeader='\n'.join(lstHeaders)
    strCommand='int XX_MARKER_XX = 123234;\n'
    strNewContent='\n'.join([strHeader,'\n','using namespace std;\n',strCommand,strContent])
    f1=open(fpOutpurItem,'w')
    f1.write(strNewContent)
    f1.close()

print('done')

