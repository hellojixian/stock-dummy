#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os

def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_categorial(v, categories):
    return np.round(np.quantile([0,v*(categories-1),(categories-1)],0.5)).astype('i')

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
    if history.shape[0]!=max_days: return None
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

        feature['f{}d_pos'.format(days)]= to_categorial(pos, n_steps)
        feature['f{}d_amp'.format(days)]= to_categorial(amp, n_steps)
        feature['f{}d_cdi'.format(days)]= to_categorial(cdi, n_steps)

    change = (close - prev_close)/prev_close
    d1_chg = to_categorial(min_max_scale(change,-0.09,0.09), n_steps)
    d2_chg = to_categorial(min_max_scale((close - prev2_close)/prev2_close,-0.18,0.18), n_steps)

    feature['f1d_chg'] = d1_chg
    feature['f2d_chg'] = d2_chg
    feature['close'] = close
    feature['change'] = np.round(change,3)
    feature['date'] = trade_date

    return feature

def extract_all_features(security,dataset,get_price):
    cache_name_file = "data/cache/{:.6}-features-{:.10}-{:.10}.cache".format(security,str(dataset.index[0]),str(dataset.index[-1]))
    if os.path.isfile(cache_name_file):
        df = pd.read_csv(cache_name_file)
        cols = df.columns.tolist()
        cols.remove('close')
        cols.remove('date')
        df[cols] = df[cols].astype('i')
    else:
        features = []
        for trade_date in dataset.index:
            f = extract_features(security,trade_date,get_price)
            if f is not None: features.append(f)
        df = pd.DataFrame(features)
        df = mark_ideal_buypoint(security,df)
        df = mark_ideal_sellpoint(security,df)
        df = mark_holding_days(security,df)
        df.to_csv(cache_name_file, index=False)
    return df


def mark_ideal_buypoint(security,dataset):
    close = dataset['close']
    dataset['buy'] = 0
    for i in range(len(dataset)):
        if i<=2: continue
        if i+3>= len(dataset): break
        if close.iloc[i-1] >= close.iloc[i]   and \
           close.iloc[i+1] > close.iloc[i]   and \
           ((close.iloc[i+1] - close.iloc[i])/close.iloc[i]>0.015 or \
           (close.iloc[i+2] - close.iloc[i])/close.iloc[i]>0.015 or \
           (close.iloc[i+3] - close.iloc[i])/close.iloc[i]>0.015 ):
           dataset.loc[dataset.iloc[i].name,'buy'] = 1
    return dataset

def mark_ideal_sellpoint(security,dataset):
    close = dataset['close']
    dataset['sell'] = 0
    for i in range(len(dataset)):
        if i<=2: continue
        if i+3>= len(dataset): break
        if close.iloc[i-1] <= close.iloc[i]   and \
           close.iloc[i+1] < close.iloc[i]   and \
           ((close.iloc[i+1] - close.iloc[i])/close.iloc[i]<-0.015 or \
           (close.iloc[i+2] - close.iloc[i])/close.iloc[i]<-0.015 or \
           (close.iloc[i+3] - close.iloc[i])/close.iloc[i]<-0.015 ):
           dataset.loc[dataset.iloc[i].name,'sell'] = 1
    return dataset

def mark_holding_days(security,dataset):
    close = dataset['close']
    dataset['hold'] = 0
    hold_status=0
    for i in range(len(dataset)):
        dataset.loc[dataset.iloc[i].name,'hold'] = hold_status
        if dataset['buy'].iloc[i]==1:
            hold_status=1
        elif dataset['sell'].iloc[i]==1:
            hold_status=0
            dataset.loc[dataset.iloc[i].name,'hold'] = hold_status
    return dataset
