from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from nltk.tokenize import word_tokenize
import os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.random_projection import GaussianRandomProjection
from sklearn.model_selection import cross_val_score, cross_val_predict, StratifiedKFold, train_test_split
import sys,os
print(os.path.abspath(os.path.join('../..')))
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist
import torch

#handling text data
from torchtext.legacy import data
# from torchtext.legacy.data import *

import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from numpy import unique
import sys,os
sys.path.append(os.path.abspath(os.path.join('../..')))
from UtilFunctions import createDirIfNotExist
import nltk
nltk.download('punkt')
import traceback
import torch.nn as nn

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

def putTextAndLabelToCSV(fpText,fpLabel,lstText,lstLbl,fpOut):
    f1=open(fpText,'r')
    arrText=f1.read().strip().split('\n')
    f1.close()
    f1 = open(fpLabel, 'r')
    arrLabel = f1.read().strip().split('\n')
    f1.close()

    lstStr = ['label,text']
    data=[]
    for i in range(0,len(arrText)):
        itemText=arrText[i].split('\t')[1].replace(',',' COMMA ')
        itemLabel=arrLabel[i].split('\t')[1].replace(',',' COMMA ')
        strItem='{},{}'.format(itemLabel,itemText)
        lstStr.append(strItem)
        tup=(itemText,itemLabel)
        data.append(tup)
        lstText.append(itemText)
        lstLbl.append(itemLabel)

    f1=open(fpOut,'w')
    f1.write('\n'.join(lstStr))
    f1.close()
    # df=pd.read_csv(fpOut,delimiter='\t')
    # print('lendf {}'.format(len(df)))
    return data

def putTextAndLabelInRange(lstTextAndLabels,startIndex,endIndex,fpOutP1,fpOutP2,fpOutP3):
    lstStrP1 = ['label,text']
    lstStrP2 = ['label,text']
    lstStrP3 = ['label,text']
    data=[]
    for i in range(startIndex,endIndex):
        objItem=lstTextAndLabels[i]
        itemText=objItem[3].replace(',',' COMMA ')
        itemLabelP1=objItem[0].replace(',',' COMMA ')
        itemLabelP2 = objItem[1].replace(',', ' COMMA ')
        itemLabelP3 = objItem[2].replace(',', ' COMMA ')
        strItemP1='{},{}'.format(itemLabelP1,itemText)
        strItemP2 = '{},{}'.format(itemLabelP2, itemText)
        strItemP3='{},{}'.format(itemLabelP3,itemText)
        lstStrP1.append(strItemP1)
        lstStrP2.append(strItemP2)
        lstStrP3.append(strItemP3)
        tup=(itemText,itemLabelP1,itemLabelP2,itemLabelP3)
        data.append(tup)
        print('handle {}'.format(i))
        # lstText.append(itemText)
        # lstLbl.append(itemLabel)

    f1=open(fpOutP1,'w')
    f1.write('\n'.join(lstStrP1))
    f1.close()
    f1=open(fpOutP2,'w')
    f1.write('\n'.join(lstStrP2))
    f1.close()
    f1=open(fpOutP3,'w')
    f1.write('\n'.join(lstStrP3))
    f1.close()
    # df=pd.read_csv(fpOut,delimiter='\t')
    # print('lendf {}'.format(len(df)))
    return data

def train(model, iterator, optimizer, criterion):
    # initialize every epoch
    epoch_loss = 0
    epoch_acc = 0

    # set the model in training phase
    model.train()

    for batch in iterator:
        # resets the gradients after every batch
        optimizer.zero_grad()

        # retrieve text and no. of words
        text, text_lengths = batch.text
        text_lengths=text_lengths.cpu()
        # print('text and length {}  AAA {}'.format(text_lengths,text))
        # convert to 1D tensor
        if(len(text_lengths)==0):
            continue
        predictions = model(text, text_lengths).squeeze()

        # compute the loss
        loss = criterion(predictions, batch.label)

        # compute the binary accuracy
        acc = multiclass_accuracy(predictions, batch.label)

        # backpropage the loss and compute the gradients
        loss.backward()

        # update the weights
        optimizer.step()

        # loss and accuracy
        epoch_loss += loss.item()
        epoch_acc += acc.item()

    return epoch_loss / len(iterator), epoch_acc / len(iterator)

