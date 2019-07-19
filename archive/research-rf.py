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

print('loading data')
#load data
df = pd.read_csv('update_'+filename)

df.rename(columns={"Unnamed: 0":"date"}, inplace=True)
# df = df.drop(columns=['money','high','open','low','close','median',\
#                     'ma5','ma10','ma60','volume',\
#                     'hash_close','p_close'])

# df = df.drop(columns=['future_c1','future_c2','future_c3','future_c4'])
print('data loaded')

# df['action'] = df.action.fillna(0)
df = df.dropna()
# print('start converting data')

# # convert value
# df.loc[df[df.action=='buy'].index,'action'] = 1
# df.loc[df[df.action=='sell'].index,'action'] = 2

# df.loc[df[df.trend=='up'].index,'trend'] = 1
# df.loc[df[df.trend=='down'].index,'trend'] = 0

# print('start cutting data')

# for i in range(len(df)-2):
# 	idx = int(len(df) - i)
# 	if df['action'].iloc[idx-1]!=0:
# 		df.loc[df.iloc[idx].name,'action']  = df['action'].iloc[(idx-1)]	

# df.to_csv('update_'+filename)

sample_count = min(len(df[df.action==1]),len(df[df.action==2]))


ds_buy  = df[df.action==1].sample(sample_count)
ds_sell = df[df.action==2].sample(round(sample_count*0.5))
ds_hold = df[df.action==0].sample(round(sample_count*0.8))

df = pd.DataFrame()
df = ds_buy.append(ds_sell)
df = df.append(ds_hold)
df = shuffle(df)

print(df['action'].value_counts())

Y = df['action']
X = df.drop(columns=['date','action'])

spliter = round(len(X)*0.8)
X_train, X_test = X[:spliter], X[spliter:]
Y_train, Y_test = Y[:spliter], Y[spliter:]

clf = RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini',
            max_depth=None, max_features=None, max_leaf_nodes=None,
            min_impurity_split=1e-08, min_samples_leaf=1,
            min_samples_split=15, min_weight_fraction_leaf=0,
            n_estimators=60, n_jobs=1, oob_score=True, random_state=0,
            verbose=1, warm_start=True)

clf.fit(X_train, Y_train)
joblib.dump(clf, model_filename)



res = clf.predict(X_test)
# predict = pd.Series(res,name='predict')

res_df = pd.DataFrame()
res_df['actual'] = Y_test
res_df['predict'] = res
res_df['error'] = 1
res_df = res_df[res_df.predict==1]
# 
res_df.loc[res_df[res_df.actual==res_df.predict].index,'error'] = 0

print(res_df[res_df.error==1])

errors = 0
v_count = res_df['error'].value_counts()
if 1 in v_count:
	errors = v_count[1]

print(res_df['error'].value_counts())
print("-"*100)
print('train score',clf.score(X_train, Y_train))
print('test score',clf.score(X_test, Y_test))
print('Error rate: ', str(round(errors/len(res_df)*100,2))+'%')
print('Test Samples: ',len(res_df))
print("-"*100)
print("\n")