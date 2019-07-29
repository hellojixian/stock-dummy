#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    [ 5,10,30,120] 目前价格的位置区间 [Done]
    [ 5,10,30,120] 趋势 [Done]

搜索思路
    除掉自己后按”位“搜索，直到找到样本数量在100-200左右，
'''

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
securities = jq.get_index_stocks('000300.XSHG')

knowledge_base = pd.DataFrame()
knowledge_base_filename = "data/knowledge_base.csv"
test_cache_filename = 'data/cache/test.csv'
i=0
for security in securities:
    start_date = datetime.date(2005,1,1)
    end_date = datetime.date(2016,12,30)
    frequency = 'daily'
    raw_filename = 'data/cache/raw-{}-{}-{}-{}.csv'.format(security, start_date, end_date, frequency)

    # laod dataset
    if os.path.isfile(raw_filename):
        # print("Loading data from cache")
        dataset = pd.read_csv(raw_filename, index_col=0)
    else:
        # print("Loading data from remote")
        dataset = jq.get_price(security, start_date=start_date, end_date=end_date, frequency=frequency)
        dataset.to_csv(raw_filename)

    knowledge_base = knowledge_base.append(dataset)
    i+=1
    print("\rprogress: {:.2f}%\tsecurity: {}\trecords: {} ".format(
        i/len(securities)*100, security, knowledge_base.shape[0]),end="")

knowledge_base.to_csv(knowledge_base_filename)
print(knowledge_base.shape)
print("Done")



if os.path.isfile(test_cache_filename) and True:
    print("Loading feature data from cache")
    dataset = pd.read_csv(test_cache_filename, index_col=0)
else:
    print("Generate feature data")
    dataset['security'] = security
    dataset = dataset.join(fe.daily_changes([4,3,2,1,0],dataset))
    dataset = dataset.join(fe.get_env([120,30,10,5],dataset))
    dataset = dataset.join(fe.risk_index([60,30,20,10],dataset))
    dataset = dataset.join(fe.future_value(dataset))
    dataset = dataset.dropna()
    dataset.to_csv(test_cache_filename)

dataset = dataset.drop(columns=['open', 'close', 'high', 'low', 'volume', 'money'])
print(dataset.shape)
# print(dataset.columns)

sample = dataset.sample(1).iloc[0]
future = ['future_profit','future_risk']
filters = {
    'prev0_change'  :[0,0],
    'prev1_change'  :[-1,1],
    'prev2_change'  :[-1,1],
        'trend_5'   :[0,0],
        'trend_10'  :[-1,1],
        'trend_30'  :[-1,1],
}

_filter = "dataset["
for f in filters.keys():
    _filter += "(dataset.{}>={}) & (dataset.{}<={}) &".format(
        f,int(sample[f]+filters[f][0]),
        f,int(sample[f]+filters[f][1]))
_filter += " True]"

rs = eval(_filter)
rs=rs[rs.index!=sample.name]
print(sample[future])
print(rs.shape[0])
print(rs[future].mean())
