from nltk.parse import stanford
from nltk.tree import Tree
import json
import os
import sys
# os.environ['STANFORD_PARSER'] = '../../../dataPapers/StanfordParser/stanford-parser-full-2020-11-17'
# os.environ['STANFORD_MODELS'] = '../../../dataPapers/StanfordParser/stanford-parser-full-2020-11-17'

fopStanfordCoreNLP='../../../dataPapers/stanford-corenlp-4.2.2/'

# sp = stanford.StanfordParser()
#
# # def tree_to_dict(tree):
# #     tdict = {}
# #     for t in tree:
# #         if isinstance(t, Tree) and isinstance(t[0], Tree):
# #             tdict[t.node] = tree_to_dict(t)
# #         elif isinstance(t, Tree):
# #             tdict[t.node] = t[0]
# #     return tdict
# #
# # def dict_to_json(dict):
# #     return json.dumps(dict)
#
# def getTree(treeObj,index,lstTreeInfos):
#     lstIndent=[]
#     for i in range(0,index):
#         lstIndent.append('\t')
#     print(treeObj)
#     lstIndent.append(treeObj)
#     strInfo=''.format(lstIndent)
#     lstTreeInfos.append(strInfo)
#     for item in treeObj.leaves():
#         indexItem=index+1
#         getTree(item,indexItem,lstTreeInfos)
#
#
#
# trees = [tree for tree in sp.parse("this is a sentence . \n Hello how are you?".split())]
# tree=trees[0]
# # output_json = dict_to_json({tree.node: tree_to_dict(tree)})
#
# # print('{}\n{}\naaa'.format(type(trees[0]),trees[0]))
# # print('json: {}'.format(output_json))
# lstTreeInfos=[]
# index=0
# # print(tree.pretty_print())
# getTree(trees[0],index,lstTreeInfos)
# strInfo='\n'.join(lstTreeInfos)
# print(strInfo)

def tree2dict(tree):
  return {tree.label(): [tree2dict(t) if isinstance(t, Tree) else t
                      for t in tree]}

def printIndent(numIndent):
  lstStr=[]
  for i in range(0,numIndent):
    lstStr.append('\t')
  return ''.join(lstStr)


def textToJson(strText):
  try:
    output = nlp.annotate(text, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
    })
    jsonTemp = json.loads(output)
    strJsonObj = jsonTemp
    # json.dumps(jsonTemp, indent=1)
    # print(type(jsonObject))
    # strTree = jsonTemp['sentences'][0]['parse']
    # tree2 = Tree.fromstring(strTree)
    # dictTree =tree2dict(tree2)
    # strJsonObj=json.dumps(dictTree,indent=1)
    # jsonObj=json.loads(strJsonObj)
  except:
    strJsonObj='Error'
  return strJsonObj

def printTree(jsonObj,index):
  if isinstance(jsonObj,list):
    # print(str(type(jsonObj)))
    strIndent = printIndent(index)
    strLine = '{}{}'.format(strIndent, jsonObj.label())
    print(strLine)
    for item in jsonObj:
      # print('go here {} {}'.format(type(item),item.label()))
      index=index+1
      # strIndent = printIndent(index)
      # strLine = '{}{}'.format(strIndent, item.label())
      # print(strLine)
      printTree(item,index)
  elif isinstance(jsonObj,str):
    strIndent=printIndent(index)
    strLine='{}{}'.format(strIndent,jsonObj)
    print(strLine)
  else:
    print('go here')
    strIndent=printIndent(index)
    strLine='{}{}'.format(strIndent,jsonObj.label())
    print(strLine)
  # else:
  #   keys = jsonObj.keys()
  #   print('{}'.format(keys))
  #   if (len(keys)>0):
  #     for key in keys:
  #       index = index + 1
  #       strIndent = printIndent(index)
  #       strLine = '{}{}'.format(strIndent, key)
  #       print(strLine)
  #       printTree(jsonObj[key])

def getListOfDependency(jsonDep):
  lstDeps=[]
  for dep in jsonDep:
    strDep='Dep name: {}: {} --> {}'.format(dep['dep'],dep['governorGloss'],dep['dependentGloss'])
    lstDeps.append(strDep)
    # print(strDep)
  return lstDeps

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

text = "Let bal be character array with length 110 ."



jsonRoot=textToJson(text)
# jsonObject=json.loads(jsonObject)
print(jsonRoot)
jsonObject=jsonRoot['sentences'][0]['parse']
jsonDependency=jsonRoot['sentences'][0]['basicDependencies']
tree=Tree.fromstring(jsonObject)
# print('{}'.format(jsonObject))
printTree(tree,0)
lstDeps=getListOfDependency(jsonDependency)
print('\n'.join(lstDeps))

# jsonObj=json.dumps(jsonObject,indent=1)
# print(jsonObj)

# print('{}'.format(jsonObject['sentences'][0]['parse'])) # tagged output sentence