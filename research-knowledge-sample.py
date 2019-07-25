#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will visualize the win/lose data distributions
"""
import pandas as pd
import numpy as np
import warnings,sys,os
import json, pprint

KB_FILENAME = 'data/knowledge_base.h5'
KB_KEY = 'KnowledgeBase'


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print("Loading local knowledge base...\t\t")
kb = pd.read_hdf(KB_FILENAME, key=KB_KEY)
kb = kb.sort_values(by=['win_r'],ascending=False)


try:
    dataset = sys.argv[1]
    slice = int(sys.argv[2])
except:
    slice=20
    dataset= 'validation'

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

def get_dist_report(knowledge, df, slice):
    rs = df
    dna = knowledge
    factors = df.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values

    rs = eval(_compile_filter(factors))
    total_count = rs.shape[0]
    rs_wr = rs[rs.fu_c1>=0].shape[0]/total_count

    scopes = np.linspace(0,rs.shape[0],slice+1,dtype='int')
    report = pd.DataFrame()
    for factor in factors:
        rs = rs.sort_values(by=[factor],ascending=True)
        record = pd.Series()
        for i in range(slice):
            df = rs.iloc[scopes[i]:scopes[i+1]]
            wr = df[df.fu_c1>0].shape[0]/df.shape[0]
            record['slice_{:.0f}'.format((i)/slice*100)] = round(wr*100,2)
        cond = 'asc'
        record.name="{}".format(factor)
        report = report.append(record)
    return report,rs_wr,total_count

kb = kb[kb.win_r>0.55]
k = kb.sample(1).iloc[0]
# k = kb.iloc[80]

knowledge = k['knowledge']
train_report,train_wr,train_count = get_dist_report(knowledge, train_set, slice)
val_report,val_wr,val_count = get_dist_report(knowledge, validation_set, slice)

import matplotlib.pyplot as plt
import seaborn as sns
fig =plt.figure(figsize=(16,6))
ax1 =fig.add_subplot(121)
ax2 =fig.add_subplot(122)

# 可视化 WR 的标准化
sns.heatmap(train_report,
            ax=ax1, cmap='RdYlGn_r',
            linewidths=0.1, annot=False,
            vmin=10, vmax=90)
ax1.set_ylabel("features")
ax1.set_xlabel("slices")
ax1.set_title("Train   WR:{:.1f}%  Samples:{:.1f}K".format(train_wr*100,train_count/1000))

sns.heatmap(val_report,
            ax=ax2, cmap='RdYlGn_r',
            linewidths=0.1, annot=False,
            vmin=10, vmax=90)
ax2.set_ylabel("features")
ax2.set_xlabel("slices")
ax2.set_title("Validation   WR:{:.1f}%  Samples:{:.1f}K".format(val_wr*100,val_count/1000))
fig.suptitle("K: {} Slices: {:d}".format(k.name, slice))
plt.show()
