#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will visualize the win/lose data distributions
"""
import pandas as pd
import numpy as np
import warnings,sys,os
import json, pprint
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

train_data_filename      = 'data/featured-v7.1-HS300-2006-2016.csv'
validation_data_filename = 'data/featured-v7.1-HS300-2017-2018.csv'

print('Loading dataset ...')
train_df = pd.read_csv(train_data_filename, index_col=0)
validation_df = pd.read_csv(validation_data_filename, index_col=0)

report = pd.DataFrame()
profit_min, profit_max, step = -2.5,3.5,0.25
for min_exp in np.arange(profit_min, profit_max ,step):
    rec = pd.Series()
    for name,df in [('train',train_df), ('validation',validation_df)]:
        total = df.shape[0]
        sample_c = df[df.fu_c1>min_exp].shape[0]
        sample_r = sample_c/total
        rec[name+'_sample_r'] = sample_r
    rec['min_exp'] = min_exp
    report=report.append(rec,ignore_index=True)

print(report)
fig =plt.figure(figsize=(14,6))
ax1 =fig.add_subplot(111)

# 可视化 WR 的标准化
width=step*0.8/2
ax1.plot(report['min_exp'], report['train_sample_r'],label='train_sample_r', alpha=0.3, color='b')
ax1.plot(report['min_exp'], report['validation_sample_r'],label='validation_sample_r', alpha=0.3, color='r')
ax1.bar(report['min_exp']- width/2, report['train_sample_r'],width=width, label='train_sample_r', alpha=0.6, color='b')
ax1.bar(report['min_exp']+ width/2, report['validation_sample_r'],width=width,label='validation_sample_r', alpha=0.6, color='r')


ax1.set_ylabel('score')
ax1.set_xlabel('min profit expectation')
ax1.legend(loc='upper right')
ax1.set_xticks(report['min_exp'])
ax1.set_yticks(np.round(np.linspace(0,1, 21),2))
ax1.set_ylim(0,1)
ax1.set_xlim(profit_min-step/2, profit_max-step/2)
ax1.set_title("Min Profile Expectation / Samples")
ax1.grid(color='gray', linestyle='dashed',alpha=0.3)
plt.show()
