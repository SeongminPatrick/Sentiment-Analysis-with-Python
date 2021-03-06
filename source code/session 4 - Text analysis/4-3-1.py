import gensim
from gensim.models import Doc2Vec

import numpy as np
from random import shuffle
from sklearn.linear_model import LogisticRegression

from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

import multiprocessing
import os

stop_words = set(stopwords.words('english'))
lemm = WordNetLemmatizer()

LabeledSentence = gensim.models.doc2vec.LabeledSentence

class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
       self.labels_list = labels_list
       self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield LabeledSentence(words=str(doc).split(),tags=[self.labels_list[idx]])

review_list = []
labels_list = []

files = os.listdir('aclImdb/train/pos')[:1000]
for file in files:
    review = ''
    with open('aclImdb/train/pos/{}'.format(file), 'r', encoding = 'utf-8') as f:
        for word in word_tokenize(f.read()):
            if lemm.lemmatize(word) not in stop_words:
                review += ' ' + word
        f.close()
    review_list.append(review)
    labels_list.append('pos_' + file)

files = os.listdir('aclImdb/train/neg')[:1000]
for file in files:
    review = ''
    with open('aclImdb/train/neg/{}'.format(file), 'r', encoding = 'utf-8') as f:
        for word in word_tokenize(f.read()):
            if lemm.lemmatize(word) not in stop_words:
                review += ' ' + word
        f.close()
    review_list.append(review)
    labels_list.append('neg_' + file)

files = os.listdir('aclImdb/test/pos')[:1000]
for file in files:
    review = ''
    with open('aclImdb/test/pos/{}'.format(file), 'r', encoding = 'utf-8') as f:
        for word in word_tokenize(f.read()):
            if lemm.lemmatize(word) not in stop_words:
                review += ' ' + word
        f.close()
    review_list.append(review)
    labels_list.append('pos_' + file)

files = os.listdir('aclImdb/test/neg')[:1000]
for file in files:
    review = ''
    with open('aclImdb/test/neg/{}'.format(file), 'r', encoding = 'utf-8') as f:
        for word in word_tokenize(f.read()):
            if lemm.lemmatize(word) not in stop_words:
                review += ' ' + word
        f.close()
    review_list.append(review)
    labels_list.append('neg_' + file)

it = LabeledLineSentence(doc_list = review_list, labels_list = labels_list)

model = Doc2Vec(size = 3000, window = 10, dm = 0, alpha=0.025, min_alpha=0.025, min_count=5, workers = multiprocessing.cpu_count())

model.build_vocab(it)
model.train(it, total_examples = 4000, epochs = 20)

model.save('partial_Doc2Vec.model')

model = Doc2Vec.load('partial_Doc2Vec.model')

x_train = np.zeros((2000, 3000))
y_train = np.zeros(2000)

files = os.listdir('aclImdb/train/pos')[:1000]
for i in range(1000):
    x_train[i] = model.docvecs['pos_' + files[i]]
    y_train[i] = 1

files = os.listdir('aclImdb/train/neg')[:1000]
for i in range(1000):
    x_train[i+1000] = model.docvecs['neg_' + files[i]]
    y_train[i+1000] = 0

x_test = np.zeros((2000, 3000))
y_test = np.zeros(2000)

files = os.listdir('aclImdb/test/pos')[:1000]
for i in range(1000):
    x_test[i] = model.docvecs['pos_' + files[i]]
    y_test[i] = 1

files = os.listdir('aclImdb/test/neg')[:1000]
for i in range(1000):
    x_test[i+1000] = model.docvecs['neg_' + files[i]]
    y_test[i+1000] = 0

clf = LogisticRegression()
clf.fit(x_train, y_train)

print(clf.score(x_test, y_test))