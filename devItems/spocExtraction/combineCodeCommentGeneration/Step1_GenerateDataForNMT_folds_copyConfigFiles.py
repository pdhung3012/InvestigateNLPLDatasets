import glob
import sys, os
import operator,traceback
import shutil
import json
sys.path.append(os.path.abspath(os.path.join('../..')))
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
fopInputStep2Pseudocode=fopRoot+'step2_pseudo_tokenize/'
fopInputStep2ReplaceDict=fopRoot+'step2_code_replaceDict/'
fopInputStep2BeforeTranslation=fopRoot+'step2_beforeTranslation/step1/'
fopInputStep2Folds=fopRoot+'step2_beforeTranslation/folds/'
fpFold1Yaml=fopInputStep2Folds+'config-fold-1.yaml'
fpFold1Sh=fopInputStep2Folds+'config-fold-1-run.sh'

f1=open(fpFold1Yaml,'r')
strFold1Yaml=f1.read()
f1.close()

f1=open(fpFold1Sh,'r')
strFold1Sh=f1.read()
f1.close()

for i in range(3,11):
    fpYaml=fopInputStep2Folds+'config-fold-{}.yaml'.format(i)
    fpSh=fopInputStep2Folds+'config-fold-{}-run.sh'.format(i)
    strYaml=strFold1Yaml.replace('fold-1','fold-{}'.format(i))
    strSh=strFold1Sh.replace('fold-1','fold-{}'.format(i))
    f1=open(fpYaml,'w')
    f1.write(strYaml)
    f1.close()
    f1 = open(fpSh, 'w')
    f1.write(strSh)
    f1.close()
















