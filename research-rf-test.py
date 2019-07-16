#!/usr/bin/env python3


import pandas as pd
import numpy as np
import os,sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.preprocessing import OneHotEncoder
from sklearn.externals import joblib

np.random.seed(0)  # for reproducibility

filename = 'featured-v4-HS300-2010-2016.csv'
model_filename = 'randomforest_model.sav'


#load data
df = pd.read_csv(filename)

df.rename(columns={"Unnamed: 0":"date"}, inplace=True)
df = df.drop(columns=['money','high','open','low','close','median',\
                    'ma5','ma10','ma60','volume',\
                    'hash_close','p_close'])

df['action'] = df.action.fillna(0)
df = df.dropna()

# convert value
df.loc[df[df.action=='buy'].index,'action'] = 1
df.loc[df[df.action=='sell'].index,'action'] = 2

df.loc[df[df.trend=='up'].index,'trend'] = 1
df.loc[df[df.trend=='down'].index,'trend'] = 0

df = df[df.action==0]

Y = df['action']
X = df.drop(columns=['date','security','action'])

X_test = X
Y_test = Y

clf = joblib.load(model_filename)

res = clf.predict(X_test)


res_df = pd.DataFrame()
res_df['actual'] = Y_test
res_df['predict'] = res
res_df['error'] = 1
res_df.loc[res_df[res_df.actual==res_df.predict].index,'error'] = 0

errors = 0
v_count = res_df['error'].value_counts()
if 1 in v_count:
	errors = v_count[1]

score = clf.score(X_test, Y_test)

# print(res_df[res_df.predict==1])

print(res_df['error'].value_counts())
print("-"*100)
print('Score',score)
print('Error rate: ', str(round(errors/len(res_df)*100,2))+'%')
print('Test Samples: ',len(res_df))
print("-"*100)
print("\n")