import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText
from tree_sitter import Language, Parser
import pygraphviz as pgv
import pylab,traceback
from pyparsing import OneOrMore, nestedExpr
import  gzip,json
import ast


def getJsonData(fopInput,fopOutput):
    try:
        lstFopJsonGz=sorted(glob.glob(fopInput+'*.jsonl.gz'))
        print('len {}'.format(len(lstFopJsonGz)))
        lstProjectNameAndSHA=[]
        for i in range(0,len(lstFopJsonGz)):
            fpJsonlGz=lstFopJsonGz[i]
            print('begin {}'.format(fpJsonlGz))
            fpExtractex=fpJsonlGz.replace('.gz','')
            try:
                partName=os.path.basename(fpJsonlGz)
                nameWithoutExtension=partName.replace('.jsonl.gz','')
                # fopItemPath=fopOutput+partName+'/'
                # createDirIfNotExist(fopItemPath)
                with gzip.open(fpJsonlGz, "r") as f:
                    data = f.read()
                with open(fpExtractex, 'w') as json_file:
                    json.dump(data.decode('utf-8'), json_file)

                with open(fpExtractex, "r") as read_it:
                    association_data = json.load(read_it)
                    # print(type(association_data))
                    # print(association_data)
                    arrJsons=association_data.strip().split('\n')
                    lstDocStrings=[]
                    lstCodes = []
                    lstLocations = []
                    lstRepos = []
                    for j in range(0,len(arrJsons)):
                        try:
                            itemJson = arrJsons[j]
                            # jsonObject = ast.literal_eval(arrJsons[j])
                            jsonObject = json.loads(itemJson)
                            # print(jsonObject)
                            strDocString=' '.join(jsonObject['docstring_tokens']).replace('\n',' ENDLINE ').replace('\t',' TABCHAR ')
                            strCode=jsonObject['code'].replace('\n',' ENDLINE ').replace('\t',' TABCHAR ')
                            strLocation='{}\t{}'.format(jsonObject['path'].replace('\n',' ENDLINE ').replace('\t',' TABCHAR '),jsonObject['func_name'].replace('\n',' ENDLINE ').replace('\t',' TABCHAR '))
                            strRepo='{}\t{}\t{}'.format(jsonObject['repo'].replace('\n',' ENDLINE ').replace('\t',' TABCHAR '),jsonObject['sha'].replace('\n',' ENDLINE ').replace('\t',' TABCHAR '),jsonObject['url'].replace('\n',' ENDLINE ').replace('\t',' TABCHAR '))
                            strRepoCompact = '{}\t{}'.format(
                                jsonObject['repo'].replace('\n', ' ENDLINE ').replace('\t', ' TABCHAR '),
                                jsonObject['sha'].replace('\n', ' ENDLINE ').replace('\t', ' TABCHAR '))
                            lstDocStrings.append(strDocString)
                            lstCodes.append(strCode)
                            lstLocations.append(strLocation)
                            lstRepos.append(strRepo)
                            lstProjectNameAndSHA.append(strRepoCompact)
                        except:
                            traceback.print_exc()
                    fpCommentPart=fopOutput+nameWithoutExtension+'_comment.txt'
                    fpCodePart = fopOutput + nameWithoutExtension + '_code.txt'
                    fpLocationPart = fopOutput + nameWithoutExtension + '_location.txt'
                    fpRepoPart=fopOutput+nameWithoutExtension+'_repo.txt'

                    f1=open(fpCommentPart,'w')
                    f1.write('\n'.join(lstDocStrings))
                    f1.close()
                    f1 = open(fpCodePart, 'w')
                    f1.write('\n'.join(lstCodes))
                    f1.close()
                    f1 = open(fpLocationPart, 'w')
                    f1.write('\n'.join(lstLocations))
                    f1.close()
                    f1 = open(fpRepoPart, 'w')
                    f1.write('\n'.join(lstRepos))
                    f1.close()

            except:
                traceback.print_exc()
            fpRepoDict = fopOutput +  '0a_dict_repo.txt'
            lstProjectNameAndSHA=sorted(list(set(lstProjectNameAndSHA)))
            f1=open(fpRepoDict,'w')
            f1.write('\n'.join(lstProjectNameAndSHA))
            f1.close()
            print('end len json {} total repos {}'.format(len(arrJsons),len(lstProjectNameAndSHA)))
    except:
        traceback.print_exc()

fopLocalDataPapers='../../../../dataPapers/'
fopExternalDataPapers='/home/hungphd/media/dataPapersExternal/'
fopDataCSN=fopExternalDataPapers+'data_CSN/'
fopExtractedJson=fopExternalDataPapers+'extractedJson_CSN/'

fopSubPath='/final/jsonl/'
lstLanguages=['java','python','go','php','javascript','ruby']
lstFolderNames=['train','valid','test']
lstFopInput=[]
lstFopOutput=[]

for i in range(0,len(lstLanguages)):
    for j in range(0,len(lstFolderNames)):
        lstFopInput.append(fopDataCSN+lstLanguages[i]+'/'+fopSubPath+'/'+lstFolderNames[j]+'/')
        lstFopOutput.append(fopExtractedJson+lstLanguages[i]+'/'+fopSubPath+'/'+lstFolderNames[j]+'/')

for i in range(0,len(lstFopInput)):
    getJsonData(lstFopInput[i],lstFopOutput[i])



