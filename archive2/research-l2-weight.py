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

def get_dist_report(knowledge, dataset, ranges):
    factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
    df = get_subset_slice(knowledge, dataset)

    total_count = df.shape[0]
    rs_wr = df[df.fu_c1>=0].shape[0]/total_count

    report = pd.DataFrame()

    for factor in ranges.index:
        record = pd.Series()
        slices = ranges.loc[factor]
        filters = []
        filter = "rs[(rs.{}<={})]".format(factor,slices[0])
        filters.extend([filter])

        for i in range(len(slices)):
            if i+1>=len(slices): break
            filter = "rs[(rs.{}>{}) & (rs.{}<={})]".format(factor,slices[i],factor,slices[i+1])
            filters.extend([filter])
        filter = "rs[(rs.{}>{})]".format(factor,slices[len(slices)-1])
        filters.extend([filter])

        for i in range(len(filters)):
            filter = filters[i]
            rs = df
            rs = eval(filter)
            if rs.shape[0]==0:
                wr = 0.5
            else:
                wr = rs[rs.fu_c1>=0].shape[0]/rs.shape[0]

            hr = rs.shape[0]/total_count
            # score = wr*hr
            score = wr
            record['{:d}'.format(i+1)] = score

        record.name = factor
        report = report.append(record)

    report = report[np.sort(report.columns.astype('i').to_list()).astype(str)]
    return report,rs_wr,total_count

def get_factor_ranges(knowledge, dataset, slice):
    factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
    df = get_subset_slice(knowledge, dataset)
    ranges = pd.DataFrame()
    slice -=1
    for factor in factors:
        record = pd.Series(np.zeros(slice))
        min = df[factor].quantile(0.05)
        max = df[factor].quantile(0.95)
        record[:] = np.linspace(min, max, slice)
        record.name = factor
        ranges = ranges.append(record)
    return ranges

def get_subset_slice(knowledge, dataset):
    rs = dataset
    factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
    df = eval(_compile_filter(factors, knowledge))
    return df

def get_sample_weight(sample,weight_matrix):
    # 判断当前样本命中在哪个区间内
    w = 0
    for factor in weight_matrix['ranges'].index:
        value = sample[factor]
        w_i = None
        if value < weight_matrix['ranges'].loc[factor][0]:
            w_i = 0
        else:
            for i in range(len(weight_matrix['ranges'].columns)):
                if i+1 >= len(weight_matrix['ranges'].columns):
                     w_i = len(weight_matrix['ranges'].columns)
                     break
                if value > weight_matrix['ranges'].loc[factor].iloc[i] and \
                    value < weight_matrix['ranges'].loc[factor].iloc[i+1]:
                    w_i = i
                    break
        factor_weight = weight_matrix['base_weights'].loc[factor].iloc[w_i]
        w += (factor_weight * w_i/20)
    return w

if knowledge_id is None:
    k = kb.sample(1).iloc[0]
else:
    k = kb.loc[knowledge_id]

k = kb.iloc[15]
knowledge = k['knowledge']
train_subset = get_subset_slice(knowledge, train_set)

# train_subset = train_subset[(train_subset.open_c>1) & (train_subset.open_c<2)]
# print(train_subset[['open_c','fu_c1']])
# print(train_subset.shape)

# sys.exit()
ranges = get_factor_ranges(knowledge, train_subset, slice)
train_report,train_wr,train_count = get_dist_report(knowledge, train_subset, ranges)
val_report,val_wr,val_count = get_dist_report(knowledge, validation_set, ranges)

#计算每个样本的权重
weight_matrix = {"ranges":ranges,
                 "base_weights":train_report}

print(train_set.shape[0], train_subset.shape[0])

train_subset.loc[:,'weight'] = 0

train_subset = train_set.sample(200)
# train_subset['weight'] = train_subset.apply(func=get_sample_weight,args=[weight_matrix],axis=1)
for i in range(train_subset.shape[0]):
    sample = train_subset.iloc[i]
    train_subset.loc[train_subset.iloc[i].name,'weight'] = get_sample_weight(sample, weight_matrix)
    print("\rid:{}, progress: {:.2f}% of {}\t\t".format(i, round(i/train_subset.shape[0]*100,2), train_subset.shape[0]),end="")
print("")

train_subset = train_subset.sort_values(by=["weight"],ascending=False)
# train_set = train_set[["fu_c1","weight"]]
train_subset.to_csv("train_subset.csv")

print("Done")

df = pd.read_csv("train_subset.csv", index_col=0)
df = df.sort_values(by=['weight'],ascending=False)
df['weight'] = np.round(df['weight'],2)

df = df[['fu_c1','weight']]
total = df.shape[0]
df_full = df
win_r = df[df.fu_c1>=0].shape[0] / df.shape[0]
print('full_wr',win_r)

df = df[:100]
win_r = df[df.fu_c1>=0].shape[0] / df.shape[0]
print(df.shape[0], total)
print(win_r)
print(df_full)
