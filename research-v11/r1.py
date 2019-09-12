#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os

SECURITY = 'sz002627'
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

# find turn point, or dense point
step_len = np.abs(history['close'] - history['close'].shift(periods=1)).mean()

subset = history[['open','high','low','close']][:60]
close = subset['close'].iloc[-1]
prices = subset.values.flatten()
prices = np.sort(prices)
prices = np.round(prices/step_len)
dist = pd.Series(prices).value_counts()
dist.index *= step_len
dist.index = np.round(dist.index,2)
dist = dist.sort_index()
print(dist)
print(int(close/step_len)*step_len)
print(history[['close','change']][10:80])


sys.exit()