def evaluate(model, iterator, criterion):
    # initialize every epoch
    epoch_loss = 0
    epoch_acc = 0

    # deactivating dropout layers
    model.eval()

    # deactivates autograd
    with torch.no_grad():
        for batch in iterator:
            # retrieve text and no. of words
            text, text_lengths = batch.text
            text_lengths = text_lengths.cpu()

            # convert to 1d tensor
            predictions = model(text, text_lengths).squeeze()

            # compute loss and accuracy
            loss = criterion(predictions, batch.label)
            acc = multiclass_accuracy(predictions, batch.label)

            # keep track of loss and accuracy
            epoch_loss += loss.item()
            epoch_acc += acc.item()

    return epoch_loss / len(iterator), epoch_acc / len(iterator)

class classifier(nn.Module):

    # define all the layers used in model
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim, n_layers,
                 bidirectional, dropout):
        # Constructor
        super().__init__()

        # embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)

        # lstm layer
        self.lstm = nn.LSTM(embedding_dim,
                            hidden_dim,
                            num_layers=n_layers,
                            bidirectional=bidirectional,
                            dropout=dropout,
                            batch_first=True)

        # dense layer
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

        # activation function
        self.act = nn.Sigmoid()

    def forward(self, text, text_lengths):
        # text = [batch size,sent_length]
        embedded = self.embedding(text)
        # embedded = [batch size, sent_len, emb dim]

        # packed sequence
        packed_embedded = nn.utils.rnn.pack_padded_sequence(embedded, text_lengths, batch_first=True)

        packed_output, (hidden, cell) = self.lstm(packed_embedded)
        # hidden = [batch size, num layers * num directions,hid dim]
        # cell = [batch size, num layers * num directions,hid dim]

        # concat the final forward and backward hidden state
        hidden = torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1)

        # hidden = [batch size, hid dim * num directions]
        dense_outputs = self.fc(hidden)

        # Final activation function
        outputs = self.act(dense_outputs)

        return outputs
import spacy
nlp = spacy.load('en_core_web_sm')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def predict(model, sentence):
    tokenized = [tok.text for tok in nlp.tokenizer(sentence)]  #tokenize the sentence
    indexed = [TEXT.vocab.stoi[t] for t in tokenized]          #convert to integer sequence
    length = [len(indexed)]                                    #compute no. of words
    tensor = torch.LongTensor(indexed).to(device)              #convert to tensor
    tensor = tensor.unsqueeze(1).T                             #reshape in form of batch,no. of words
    length_tensor = torch.LongTensor(length)                   #convert to tensor
    prediction = model(tensor, length_tensor)                  #prediction
    return prediction.item()

# define metric
def multiclass_accuracy(preds, y):
    # round predictions to the closest integer
    # torch.argmax(preds)
    # selectedIndex=preds.
    # print('preds {} lenPreds {}'.format(preds,type(preds)))
    # print('y {} lenY {}'.format(y, len(y)))
    # print('argmax_preds {} '.format(argmax_preds))
    argmax_preds=torch.argmax(preds, dim=1)
    # print('argmax_preds {} '.format(argmax_preds))

    correct = (argmax_preds == y).float()
    acc = correct.sum() / len(correct)
    return acc

