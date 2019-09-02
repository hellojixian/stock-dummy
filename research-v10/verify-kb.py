#!/usr/bin/env python3
import datetime
import pandas as pd
import math, sys, os

from lib.jqdata import *
from lib.func import *

filename = 'data/dataset-labeled-min.csv'
np.random.seed(0)
dataset = pd.read_csv(filename,index_col=0)
trading_dates = dataset['security'].groupby(dataset.index).count().index.tolist()
print('Trading data loaded')

total_profit = 1
profits,temp = [],[]
history = pd.DataFrame()
skip_days =0
for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    # if date_i>412:break
    subset = dataset[dataset.index==trading_date]
    total = subset.shape[0]

    query = "(prev_5<-9 or prev_4 <-9) and (prev_3>-5 and prev_2>-5) and (prev_1<0 and prev_1>-4) and (prev_0<4.5 and prev_0>0)"
    subset = subset[subset.eval(query)]
    total = subset.shape[0]
    factors = ['money','volume']

    rs = subset
    rs = rs.sort_values(by=['money'],ascending=True)
    rs = rs[:4]

    rs = rs[['security','close','prev_5','prev_4','prev_3','prev_2','prev_1','prev_0','fu_1']]

    if skip_days>0:
        skip_days-=1
        print('skip: {}'.format(skip_days))
    elif rs.shape[0]>=3 :
        print("="*120,'\n',rs,'\n',"="*120)

        profit = rs['fu_1'].mean()
        profits.append({'id':date_i,'date':trading_date,'profit':profit})

        total_profit = total_profit*(1+(profit/100))

        print("{:06}\t{}\t Profit: {:.2f}%\t Total: {:.2f}%\t skip:{}\t secs:{:.2f}\n".format(
                    date_i,trading_date,profit,total_profit*100, skip_days, total))

        # if profit>1:skip_days=1
        # if profit<-0.5:skip_days=10


profits = pd.DataFrame(profits)
profits.to_csv('profit_changes.csv')
history.to_csv('buy_history.csv')
