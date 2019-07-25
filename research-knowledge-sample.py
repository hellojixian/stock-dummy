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

def _compile_filter(factors):
    filter = "rs["
    for _ in range(len(factors)):
        factor = factors[_]
        filter += " (rs."+factor+" < dna['"+factor+"_u']) & (rs."+factor+" > dna['"+factor+"_d']) & "
    filter += "True ]"
    return filter

data_source = {
    'train':'data/featured-v7.1-HS300-2006-2016.csv',
    'validation':'data/featured-v7.1-HS300-2017-2018.csv'}

print('Loading dataset ...')

train_set = pd.read_csv(data_source['train'], index_col=0)
validation_set = pd.read_csv(data_source['validation'], index_col=0)

def get_dist_report(knowledge, df, ranges):
    rs = df
    dna = knowledge

    total_count = rs.shape[0]
    rs_wr = rs[rs.fu_c1>=0].shape[0]/total_count

    scopes = np.linspace(0,rs.shape[0],slice+1,dtype='int')
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
                wr = 0
            else:
                wr = rs[rs.fu_c1>0].shape[0]/rs.shape[0]
            record['{:d}'.format(i+1)] = round(wr*100,2)

        record.name = factor
        report = report.append(record)

    report = report[np.sort(report.columns.astype('i').to_list()).astype(str)]
    return report,rs_wr,total_count

def get_factor_ranges(dataset, slice):
    df = dataset
    factors = df.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
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


if knowledge_id is None:
    k = kb.sample(1).iloc[0]
else:
    k = kb.loc[knowledge_id]

print(k.name)
knowledge = k['knowledge']
ranges = get_factor_ranges(train_set, slice)
train_report,train_wr,train_count = get_dist_report(knowledge, train_set, ranges)
val_report,val_wr,val_count = get_dist_report(knowledge, validation_set, ranges)
vmin,vmax=np.quantile(train_report.values,0.01),np.quantile(train_report.values,0.99)

# 可视化 WR 的标准化
fig =plt.figure(figsize=(16,6))
ax1 =fig.add_subplot(121)
ax2 =fig.add_subplot(122)
sns.heatmap(train_report,
            ax=ax1, cmap='RdYlGn_r',
            linewidths=0.05, annot=False,
            cbar=False, cbar_kws=dict(ticks=np.linspace(vmin,vmax,10)),
            vmin=vmin, vmax=vmax)
ax1.set_ylabel("features")
ax1.set_xlabel("slices")
ax1.set_title("Train   WR:{:.1f}%  Samples:{:.1f}K".format(train_wr*100,train_count/1000))

sns.heatmap(val_report,
            ax=ax2, cmap='RdYlGn_r',
            linewidths=0.05, annot=False,
            cbar=False, cbar_kws=dict(ticks=np.linspace(vmin,vmax,10)),
            vmin=vmin, vmax=vmax)
ax2.set_ylabel("features")
ax2.set_xlabel("slices")
ax2.set_title("Validation   WR:{:.1f}%  Samples:{:.1f}K".format(val_wr*100,val_count/1000))
fig.suptitle("K: {} Slices: {:d}".format(k.name, slice))

plt.show()
