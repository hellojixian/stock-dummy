#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os,sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.preprocessing import OneHotEncoder
from sklearn.externals import joblib

np.random.seed(0)  # for reproducibility
np.set_printoptions(threshold=sys.maxsize)

model_filename = 'test/randomforest_model.sav'

print('loading data')
fullset=False

if fullset==True:
    X_file = "test/train_full_X.csv"
    Y_file = "test/train_full_Y.csv"
    s_rate = 1
else:
    X_file = "test/train_X.csv"
    Y_file = "test/train_Y.csv"
    s_rate = 1

print("Reading X data")
X = pd.read_csv(X_file, index_col=0).values

print("Reading Y data")
Y = pd.read_csv(Y_file, index_col=0).values

print(X.shape,Y.shape)
print(Y[0])


split_ratio = int(X.shape[0] * s_rate)
X= X[0:split_ratio]
Y= Y[0:split_ratio]

model_saved = "test/t1_weights.h5"
split_ratio = int(X.shape[0] * 0.8)
X_train= X[0:split_ratio]
Y_train= Y[0:split_ratio]
X_test = X[split_ratio:]
Y_test = Y[split_ratio:]


Y_test = pd.DataFrame(Y_test)
X_test = pd.DataFrame(X_test)


Y_test = Y_test[(Y_test[0]==1)]
X_test = X_test.loc[Y_test.index]


X_test = X_test.values
Y_test = Y_test.values

clf = RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini',
            max_depth=None, max_features=None, max_leaf_nodes=None,
            min_impurity_split=1e-08, min_samples_leaf=1,
            min_samples_split=2, min_weight_fraction_leaf=0,
            n_estimators=100, n_jobs=1, oob_score=True, random_state=0,
            verbose=0, warm_start=True)

clf.fit(X_train, Y_train)
joblib.dump(clf, model_filename)



res = clf.predict(X_test)
# print(res)

print("-"*100)
print('train score',clf.score(X_train, Y_train))
print('test score',clf.score(X_test, Y_test))
print("-"*100)
print("\n")
