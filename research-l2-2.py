#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will visualize the win/lose data distributions
"""
import pandas as pd
import numpy as np
import warnings,sys,os
import json, pprint
import time
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation

KB_FILENAME = 'data/knowledge_base.h5'
KB_KEY = 'KnowledgeBase'

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print("Loading local knowledge base...\t\t")
kb = pd.read_hdf(KB_FILENAME, key=KB_KEY)
kb = kb.sort_values(by=['win_r'],ascending=False)


try: slice = int(sys.argv[1])
except: slice=20

try: knowledge_id = sys.argv[2]
except: knowledge_id = None

def _compile_filter(factors, knowledge):
    filter = "rs["
    for _ in range(len(factors)):
        factor = factors[_]
        filter += " (rs.{:s} < {}) & (rs.{:s} > {}) & ".format(factor,knowledge[factor+"_u"],
                                                            factor,knowledge[factor+"_d"])
    filter += "True ]"
    return filter

data_source = {
    'train':'data/featured-v7.1-HS300-2006-2016.csv',
    'validation':'data/featured-v7.1-HS300-2017-2018.csv'}

print('Loading dataset ...')

train_set = pd.read_csv(data_source['train'], index_col=0)
validation_set = pd.read_csv(data_source['validation'], index_col=0)

def convert_dataset(dataset, slice):
    factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values

    X = np.zeros(shape=(dataset.shape[0],len(factors),slice))

    for i in range(len(factors)):
        factor = factors[i]
        record = pd.Series(np.zeros(slice))
        min = dataset[factor].quantile(0.02)
        max = dataset[factor].quantile(0.98)
        if factor=='up_l': min, max = -3, 0
        if factor=='dn_l': min, max = 0,3
        dataset.loc[:,factor] = np.ceil(((dataset[factor].values-min) / (max-min)) * slice-1)
        dataset.loc[:,factor] = np.clip(dataset.loc[:,factor], 0, slice-1)
        X[:,i] = np.eye(slice)[dataset[factor].values.astype('i')]

    y_type = 3
    Y = np.zeros(shape=(dataset.shape[0],y_type))
    dataset['Y'] = 0
    dataset.loc[dataset.fu_c1>2,'Y'] = 1
    dataset.loc[dataset.fu_c1<-2,'Y'] = 2
    Y = np.eye(y_type)[dataset['Y'].values.astype('i')]
    return X,Y

def get_subset_slice(knowledge, dataset):
    rs = dataset
    factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
    df = eval(_compile_filter(factors, knowledge))
    return df


if knowledge_id is None:
    k = kb.sample(1).iloc[0]
else:
    k = kb.loc[knowledge_id]

k = kb.iloc[15]
knowledge = k['knowledge']
# crop the sample
train_subset = get_subset_slice(knowledge, train_set)
# convert sample to one-hot matrix and save it
X, Y = convert_dataset(train_subset, slice)
X = X.reshape(X.shape[0],X.shape[1]*X.shape[2])
print(X.shape, Y.shape)
train_X = pd.DataFrame(X)
train_Y = pd.DataFrame(Y)

# train_set = train_set[["fu_c1","weight"]]
# train_X.to_csv("test/train_full_X.csv")
# train_Y.to_csv("test/train_full_Y.csv")
train_X.to_csv("test/train_X.csv")
train_Y.to_csv("test/train_Y.csv")
print("Done")
