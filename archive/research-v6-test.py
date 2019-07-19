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


print('loading data')
#load data
df = pd.read_csv(filename)
print(len(df))
df.rename(columns={"Unnamed: 0":"date"}, inplace=True)

df['openjump'] = round((df['open'] - df['close'].shift(periods=1)) / df['close'].shift(periods=1),4)
df['downline'] = round((df['open'] - df['low']) / df['close'].shift(periods=1),4)
df['upline'] = round((df['high'] - df['open']) / df['close'].shift(periods=1),4)


df = df.drop(columns=['money','high','open','low','close','median',\
                    'ma5','ma10','ma60','volume',\
                    'hash_close','p_close','action','security'])



# df = df.drop(columns=['future_c1','future_c2','future_c3','future_c4'])
print('data loaded')

# df['action'] = df.action.fillna(0)
df = df.dropna()
df['action'] = 0


# ----------------------------------------------------------------------------------------------------
# [Parallel(n_jobs=1)]: Done  10 out of  10 | elapsed:    0.0s finished
# train score 0.969982219433
# [Parallel(n_jobs=1)]: Done  10 out of  10 | elapsed:    0.0s finished
# test score 0.959419885651
# Error rate:  7.57%
# Test Samples:  3830
# ----------------------------------------------------------------------------------------------------
df.loc[df.future_c1>0.01,'action']=1
df.loc[df.prev_c1>=0.00,'action']=0
df.loc[df.prev_c2>=0.00,'action']=0

df.loc[df[df.trend=='up'].index,'trend'] = 1
df.loc[df[df.trend=='down'].index,'trend'] = 0


# sample_count = 20000
print(df.head(5))

df = df.loc[df.prev_c1<0.00]
df = df.loc[df.prev_c2<0.00]
df = df.loc[df.today_c<0.00]

df = shuffle(df)

print('Test buy action:',len(df[df.action==1]))
print(df['action'].value_counts())

Y = df['action']
X = df.drop(columns=['date','action','future_c1','future_c2','future_c3','future_c4'])

print(X.head(10))

print('Test buy action:',len(df[df.action==1]))


X_test = X
Y_test = Y

clf_61 = joblib.load('randomforest_model-v6.1.sav')
clf_62 = joblib.load('randomforest_model-v6.2.sav')

res_61 = clf_61.predict(X_test)
res_62 = clf_62.predict(X_test)


res_df = pd.DataFrame()
res_df['actual'] = Y_test
res_df['predict_61'] = res_61
res_df['predict_62'] = res_62
res_df['error'] = 0

score61 = clf_61.score(X_test, Y_test)
score62 = clf_62.score(X_test, Y_test)

print("-"*100)
print('Score 61: ',score61)
print('Score 62: ',score62)
total = len(res_df)

print('checking result')
res_df = res_df[res_df.predict_62==res_df.predict_61]
res_df = res_df[res_df.predict_61==1]
res_df.loc[res_df[res_df.actual!=res_df.predict_61].index,'error'] = 1


errors = 0
v_count = res_df['error'].value_counts()
if 1 in v_count:
	errors = v_count[1]


# print(res_df[res_df.predict==1])

print(res_df['error'].value_counts())
print('Buy Action: ',len(res_df[res_df.predict_62==1]))
print('Error rate: ', str(round(errors/len(res_df)*100,2))+'%')
print('Test Samples: ',total)
print("-"*100)
print("\n")