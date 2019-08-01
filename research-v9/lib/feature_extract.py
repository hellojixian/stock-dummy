#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_categorial(v, categories):
    if v<0: return 0
    if v>1: return categories

    val = v/(1/(categories-1))
    return int(np.round(val+1))

def extract_features(security,trade_date,get_price):
    close = get_price(security=security, end_date=trade_date, count=1)['close'][0]
    days_scopes=[3,5,10,20,30,60,120]
    n_steps = 7

    feature = {}
    for days in days_scopes:
        history = get_price(security=security, end_date=trade_date, count=days)
        history = history.iloc[:-1]
        min, max = history['low'].min(), history['high'].max()
        pos = to_categorial((close-min) / (max-min), n_steps)
        f_key = 'pos_{}'.format(days)
        feature[f_key]= pos

    feature['short']  = np.round(np.mean([feature['pos_3'],feature['pos_5'],feature['pos_10']]),1)
    feature['median'] = np.round(np.mean([feature['pos_20'],feature['pos_30']]),1)
    feature['long']   = np.round(np.mean([feature['pos_60'],feature['pos_120']]),1)
    feature['close'] = close
    feature['date'] = trade_date
    return feature
