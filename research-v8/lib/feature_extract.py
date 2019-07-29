#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jqdatasdk as jq
import numpy as np
import pandas as pd
import sys,os,datetime

def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_bin(v,bits):
    def _b(v, ):
        format = "{:0"+int(bits)+"b}"
        if not np.isnan(v):
            return [int(i) for i in format.format(int(v))]
        return v
    return np.round(v*100/(2**bits-1),0).apply(func=_b)

def merge_features(v):
    m = np.array([np.array(x) for x in v.values])
    m = m.T.reshape(m.shape[0]*m.shape[1])
    m = np.array2string(m,separator='')[1:-1]
    return m

def encode_daily_prev_changes(scopes, dataset):
    prefix = 'prev_c'
    res = pd.DataFrame()
    skip = max(scopes)+1
    for scope in scopes:
        df = pd.DataFrame()
        change  = (dataset['close'].shift(periods=scope) - dataset['close'].shift(periods=1+scope)) / dataset['close'].shift(periods=1+scope)
        open_c  = (dataset['open'].shift(periods=scope) - dataset['close'].shift(periods=1+scope)) / dataset['close'].shift(periods=1+scope)
        bar     = (dataset['close'].shift(periods=scope) - dataset['open'].shift(periods=scope)) / dataset['open'].shift(periods=scope)
        up_line     = (dataset['high'].shift(periods=scope) - dataset['close'].shift(periods=scope)) / dataset['close'].shift(periods=scope)
        down_line   = -(dataset['low'].shift(periods=scope) - dataset['close'].shift(periods=scope)) / dataset['close'].shift(periods=scope)

        df['change'] = to_bin(min_max_scale(change, -0.1, 0.1), 4)[skip:]
        df['bar']    = to_bin(min_max_scale(bar, -0.1, 0.1), 4)[skip:]
        df['open_c'] = to_bin(min_max_scale(open_c, -0.1, 0.1), 3)[skip:]
        df['up_line']= to_bin(min_max_scale(up_line, 0, 0.1), 3)[skip:]
        df['down_line']= to_bin(min_max_scale(down_line, 0, 0.1), 3)[skip:]

        df['code'] = df.apply(func=merge_features, axis=1)
        res[prefix+str(scope)] = df['code']
    return res


def _get_support_presure(latest_price, ranges, dataset):
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

def _get_env_long(latest_price, ranges, dataset):
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
