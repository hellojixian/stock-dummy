#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys,os,datetime,time
import gc

# 强制转换成整数 为了加速搜索 至少减少内存消耗了
def optimize_df(df):
    int_cols = df.columns[:-2]
    float_cols = ['future_profit','future_risk']
    df_float = df[float_cols].copy()
    df = df.astype('b')
    df[float_cols] = df_float
    return df

def predict(sample):
    start_timestamp = time.time()
    future = ['future_profit','future_risk']

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
        _filter = _filter[:-1]
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
