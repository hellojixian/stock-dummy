#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jqdatasdk as jq
import numpy as np
import pandas as pd
import sys,os,datetime


def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_categorial(v, categories):
    return np.round(v/(1/categories),0)

def merge_features(v):
    m = np.array([np.array(x) for x in v.values])
    m = m.T.reshape(m.shape[0]*m.shape[1])
    m = np.array2string(m,separator='')[1:-1]
    return m

def daily_changes(scopes, dataset):
    prefix = 'prev'
    skip = max(scopes)+1
    df = pd.DataFrame()
    for scope in scopes:
        change  = (dataset['close'].shift(periods=scope) - dataset['close'].shift(periods=1+scope)) / dataset['close'].shift(periods=1+scope)
        open_c  = (dataset['open'].shift(periods=scope) - dataset['close'].shift(periods=1+scope)) / dataset['close'].shift(periods=1+scope)
        bar     = (dataset['close'].shift(periods=scope) - dataset['open'].shift(periods=scope)) / dataset['open'].shift(periods=scope)
        up_line     = (dataset['high'].shift(periods=scope) - dataset['close'].shift(periods=scope)) / dataset['close'].shift(periods=scope)
        down_line   = -(dataset['low'].shift(periods=scope) - dataset['close'].shift(periods=scope)) / dataset['close'].shift(periods=scope)

        df[prefix+str(scope)+'_change'] = to_categorial(min_max_scale(change, -0.1, 0.1), 16)[skip:]
        df[prefix+str(scope)+'_bar']    = to_categorial(min_max_scale(bar, -0.1, 0.1), 16)[skip:]
        df[prefix+str(scope)+'_open_c'] = to_categorial(min_max_scale(open_c, -0.1, 0.1), 10)[skip:]
        df[prefix+str(scope)+'_up_line']= to_categorial(min_max_scale(up_line, 0, 0.1), 5)[skip:]
        df[prefix+str(scope)+'_down_line']= to_categorial(min_max_scale(down_line, 0, 0.1), 5)[skip:]
    return df

def get_env(ranges, dataset):
    res = pd.DataFrame()
    def _get_trend(v):
        min, max = np.min(v), np.max(v)
        min_pos, max_pos = v.tolist().index(min), v.tolist().index(max)
        amp = (v[-1]-min) / (max-min)
        trend = 1.
        if min_pos >= max_pos:
            trend=0. #下跌
        if min_pos < max_pos:
            trend=2.  #上涨
        if amp <=0.1: trend=1. #横盘整理
        return trend

    for scope in ranges:
        df = dataset
        min, max = df['low'].rolling(window=scope).min(), df['high'].rolling(window=scope).max()
        res['pos_'+str(scope)] = to_categorial(min_max_scale((df['close']-min) / (max-min),0,1),5)
        res['amp_'+str(scope)] = to_categorial(min_max_scale((max-min)/min,0,0.5),4)
        res['trend_'+str(scope)] = df['close'].rolling(window=scope).apply(func=_get_trend, raw=True)
    return res


def risk_index(ranges, dataset):
    res = pd.DataFrame()
    def _get_risk_index(v):
        return len(np.where(v<=0)[0])/v.shape[0]

    for scope in ranges:
        df = dataset
        change = (dataset['close'].shift(periods=scope) - dataset['close'].shift(periods=1+scope)) / dataset['close'].shift(periods=1+scope)
        res['risk_'+str(scope)] = to_categorial(change.rolling(window=scope).apply(func=_get_risk_index, raw=True),7)
    return res

def future_value(dataset):
    res = pd.DataFrame()

    dataset = dataset.copy()
    def _profit_eval(v):
        close = v[0]
        max = np.max(v)
        return (max - close) / close

    def _risk_eval(v):
        close = v[0]
        max_idx = 0
        if not np.isnan(np.max(v)):
            max_idx = v.tolist().index(np.max(v))
        if max_idx>1:
            v = v[0:max_idx]
        return (np.min(v) - close) / close

    cols = []
    for i in range(8):
        cols.extend(['f'+str(i)])
        dataset['f'+str(i)] = dataset['close'].shift(periods=-i)
    res['future_profit'] = np.round(dataset[cols].apply(func=_profit_eval, raw=True, axis=1)*100,2)
    res['future_risk'] = np.round(dataset[cols].apply(func=_risk_eval, raw=True, axis=1)*100,2)
    return res

def reduce_kb(df):
    if len(df)==0: return df
    cols =['open', 'close', 'high', 'low', 'volume', 'money']
    df = df.drop(columns=cols)

    df = df.reset_index()
    cols = [
    'index',
    'security',
    'risk_60',
    'risk_30',
    'amp_10',
    'amp_120',
    'prev4_down_line',
    'prev4_up_line',
    'prev4_open_c',
    'prev4_bar',
    'prev3_down_line',
    'prev3_up_line',
    'prev3_open_c',
    'prev4_bar',
    'prev2_down_line',
    'prev2_up_line',
    'prev2_open_c',
    'prev2_bar',
    'prev1_down_line',
    'prev1_up_line',
    ]

    df = df.drop(columns=cols)
    int_cols = df.columns[:-2]
    float_cols = ['future_profit','future_risk']
    df_float = df[float_cols].copy()
    df = df.astype('i')
    df[float_cols] = df_float
    return df
