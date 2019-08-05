#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import multiprocessing as mp
import os

from lib.jqdata import *

def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_categorial(v, categories):
    return np.round(np.quantile([0,v*(categories-1),(categories-1)],0.5)).astype('i')

def extract_features(security,trade_date,get_price,close=None):
    n_steps = 10
    max_days = 120
    params = [
    # days, min, max
    {  8:[0,1]},
    {  5:[0,0.6]},
    {  4:[0,0.5]},
    {  3:[0,0.4]},
    {  2:[0,0.3]},
    {  1:[0,0.15]},]

    history = get_price(security=security, end_date=trade_date, count=max_days)
    if history.shape[0]!=max_days: return None
    if close is None:
        close = history.iloc[-1]['close']

    prev_close = history.iloc[-2]['close']
    prev2_close = history.iloc[-3]['close']

    history = history.iloc[:-1]
    feature = {}

    # env = ""
    # for days in [10,5,3]:
    #     h = history[-days:]
    #     min, max = h['low'].min(), h['high'].max()
    #     min_idx = h[h.low==min].iloc[0].name
    #     max_idx = h[h.high==max].iloc[0].name
    #     min_idx = h.index.get_loc(min_idx)
    #     max_idx = h.index.get_loc(max_idx)
    #     env_bit = 0
    #     if min_idx > max_idx: env_bit=1
    #     env += str(env_bit)
    #
    # env = int(env,2)
    # env = to_categorial(min_max_scale(env,0,15),n_steps)
    # feature['f_env'] = env

    h = history[-6:].copy()
    h['ma5'] = h['close'].rolling(window=5).mean()
    h['ma5_pos'] = (h['close'] - h['ma5']) / h['ma5']
    fma5_pos = h['ma5_pos'].iloc[-1]
    feature['fma5_pos'] = to_categorial(min_max_scale(fma5_pos,-0.05,0.05), n_steps)

    for param in params:
        days = list(param.keys())[0]
        param = param[days]
        history = history[-days:]
        min, max = history['low'].min(), history['high'].max()
        env_bit=0
        if min==max:
            pos = np.round(n_steps/2)
            down = 0
            up = 0
        else:
            pos = (close-min)/(max-min)
            down = min_max_scale((close - max) / max, -param[1],param[0])
            up = min_max_scale((close - min) / min, param[0],param[1])

        feature['f{}d_pos'.format(days)]= to_categorial(pos, n_steps)
        feature['f{}d_down'.format(days)]= to_categorial(down, n_steps)
        feature['f{}d_up'.format(days)]= to_categorial(up, n_steps)

    change = (close - prev_close)/prev_close


    feature['close'] = close
    feature['change'] = np.round(change,3)
    feature['date'] = trade_date

    return feature

def get_train_set(sample_set, start_date, end_date):
    securities = get_all_securites()['security']
    securities = securities.sample(sample_set)

    train_cache = 'data/train_set.csv'
    if os.path.isfile(train_cache):
        train_df = pd.read_csv(train_cache)
    else:
        # generate header
        i,df = 0, pd.DataFrame()
        while len(df)==0:
            i+=1
            backtest = get_price(security=securities.values[i], start_date=start_date, end_date=end_date)
            backtest = backtest[:5]
            df = extract_all_features(securities.values[i], backtest, get_price)
            df = df[:1]
        df.to_csv(train_cache, index=False, header=True)

        N_THREAD = mp.cpu_count()
        threads = []
        splited = np.array_split(securities.values,N_THREAD)
        def runner(securities):
            for i in range(len(securities)):
                security = securities[i]
                print("Generating val set {}/{}: {}".format(i+1,len(securities),security))
                backtest = get_price(security=security, start_date=start_date, end_date=end_date)
                if len(backtest)==0: continue
                df = extract_all_features(security, backtest, get_price)
                train_cache_tmp = train_cache+"_"+security
                df.to_csv(train_cache_tmp, index=False, header=False)
                os.system("cat {} >> {}".format(train_cache_tmp,train_cache))
                os.remove(train_cache_tmp)
        for i in range(len(splited)):
            t = mp.Process(target=runner, args=([splited[i]]))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        train_df = pd.read_csv(train_cache)
    return train_df

def extract_all_features(security,dataset,get_price):
    cache_name_file = "data/cache/{:.6}-features-{:.10}-{:.10}.cache".format(security,str(dataset.index[0]),str(dataset.index[-1]))
    if os.path.isfile(cache_name_file):
        df = pd.read_csv(cache_name_file)
        cols = df.columns.tolist()
        cols.remove('close')
        cols.remove('date')
        df[cols] = df[cols].astype('i')
    else:
        if len(dataset)==0: return pd.DataFrame()
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
    if len(dataset)==0: return dataset
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
    if len(dataset)==0: return dataset
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
    if len(dataset)==0: return dataset
    close = dataset['close']
    dataset['hold'] = 0
    hold_status=0
    for i in range(len(dataset)):
        if hold_status==1 and dataset['buy'].iloc[i]==0:
            dataset.loc[dataset.iloc[i].name,'hold'] = hold_status
        if dataset['buy'].iloc[i]==1:
            hold_status=1
        elif dataset['sell'].iloc[i]==1:
            hold_status=0
            dataset.loc[dataset.iloc[i].name,'hold'] = hold_status
    return dataset