# No. of trianable parameters
def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def trainAndEval(train_data,valid_data,test_data):
    from torchtext.vocab import Vectors
    vectors = Vectors(name='vectors_glove.txt', cache=fopRoot)
    TEXT.build_vocab(train_data, valid_data, test_data, vectors=vectors)
    LABEL.build_vocab(train_data, valid_data, test_data)
    #No. of unique tokens in text
    print("Size of TEXT vocabulary:",len(TEXT.vocab))
    #No. of unique tokens in label
    print("Size of LABEL vocabulary:",len(LABEL.vocab))
    #Commonly used words
    print(TEXT.vocab.freqs.most_common(10))
    #Word dictionary
    # print(TEXT.vocab.stoi)
    print(LABEL.vocab.itos)
    print(LABEL.vocab.stoi)
    num_classes=len(LABEL.vocab.itos)
    # input('label')
    #check whether cuda is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #set batch size
    BATCH_SIZE = 64
    #Load an iterator
    train_iterator, valid_iterator ,test_iterator= data.BucketIterator.splits(
        (train_data, valid_data,test_data),
        batch_size = BATCH_SIZE,
        sort_key = lambda x: len(x.text),
        sort_within_batch=True,
        device = device)




    #define hyperparameters
    size_of_vocab = len(TEXT.vocab)
    embedding_dim = 100
    num_hidden_nodes = 32
    num_output_nodes = num_classes
    num_layers = 2
    bidirection = True
    dropout = 0.2

    #instantiate the model
    model = classifier(size_of_vocab, embedding_dim, num_hidden_nodes,num_output_nodes, num_layers,
                       bidirectional = True, dropout = dropout)

    # architecture
    print(model)




    print(f'The model has {count_parameters(model):,} trainable parameters')
    # Initialize the pretrained embedding
    pretrained_embeddings = TEXT.vocab.vectors
    model.embedding.weight.data.copy_(pretrained_embeddings)

    print(pretrained_embeddings.shape)

    import torch.optim as optim

    # define optimizer and loss
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    # push to cuda if available
    model = model.to(device)
    criterion = criterion.to(device)
    N_EPOCHS = 30
    best_valid_loss = float('inf')
    for epoch in range(N_EPOCHS):
        # train the model
        train_loss, train_acc = train(model, train_iterator, optimizer, criterion)
        # evaluate the model
        valid_loss, valid_acc = evaluate(model, valid_iterator, criterion)
        # save the best model
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), fopRoot+'saved_weights.pt')
        print(f'Epoch: {epoch}\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc * 100:.2f}%')
        print(f'Epoch: {epoch}\t Val. Loss: {valid_loss:.3f} |  Val. Acc: {valid_acc * 100:.2f}%')
    #load weights
    path=fopOutputML+'/saved_weights.pt'
    model.load_state_dict(torch.load(path));
    model.eval();
    #inference
    import spacy
    nlp = spacy.load('en_core_web_sm')
    test_loss, test_acc = evaluate(model, test_iterator, criterion)
    # acc_prob1=test_acc
    print('test loss and test acc \n{}\t{}'.format(test_loss,test_acc))
    return test_acc
def trainAndEval(train_data,valid_data,test_data):
    from torchtext.vocab import Vectors
    vectors = Vectors(name='vectors_glove.txt', cache=fopRoot)
    TEXT.build_vocab(train_data, valid_data, test_data, vectors=vectors)
    LABEL.build_vocab(train_data, valid_data, test_data)
    #No. of unique tokens in text
    print("Size of TEXT vocabulary:",len(TEXT.vocab))
    #No. of unique tokens in label
    print("Size of LABEL vocabulary:",len(LABEL.vocab))
    #Commonly used words
    print(TEXT.vocab.freqs.most_common(10))
    #Word dictionary
    # print(TEXT.vocab.stoi)
    print(LABEL.vocab.itos)
    print(LABEL.vocab.stoi)
    num_classes=len(LABEL.vocab.itos)
    # input('label')
    #check whether cuda is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #set batch size
    BATCH_SIZE = 64
    #Load an iterator
    train_iterator, valid_iterator ,test_iterator= data.BucketIterator.splits(
        (train_data, valid_data,test_data),
        batch_size = BATCH_SIZE,
        sort_key = lambda x: len(x.text),
        sort_within_batch=True,
        device = device)




    #define hyperparameters
    size_of_vocab = len(TEXT.vocab)
    embedding_dim = 100
    num_hidden_nodes = 32
    num_output_nodes = num_classes
    num_layers = 2
    bidirection = True
    dropout = 0.2

    #instantiate the model
    model = classifier(size_of_vocab, embedding_dim, num_hidden_nodes,num_output_nodes, num_layers,
                       bidirectional = True, dropout = dropout)

    # architecture
    print(model)




    print(f'The model has {count_parameters(model):,} trainable parameters')
    # Initialize the pretrained embedding
    pretrained_embeddings = TEXT.vocab.vectors
    model.embedding.weight.data.copy_(pretrained_embeddings)

    print(pretrained_embeddings.shape)

    import torch.optim as optim

    # define optimizer and loss
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    # push to cuda if available
    model = model.to(device)
    criterion = criterion.to(device)
    N_EPOCHS = 30
    best_valid_loss = float('inf')
    for epoch in range(N_EPOCHS):
        # train the model
        train_loss, train_acc = train(model, train_iterator, optimizer, criterion)
        # evaluate the model
        valid_loss, valid_acc = evaluate(model, valid_iterator, criterion)
        # save the best model
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), fopOutputML+'saved_weights.pt')
        print(f'Epoch: {epoch}\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc * 100:.2f}%')
        print(f'Epoch: {epoch}\t Val. Loss: {valid_loss:.3f} |  Val. Acc: {valid_acc * 100:.2f}%')
    #load weights
    path=fopOutputML+'/saved_weights.pt'
    model.load_state_dict(torch.load(path));
    model.eval();
    #inference
    import spacy
    nlp = spacy.load('en_core_web_sm')
    test_loss, test_acc = evaluate(model, test_iterator, criterion)
    # acc_prob1=test_acc
    print('test loss and test acc \n{}\t{}'.format(test_loss,test_acc))
    return test_acc


