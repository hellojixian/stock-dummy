#!/usr/bin/env python3

import datetime
import pandas as pd
import math, sys, os
import progressbar
import multiprocessing as mp

from lib.jqdata import *
from lib.func import *
from lib.dna import *

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

filename = 'data/dataset-labeled-min.csv'
np.random.seed(0)
dataset = pd.read_csv(filename,index_col=0)
print('Data loaded')
trading_dates = dataset['security'].groupby(dataset.index).count().index.tolist()
print('Trading dates loaded')


total_profit = 1

prev_close_ma,prev_close_ma2,prev_close_ma3 = 0,0,0
skip_days = 0
high_risk=0
dataset['prev_changes'] = dataset['prev_0']+dataset['prev_1']+dataset['prev_2']+dataset['prev_3']+dataset['prev_4']
profits = []
temp = []
skip = False
for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    subset = dataset[dataset.index==trading_date]
    total = subset.shape[0]

    # subset = subset.sort_values(by=['close'],ascending=True)
    # close_ma = subset[100:400]['close'].mean()

    temp = temp[-4:]
    temp.append(today_change)
    change_ma = np.sum(temp)
    if change_ma>2:
        skip = True
    if change_ma<-15 or today_change>0:
        skip = False

    wr = subset[subset.prev_0>0].shape[0] / total

    query = "trend_10==0 &  (prev_0<=9 & prev_0>=-4)"
    subset = subset[subset.eval(query)]

    rs = subset
    rs = rs.sort_values(by=['money'],ascending=True)
    rs = rs[:500]
    rs = rs.sort_values(by=['close'],ascending=True)
    rs = rs[:200]
    rs = rs.sort_values(by=['prev_changes'],ascending=True)
    rs = rs[:100]
    rs = rs.sort_values(by=['pos_vol_10'],ascending=True)
    rs = rs[:20]
    rs = rs.sort_values(by=['pos_90'],ascending=True)
    rs = rs[:10]

    rs = rs[['security','close','prev_changes','prev_1','prev_0','fu_1']]

    if rs.shape[0]>4 :
        print("="*120)
        print(rs)
        print("="*120)

        # ma_p0 = (close_ma+prev_close_ma)/2
        # ma_p1 = (prev_close_ma+prev_close_ma2)/2
        # ma_diff = ma_p0-ma_p1
        profit = rs['fu_1'].mean()
        profits.append({
        'date_i':date_i,
        'date':trading_date,
        'profit':profit})
        # if ((prev_rr>today_rr or prev_rr_2 > today_rr) or today_rr<0.1): # 最高收益185倍
        # ma_diff>0 or close_ma-prev_close_ma>=0 or today_rr<0.3:
        if not skip:
            total_profit = total_profit*(1+(profit/100))
        print("{:06}\t{}\t Profit: {:.2f}%\t Total: {:.2f}%\t wr: {:.3f}\t rr: {:.3f}\t skip:{}".format(
                    date_i,trading_date,profit,total_profit*100,wr, pos90_ma, skip_days))

    print("\n")
profits = pd.DataFrame(profits)
profits.to_csv('profit_changes.csv')
