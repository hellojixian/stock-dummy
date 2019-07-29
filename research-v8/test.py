#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jqdatasdk as jq
import numpy as np
import pandas as pd
import sys,os,datetime

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# fetching data
jq.auth('18611850602','jixian')
security = '600822.XSHG'
start_date = datetime.date(2016,1,1)
end_date = datetime.date(2017,12,20)
frequency = '5m'
# end_date = datetime.date(2016,11,1)
raw_filename = 'data/raw-{}-{}-{}-{}.csv'.format(security, start_date, end_date, frequency)

# laod dataset
if os.path.isfile(raw_filename):
    print("Loading data from cache")
    dataset = pd.read_csv(raw_filename, index_col=0)
else:
    print("Loading data from remote")
    dataset = jq.get_price(security, end_date=end_date, frequency='15m')
    dataset.to_csv(raw_filename)

print('done')
print(dataset.shape)
sys.exit()

scope = 60
ranges = [5,10,60]

def get_support_presure(latest_price, ranges, dataset):
    res = {}
    res['support'] = 0
    ranges = [5,10,20]
    weights = [0.5, 1, 2]
    for i in range(len(ranges)):
        scope = ranges[i]
        df = dataset[-(scope):]
        p_df = pd.Series(df[['open','close']].values.reshape(df.shape[0]*2))
        step = latest_price *0.04
        p_df = np.ceil(np.ceil(p_df/step) * step*100)/100

        p_df = pd.DataFrame(p_df.value_counts(),columns=['count'])
        p_df.loc[:,'weight'] = np.round(p_df['count']/scope,2)
        p_presure = p_df[p_df.index>latest_price].sort_values(by=['count'],ascending=False)
        p_support = p_df[p_df.index<=latest_price].sort_values(by=['count'],ascending=False)

        support, presure = 0, 0
        if p_support.shape[0]>1: support = 5*(-(np.mean(p_support.index[0])-latest_price) / latest_price)
        if p_presure.shape[0]>1: presure = (np.mean(p_presure.index[0])-latest_price) / latest_price
        res['support_{}'.format(scope)] = 1-support
        res['support'] += (1-support) * weights[i]
    res['support'] /= np.sum(weights)
    return res

def get_env_long(latest_price, ranges, dataset):
    for scope in ranges:
        df = dataset[-(scope):]
        slice = 4
        min, max = df[['low']].min()[0], df[['high']].max()[0]
        min_pos, max_pos = df[df.low==min].index, df[df.high==max].index
        pos = np.round((latest_price-min) / (max-min) / (1/slice)).astype('i')
        amp = np.round((max-min)/min*10,0).astype('i')
        trend = 1
        if min_pos >= max_pos:
            trend=0 #下跌
        if min_pos < max_pos:
            trend=2  #上涨
        if amp <=1: trend=1 #横盘整理
        # bin(63)[2:].zfill(10)
        # np.array([int(b) for b in str(bin(63))[2:]])
        print(scope, trend, pos, amp)

for i in range(scope, dataset.shape[0]):
    date = dataset.index[i]
    subset = dataset[i-scope+1:i+1]
    latest_open,latest_price,latest_high,latest_low = subset[-1:][['open','close','high','low']].values[0]
    prev = subset[-2:]

    # if latest_open > latest_price and \
    #     max(prev['open'][0],prev['close'][0]) > latest_open):
    if prev['low'][0] > latest_low and \
        max(prev['open'][0],prev['close'][0]) > latest_price:
        support = get_support_presure(latest_price, [5,10,20], subset)
        # get_env_long(latest_price, ranges, subset)
        print("{} {}\tprice: {}\tsupport: {:.2f}\t".format(
            i, date, latest_price, support['support'] ))
