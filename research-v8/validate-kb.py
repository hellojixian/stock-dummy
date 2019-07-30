#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys,os,datetime,time
import gc
from scipy import stats

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('Loading knowledge base ...\t',end="")
kb = pd.read_csv("data/knowledge_base_1800.csv")
print('{} records'.format(kb.shape[0]))

print('Loading test set .........\t',end="")
test_set = pd.read_csv("data/test_set-min.csv")
print('{} records'.format(test_set.shape[0]))


# 强制转换成整数 为了加速搜索 至少减少内存消耗了
def optimize_df(df):
    int_cols = df.columns[:-2]
    float_cols = ['future_profit','future_risk']
    df_float = df[float_cols].copy()
    df = df.astype('b')
    df[float_cols] = df_float
    return df
kb = optimize_df(kb)
test_set = optimize_df(test_set)
gc.collect()

future = ['future_profit','future_risk']

def predict(sample):
    start_timestamp = time.time()

    def _check_similarity_loss(v, sample):
        return np.abs(v-sample).sum()

    filters_setting = {
        'prev0_change'  :[ 0, 0],
        'prev1_change'  :[ 0, 0],
        'prev2_change'  :[ 0, 0],
             'trend_5'  :[ 0, 0],
            'trend_10'  :[ 0, 0],
           'prev0_bar'  :[-1, 1],
            'trend_30'  :[-1, 1],
               'pos_5'  :[-1, 1],
              'pos_10'  :[-1, 1],
              'pos_30'  :[-1, 1],
        'prev4_change'  :[-1, 1],
           'trend_120'  :[-1, 1],
             'pos_120'  :[-1, 1],
               'amp_5'  :[-2, 2],
             'risk_10'  :[-1, 1],
             'risk_20'  :[-2, 2],
              'amp_30'  :[-3, 3],
        'prev0_open_c'  :[-2, 2],
        'prev1_open_c'  :[-2, 2],
           'prev1_bar'  :[-2, 2],
       'prev0_up_line'  :[-2, 2],
     'prev0_down_line'  :[-2, 2],
    }

    filters = filters_setting.copy()
    filter_limit = 0
    factors = list(filters.keys())
    filter_limit=2
    filter_offest=1
    while filter_offest<filter_limit:
        _filter = ""
        for f in factors:
            offest = np.clip([-filter_offest, filter_offest], filters[f][0], filters[f][1])
            _filter += "({}>={}) & ({}<={}) &".format(
                f,int(sample[f]+offest[0]),
                f,int(sample[f]+offest[1]))
        _filter += " True"
        rs = kb[kb.eval(_filter)].copy()
        if len(rs)<=10:
            filter_offest +=1
        else:
            break

    pred = pd.Series()
    kb_sample_count = rs.shape[0]
    reduced_sample_count = 0
    if kb_sample_count >10:
        pred['result'] = True
        rs['similarity_loss'] = rs.apply(func=_check_similarity_loss, args=[sample], raw=True, axis=1)
        rs = rs.sort_values(by=['similarity_loss'],ascending=True)
        rs = rs[rs.similarity_loss<=15]
        rs = rs[:20]
        reduced_sample_count = rs.shape[0]
        if reduced_sample_count<=2:
            pred['result'] = False
        for f in future:
            pred['{}_mean'.format(f)] = rs[f].mean()
            settings = {'med':0.5}
            for k in settings:
                v = settings[k]
                pred['{}_{}'.format(f,k)] = rs[f].quantile(v)
        pred['similarity_loss'] = rs['similarity_loss'].max()
    else:
        pred['result'] = False
        pred['similarity_loss'] = float('nan')
    pred['samples_count'] = int(kb_sample_count)
    pred['reduced_count'] = int(reduced_sample_count)
    pred['durtion'] = np.round((time.time() - start_timestamp),2)
    return pred


for _ in range(20):
    sample = test_set.sample(1).iloc[0]
    pred = predict(sample)
    if pred['result']==False:
        print("No enough samples - Skip")
        print("samples: {:d}=>{:d} \tdurtion: {:d}s ".format(
            int(pred['samples_count']),int(pred['reduced_count']),int(pred['durtion'])))
    else:
        measure = {"future_profit":{},"future_risk":{}}
        for f in future:
            measure[f]["actual"] = sample[f]
            measure[f]["predict_med"] = pred[f+"_med"]
            measure[f]["predict_mean"] = pred[f+"_mean"]
            # measure[f]["correct"] = (sample[f] >= pred[f+"_d"]) & (sample[f] <= pred[f+"_u"])
        measure = pd.DataFrame(measure)
        measure = measure.T
        cols = ['actual','predict_med','predict_mean']
        print(measure[cols])

        print("samples: {:d}=>{:d} \tdurtion: {:2.2f}s \t loss: {:.2f}".format(
            int(pred['samples_count']),int(pred['reduced_count']),pred['durtion'],pred['similarity_loss']))

    print("-"*100)
