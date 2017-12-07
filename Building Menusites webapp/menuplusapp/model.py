from collections import Counter
from menusights_aux import *
import cPickle as pickle
from sklearn.linear_model import LogisticRegression
import numpy as np
from nltk.stem.snowball import SnowballStemmer
import nltk
from sklearn.feature_extraction.text import CountVectorizer
import os
cwd = os.getcwd()

model = pickle.load(open(str(cwd + "/menuplusapp/logress.pkl"), "rb"))
vectorizer = pickle.load(open(str(cwd + "/menuplusapp/vect.pkl"), "rb"))

stopwords = nltk.corpus.stopwords.words('english')
stemmer = SnowballStemmer("english")

def tokenize_and_stem(title):
    stemmer = SnowballStemmer("english")
    stemmed_titles = []
    new_title=[]
    for word in nltk.word_tokenize(title):
        new_title.append(stemmer.stem(word))
    stemmed_titles.extend(new_title)
    return " ".join([i for i in stemmed_titles])

def report_score_and_why(menuitem, vectorizer=vectorizer, model=model):
    input_vectorized = vectorizer.transform([tokenize_and_stem(menuitem)])
    if input_vectorized.nnz > 0:
        #print(tokenize_and_stem(menuitem))
        #print(input_vectorized.shape)
        #Need to change this to inputting model
        p = model.predict_proba(input_vectorized)[0]
        q = zip(model.classes_, list(p))
        classification = model.predict(input_vectorized)[0]
        probability = dict(q)[classification]
        # Figure out why: list individual score contribution of each word
        matchwords = [i for i in input_vectorized.todok().keys( )] #todok = to dict of keys
        explaindict = {}
        ranklist = []
        for i in matchwords:
            w = vectorizer.get_feature_names()[i[1]] #gets actual word of feature, by matrix index
            coef = zip(model.classes_, model.coef_[:,i[1]])
            ranklist.append((w, dict(coef)["vhigh"]))
            explaindict[w] = dict(coef)
        # Figure out the biggest contributor:
        ranklist = sorted(ranklist, key=lambda a: a[1])
    else:
        classification = "unknown"
        probability = 0
        explaindict = {"unscorable": "yes"}
        ranklist = ["unscorable", "unscorable"]
        
    return classification, probability, explaindict, ranklist[-1][0]