#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys,os,datetime

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('Loading knowledge base ...\t',end="")
kb = pd.read_csv("data/knowledge_base.csv",index_col=0)
print('{} records'.format(kb.shape[0]))

print('Loading test set .........\t',end="")
test_set = pd.read_csv("data/test_set.csv",index_col=0)
print('{} records'.format(test_set.shape[0]))

future = ['future_profit','future_risk']

# kb = kb.sort_values(by=['future_profit','future_risk'])
# print(kb[future.extend('security')].head(50))
# sys.exit()

for _ in range(20):
    sample = test_set.sample(1).iloc[0]
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
              'amp_10'  :[-2, 2],
             'risk_10'  :[-1, 1],
             'risk_20'  :[-2, 2],
              'amp_30'  :[-3, 3],
        'prev0_open_c'  :[-2, 2],
        'prev1_open_c'  :[-2, 2],
           'prev1_bar'  :[-2, 2],
    }

    filters = filters_setting.copy()
    filter_limit = 0
    factors = list(filters.keys())
    is_finished = False
    filter_limit=4
    filter_offest=0
    while filter_offest<filter_limit:
        for i in range(len(factors)):
            factor_i = len(factors) - i -1
            _filter = "kb["
            for f in factors:
                if factors.index(f) >= factor_i:
                    offest = np.clip([-filter_offest, filter_offest], filters[f][0], filters[f][1])
                else:
                    offest = np.clip([-(filter_offest-1), (filter_offest-1)], filters[f][0], filters[f][1])
                _filter += "(kb.{}>={}) & (kb.{}<={}) &".format(
                    f,int(sample[f]+offest[0]),
                    f,int(sample[f]+offest[1]))
            _filter += " True]"
            rs = eval(_filter)
            print('\rPredicting: {:2.1f}%'.format( 100*(i/(len(factors)-1)*(1/filter_limit)+(filter_offest)/(filter_limit)) ),end="")
            if len(rs)<=10:
                if factor_i==0 or filter_offest==0:
                    filter_offest +=1
            else:
                is_finished = True
                print("\t[DONE]",end="")
                break
        if is_finished == True: break
    print("\n",end="")
    rs = rs.sort_values(by=['future_profit','future_risk'])
    pred = rs[future][2:-2].median()
    pred.name = 'predict'
    actual = sample[future]
    actual.name = 'actual'
    measure = pd.DataFrame([pred,actual])
    print(measure)
    print(rs.shape[0])
    print("-"*100)
