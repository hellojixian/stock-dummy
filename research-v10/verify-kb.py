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
cw,cwp = 0,0
cl,clp = 0,0
prev_rr = 0
dataset['prev_changes'] = dataset['prev_0']+dataset['prev_1']+dataset['prev_2']+dataset['prev_3']+dataset['prev_4']

for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    if date_i<=50:continue
    # if date_i>62:break

    subset = dataset[dataset.index==trading_date]
    total = subset.shape[0]
    today_wr = subset[subset.prev_0>0].shape[0] / total
    today_rr = subset[subset.trend_10==1].shape[0] / total

    query = "(prev_0<9.5) & (prev_0>-9.5) & prev_changes>=-17 & trend_10==0"
    subset = subset[subset.eval(query)]

    rs = subset
    rs = rs.sort_values(by=['prev_changes'],ascending=True)
    rs = rs[:20]
    rs = rs.sort_values(by=['pos_60'],ascending=True)
    rs = rs[:7]

    rs = rs[['security','close','prev_changes','prev_0','fu_1']]

    if rs.shape[0]>2 :
        print("="*120)
        print(rs)
        print("="*120)


        if today_rr>prev_rr or today_rr>0.9: # clp>-2.5 or cl>4 or clp<-8.5:
            profit = rs['fu_1'].mean()
            total_profit = total_profit*(1+(profit/100))
            print("{:06}\tDate: {}\t Profit: {:.2f}%\t Total: {:.2f}%\t\t wr: {:.3f}\t rr: {:.3f}\tcw/l: {:.2f}\t{:.2f}".format(
                        date_i,trading_date,profit,total_profit*100,today_wr, today_rr, cl, clp))
        else:
            print("{:06}\tDate: {}\t rr: {:.3f} - Ignored".format(date_i,trading_date,today_rr))

        prev_rr = today_rr
        profit = rs['fu_1'].mean()
        if profit>=0:
            cwp+=profit
            cl=0
            clp=0
        else:
            cw=0
            cwp=0
            cl+=1
            clp +=profit

    else:
        print("{:06}\tDate: {}\t rr: {:.3f} - Ignored".format(date_i,trading_date,today_rr))

    print("\n")
