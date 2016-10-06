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
    #print(tokenize_and_stem(menuitem))
    #print(input_vectorized.shape)
    #Need to change this to inputting model
    classification = model.predict(input_vectorized)[0]
#    probability = dict(zip(model.classes_, list(model.predict_proba(vect)[0])))
#     why = list(np.array(vectorizer.get_feature_names())[informative_words]).index("shrimp")
    return classification