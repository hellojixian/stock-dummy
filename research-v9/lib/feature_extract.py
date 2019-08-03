#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os

def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_categorial(v, categories):
    return np.round(np.quantile([0,v*(categories-1),(categories-1)],0.5)).astype('i')

def extract_all_features(security,backtest,get_price):
    cache_name_file = "data/cache/{:.6}-features-{:.10}-{:.10}.cache".format(security,str(backtest.index[0]),str(backtest.index[-1]))
    if os.path.isfile(cache_name_file):
        df = pd.read_csv(cache_name_file, index_col=0)
    else:
        features = []
        for trade_date in backtest.index:
            features.append(extract_features(security,trade_date,get_price))
        df = pd.DataFrame(features)
        df.to_csv(cache_name_file)
    return df

def extract_features(security,trade_date,get_price,close=None):
    n_steps = 10
    max_days = 120
    params = [
    # days, min, max
    {120:[0.2,2. ,]},
    { 60:[0. ,1. ,]},
    { 30:[0. ,0.7,]},
    { 10:[0. ,0.5,]},
    {  5:[0. ,0.4,]},
    {  3:[0. ,0.3,]}]

    history = get_price(security=security, end_date=trade_date, count=max_days)
    if close is None:
        close = history.iloc[-1]['close']

    prev_close = history.iloc[-2]['close']
    prev2_close = history.iloc[-3]['close']

    history = history.iloc[:-1]
    feature = {}
    for param in params:
        days = list(param.keys())[0]
        param = param[days]
        history = history[-days:]
        min, max = history['low'].min(), history['high'].max()
        if min==max:
            pos = np.round(n_steps/2)
            amp = 0
            cdi = min_max_scale((days-1),0,days)
        else:
            pos = (close-min)/(max-min)
            amp = min_max_scale((max-min)/min, param[0], param[1])
            cdi = min_max_scale(history['high'].tolist().index(max),0,days)

        feature['{}d_pos'.format(days)]= to_categorial(pos, n_steps)
        feature['{}d_amp'.format(days)]= to_categorial(amp, n_steps)
        feature['{}d_cdi'.format(days)]= to_categorial(cdi, n_steps)

    d1_chg = to_categorial(min_max_scale((close - prev_close)/prev_close,-0.09,0.09), n_steps)
    d2_chg = to_categorial(min_max_scale((close - prev2_close)/prev2_close,-0.18,0.18), n_steps)

    feature['1d_chg'] = d1_chg
    feature['2d_chg'] = d2_chg
    feature['close'] = close
    feature['date'] = trade_date

    return feature