fopRoot='../../../../../media/dataPapersExternal/mixCodeRaw/'
fpInputText=fopRoot+'embeddingModels/d2v/paragraph_text.txt'
fopOutputML=fopRoot+'resultMLs/rnn-lstm-small/'
fpResultDetails=fopOutputML+'result_details.txt'
fpDoc2VecModel=fopRoot+'embeddingModels/d2v/d2v.model.txt'
createDirIfNotExist(fopOutputML)

sys.stdout = open(fpResultDetails, 'w')


# fpTrain = fopRoot + 'train.csv'
# fpTextTrain = fopRoot + 'train.text.txt'
fpLabelP1Train = fopOutputML + 'train.label.p1.txt'
fpLabelP2Train = fopOutputML + 'train.label.p2.txt'
fpLabelP3Train = fopOutputML + 'train.label.p3.txt'

# fpValid = fopRoot + 'valid.csv'
# fpTextValid = fopRoot + 'testP.text.txt'
fpLabelP1Valid = fopOutputML + 'testP.label.p1.txt'
fpLabelP2Valid = fopOutputML + 'testP.label.p2.txt'
fpLabelP3Valid = fopOutputML + 'testP.label.p3.txt'

# fpTest = fopRoot + 'test.csv'
# fpTextTest = fopRoot + 'testW.text.txt'
fpLabelP1Test = fopOutputML + 'testW.label.p1.txt'
fpLabelP2Test = fopOutputML + 'testW.label.p2.txt'
fpLabelP3Test = fopOutputML + 'testW.label.p3.txt'
sys.stdout = open(fpResultDetails, 'w')
TEXT = data.Field(tokenize='spacy', batch_first=True, include_lengths=True)
LABEL = data.LabelField(dtype=torch.long, batch_first=True, use_vocab=True)
fields = [('label', LABEL), ('text', TEXT)]
# loading custom dataset p1
train_data = data.TabularDataset(path=fpLabelP1Train, format='csv', fields=fields, skip_header=True)
valid_data = data.TabularDataset(path=fpLabelP1Valid, format='csv', fields=fields, skip_header=True)
test_data = data.TabularDataset(path=fpLabelP1Test, format='csv', fields=fields, skip_header=True)
acc_p1=trainAndEval(train_data,valid_data,test_data)

TEXT = data.Field(tokenize='spacy', batch_first=True, include_lengths=True)
LABEL = data.LabelField(dtype=torch.long, batch_first=True, use_vocab=True)
fields = [('label', LABEL), ('text', TEXT)]
# loading custom dataset p2
train_data = data.TabularDataset(path=fpLabelP2Train, format='csv', fields=fields, skip_header=True)
valid_data = data.TabularDataset(path=fpLabelP2Valid, format='csv', fields=fields, skip_header=True)
test_data = data.TabularDataset(path=fpLabelP2Test, format='csv', fields=fields, skip_header=True)
acc_p2=trainAndEval(train_data,valid_data,test_data)

TEXT = data.Field(tokenize='spacy', batch_first=True, include_lengths=True)
LABEL = data.LabelField(dtype=torch.long, batch_first=True, use_vocab=True)
fields = [('label', LABEL), ('text', TEXT)]
# loading custom dataset p1
train_data = data.TabularDataset(path=fpLabelP3Train, format='csv', fields=fields, skip_header=True)
valid_data = data.TabularDataset(path=fpLabelP3Valid, format='csv', fields=fields, skip_header=True)
test_data = data.TabularDataset(path=fpLabelP3Test, format='csv', fields=fields, skip_header=True)
acc_p3=trainAndEval(train_data,valid_data,test_data)
print('\n\nP1\t{}\nP2\t{}\nP3\t{}'.format(acc_p1,acc_p2,acc_p3))
sys.stdout.close()
sys.stdout = sys.__stdout__

print('Done')