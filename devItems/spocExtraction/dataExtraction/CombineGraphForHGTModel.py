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

fopRoot='/home/hungphd/media/dataPapersExternal/mixCodeRaw/'
fopMixVersion=fopRoot+'step4_mixCode/'
fpFileCachedVersion=fopRoot+'cached_graph_all.txt'

lstFpVersionFiles=[]
if not os.path.isfile(fpFileCachedVersion):
    print('before traverse')
    lstFop1=sorted(glob.glob(fopMixVersion+'*/'))
    for fop1 in lstFop1:
        lstFop2=sorted(glob.glob(fop1+'*/'))
        for fop2 in lstFop2:
            lstFp3=sorted(glob.glob(fop2+'v_*_graphs/g_all.dot'))
            # print(fp3)
            for fp3 in lstFp3:
                lstFpVersionFiles.append(fp3)
        print('end {}'.format(fop1))
    # sorted(glob.glob(fopMixVersion+'**/**/a_json.txt'))
    print('after {} '.format(len(lstFpVersionFiles)))
    f1=open(fpFileCachedVersion,'w')
    f1.write('\n'.join(lstFpVersionFiles))
    f1.close()
else:
    f1 = open(fpFileCachedVersion, 'r')
    lstFpVersionFiles=f1.read().strip().split('\n')
    f1.close()
distanceHeader=33

