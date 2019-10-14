#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os

SECURITY = 'sz000001'
# SECURITY = 'sz002620'
np.random.seed(0)


def future_value(subset):
    date = subset.iloc[0]['date']
    close = subset.iloc[0]['close']
    subset = subset[1:]
    v_max, v_min = subset['close'].max(),subset['close'].min()
    f_risk = -(v_min - close) /close
    f_opp = (v_max - close) /close
    if f_opp<0: f_opp =0
    if f_risk<0: f_risk =0
    return f_risk, f_opp

def ideal_change(subset):
    date = subset.iloc[-1]['date']
    close = subset.iloc[-1]['close']
    v_max, v_min = subset['high'].max(),subset['low'].min()
    ideal_down = (v_max - close) /v_max
    ideal_up = (close - v_min) /v_min
    c3d = (close - subset.iloc[-3]['close'])/subset.iloc[-3]['close']
    c5d = (close - subset.iloc[-5]['close'])/subset.iloc[-5]['close']
    c7d = (close - subset.iloc[-7]['close'])/subset.iloc[-7]['close']
    c9d = (close - subset.iloc[-9]['close'])/subset.iloc[-9]['close']
    return ideal_down,ideal_up,c3d,c5d,c7d,c9d



# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

columns = ['date','open','high','low','close','change']
data_file = 'data/stock_data/{}.csv'.format(SECURITY)
history = pd.read_csv(data_file)
history = history[columns]
history = history.sort_values(by=['date'])
history = history[1000:]

# history=history[:160]

lookback_size = 120
future_size = 10

for i in range(len(history)-future_size):
    if i<=lookback_size: continue
    idx = history.index[i]
    subset = history.iloc[i-lookback_size:i]
    future = history.iloc[i:i+future_size]

    # print(subset.iloc[-1]['date'])
    # print(future.iloc[0]['date'])
    # print('----')

    history.loc[idx,'ideal_down'],\
    history.loc[idx,'ideal_up'],\
    history.loc[idx,'c3d'],\
    history.loc[idx,'c5d'],\
    history.loc[idx,'c7d'],\
    history.loc[idx,'c9d'],\
    = ideal_change(subset)

    history.loc[idx,'future_risk'],\
    history.loc[idx,'future_opp'] = future_value(future)

history = history.dropna()
history.to_csv('data/analysis/{}_feature.csv'.format(SECURITY))
print(history)
