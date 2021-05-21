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

def textToJson(strText):
  try:
    output = nlp.annotate(text, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
    })
    jsonTemp = json.loads(output)
    strJsonObj = json.dumps(jsonTemp, indent=1)
    # print(type(jsonObject))
    # strTree = jsonTemp['sentences'][0]['parse']
    # tree2 = Tree.fromstring(strTree)
    # dictTree =tree2dict(tree2)
    # strJsonObj=json.dumps(dictTree,indent=1)
    # jsonObj=json.loads(strJsonObj)
  except:
    strJsonObj='Error'
  return strJsonObj

def printTree(jsonObj):

  if isinstance(jsonObj,list):
    for item in jsonObj:
      # print('go here')
      printTree(item)
  elif isinstance(jsonObj,str):
    print(jsonObj)
  else:
    keys = jsonObj.keys()
    if (len(keys)>0):
      for key in keys:
        print(key)
        printTree(jsonObj[key])


from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

text = "The old oak tree from India fell down. I love you."
# ss


jsonObject=textToJson(text)
print('{}'.format(jsonObject))
# printTree(jsonObject)

# jsonObj=json.dumps(jsonObject,indent=1)
# print(jsonObj)

# print('{}'.format(jsonObject['sentences'][0]['parse'])) # tagged output sentence