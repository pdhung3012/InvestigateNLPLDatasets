import os
import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from numpy import unique
import nltk


def createDirIfNotExist(fopOutput):
    try:
        # Create target Directory
        os.makedirs(fopOutput, exist_ok=True)
        #print("Directory ", fopOutput, " Created ")
    except FileExistsError:
        print("Directory ", fopOutput, " already exists")


def initDefaultTextEnvi():
    nlp_model = spacy.load('en_core_web_sm')
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return nlp_model,nlp

def getSentences(text,nlp):
    result=None
    try:
        document = nlp(text)
        result= [sent.string.strip() for sent in document.sents]
    except Exception as e:
        print('sone error occured {}'.format(str(e)))
    return result


def preprocess(textInLine):
    text = textInLine.lower()
    doc = word_tokenize(text)
    # doc = [word for word in doc if word in words]
    # doc = [word for word in doc if word.isalpha()]
    return ' '.join(doc)

# Python program to illustrate the intersection
# of two lists in most simple way
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
def diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def getPOSInfo(strContent):
    tokens=word_tokenize(strContent)
    poses=nltk.pos_tag(tokens)
    return poses


def writeDictToFileText(dictParam,fpFile):
    lstStr=[]
    for key in dictParam.keys():
        strItem=key+'\t'+str(dictParam[key])
        lstStr.append(strItem)

    strContent='\n'.join(lstStr)
    fFile=open(fpFile,'w')
    fFile.write(strContent)
    fFile.close()
def writeDictToFile(dictNum,dictText,fpNum,fpText):
    lstStr=[]
    lstStr2 = []
    for key in dictNum.keys():
        strItem=key+'\t'+str(dictNum[key])
        strList=sorted(unique(dictText[key]))
        strItem2=key+'\t'+','.join(strList)

        lstStr.append(strItem)
        lstStr2.append(strItem2)
    strContent='\n'.join(lstStr)
    fFile=open(fpNum,'w')
    fFile.write(strContent)
    fFile.close()
    strContent = '\n'.join(lstStr2)
    fFile = open(fpText, 'w')
    fFile.write(strContent)
    fFile.close()
