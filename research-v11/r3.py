#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os

# SECURITY = 'sz002627'
# SECURITY = 'sz000001'
SECURITY = 'sz002620'
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

columns = ['date','open','high','low','close','change','money','turnover']
data_file = 'data/stock_data/{}.csv'.format(SECURITY)
history = pd.read_csv(data_file)
history = history[columns]
history = history.sort_values(by=['date'])

# transform
history = history.drop(columns=['money'])
history['turnover'] = np.round(history['turnover']*100,2)

history['change'] = np.round(history['change']*100,2)
history['bar'] = np.round((history['close'] - history['open']) / history['close'].shift(periods=1)*100,2)
history['open_jump'] = np.round((history['open']-history['close'].shift(periods=1)) / history['close'].shift(periods=1)*100,2)
history['amp'] = np.round((history['high']-history['low']) / history['close'].shift(periods=1)*100,2)
history['upline'] = np.round((history['high']-history['open']) / history['close'].shift(periods=1)*100,2)
history['downline'] = np.round((history['open']-history['low']) / history['close'].shift(periods=1)*100,2)
for i in [2,3,5,7]:
    history['turnover_ma{}'.format(i)] = np.round(history['turnover'].rolling(window=i).mean(),2)
    history['changes_{}d'.format(i)] = np.round((history['close']-history['close'].shift(periods=i)) / history['close'].shift(periods=i)*100,2)


slices=9
for i in range(1,slices):
    print("{:3d}  amp:{}\tbar:{:5.2f}\ttov:{:5.2f}\ttov2:{:5.2f}\ttov3:{:5.2f}\ttov5:{:5.2f}\tc2d:{:5.2f}\tc3d:{:5.2f}\tc5d:{:5.2f}\tc7d:{:5.2f}\t ".format(i,
        np.round(history['amp'].quantile(i/slices),2),
        np.round(history['bar'].quantile(i/slices),2),
        np.round(history['turnover'].quantile(i/slices),2),
        np.round(history['turnover_ma2'].quantile(i/slices),2),
        np.round(history['turnover_ma3'].quantile(i/slices),2),
        np.round(history['turnover_ma5'].quantile(i/slices),2),
        np.round(history['changes_2d'].quantile(i/slices),2),
        np.round(history['changes_3d'].quantile(i/slices),2),
        np.round(history['changes_5d'].quantile(i/slices),2),
        np.round(history['changes_7d'].quantile(i/slices),2),
        ))

print(history.shape)
