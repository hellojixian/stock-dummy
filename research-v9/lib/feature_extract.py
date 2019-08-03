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

def extract_features(security,trade_date,get_price,close=None):
    days_scopes=[120,60,30,20,10,5,3]
    n_steps = 7

    history = get_price(security=security, end_date=trade_date, count=days_scopes[0]+1)
    if close is None:
        close = history.iloc[-1]['close']
    prev_close = history.iloc[-2]['close']

    history = history.iloc[:-1]
    feature = {}
    for days in days_scopes:
        history = history[-days:]
        min, max = history['low'].min(), history['high'].max()
        if min==max:
            pos = np.round(n_steps/2)
            amp = 0
        else:
            pos = to_categorial((close-min) / (max-min), n_steps)
            amp = (max-min)/min

        feature['{}d_pos'.format(days)]= pos
        feature['{}d_amp'.format(days)]= amp

    feature['close'] = close
    feature['change'] = (close - prev_close)/prev_close
    feature['date'] = trade_date
    return feature
