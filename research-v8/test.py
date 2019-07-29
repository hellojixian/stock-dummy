#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jqdatasdk as jq
import numpy as np
import pandas as pd
import sys,os,datetime

import lib.feature_extract as fe

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# fetching data
jq.auth('18611850602','jixian')
security = '600822.XSHG'
start_date = datetime.date(2005,1,1)
end_date = datetime.date(2016,12,30)
frequency = 'daily'
raw_filename = 'data/cache/raw-{}-{}-{}-{}.csv'.format(security, start_date, end_date, frequency)
test_cache_filename = 'data/cache/test.csv'

# laod dataset
if os.path.isfile(raw_filename):
    print("Loading data from cache")
    dataset = pd.read_csv(raw_filename, index_col=0)
else:
    print("Loading data from remote")
    dataset = jq.get_price(security, start_date=start_date, end_date=end_date, frequency=frequency)
    dataset.to_csv(raw_filename)

print(dataset.shape)

'''
技术难点，

抽象提取特征并保留相似度
    抽象归纳中包含了 涨跌 红绿柱 开盘的跳空
    二进制还是稀疏散列  主要看怎么搜索， 二进制搜索就看右侧几位的相似度
    1根K柱表示为 [0 011 1]
    左侧叠加 这样可以保证高位上的特征相似性
    m.T.reshape(30,1)


要考虑的因素
    5 日K线变化
    [10,20,60] 日冷暖比例
    [ 5,10,30,120] 目前价格的位置区间
    [ 5,10,30,120] 趋势

搜索思路
    除掉自己后按”位“搜索，直到找到样本数量在100-200左右，
'''

scope = 120
# for i in range(scope, dataset.shape[0]):
#     date = dataset.index[i]
#     subset = dataset[i-scope+1:i+1]


if os.path.isfile(test_cache_filename) and True:
    print("Loading feature data from cache")
    df = pd.read_csv(test_cache_filename, index_col=0)
else:
    print("Generate feature data")
    df = fe.encode_daily_prev_changes([0,1,2,3,4],dataset)
    df.to_csv(test_cache_filename)

print(df.shape)
sample = df.sample(1).iloc[0]
filter = 2 ** 20 - 1
bits = 0
while (filter & (filter<<bits)) >0:
    f = filter & (filter<<bits)
    subset = df[(df.prev_c0 & f) == (sample['prev_c0'] & f)]
    print("{:2d}\t{:4d}\t{}".format(bits, subset.shape[0], bin(f)))
    bits +=1
