#!/usr/bin/env python3
import datetime
import pandas as pd
import math, sys, os

from lib.jqdata import *
from lib.func import *

# 002633	2019-06-27	 Profit: -0.55%	 Total: 370126.65%	 skip:0	 secs:3559.00


filename = 'data/dataset-labeled-min.csv'
np.random.seed(0)
dataset = pd.read_csv(filename,index_col=0)
trading_dates = dataset['security'].groupby(dataset.index).count().index.tolist()
print('Trading data loaded')

prev_total_profit,total_profit = 1,1
profits,temp = [],[]
skip_days = 8
history = pd.DataFrame()
max_security_pool = 4
min_security_pool = 4

for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    # if date_i>412:break
    subset = dataset[dataset.index==trading_date]
    total = subset.shape[0]
    wr = subset[subset.prev_0>0].shape[0]/total

    # query = "(prev_0<=9 & prev_0>=-4) and (high!=low) and (prev_0>5.2 or prev_0<4.8)"  # 426395.76%
    query = " (prev_0<4 & prev_0>-4) and (high!=low) and pos_10<=20"
    subset = subset[subset.eval(query)]

    factors = ['money_ma_5','money']

    rs = subset
    # rs = rs.sort_values(by=['prev_changes_15'],ascending=True)

    if wr<1:
        rs = subset
        rs_f1 = subset.sort_values(by=[factors[0]],ascending=True)[:10]
        rs_f2 = subset.sort_values(by=[factors[1]],ascending=True)[:150]
        rs = pd.merge(rs_f1,rs_f2,how='inner',on='security',suffixes=("","_y"))
        rs = rs.sort_values(by=['prev_changes_4'],ascending=True)
        change_mean = rs['prev_changes_15'].mean()
        rs = rs[:6]
    else:
        print(wr,'skiped')
        continue


    # rs = rs.sort_values(by=[factors[1]],ascending=False)
    # rs_ob = rs[:10]
    rs = rs[['security','close','prev_changes_25','prev_changes_4','prev_2','prev_1','prev_0','fu_1','fu_2','fu_3','fu_4','fu_5','fu_6']]

    if rs.shape[0]>=min_security_pool :


        profit = rs['fu_5'].mean()
        profits.append({'id':date_i,'date':trading_date,'profit':profit})
        temp.append(profit)

        if skip_days>0:
            skip_days-=1
        else:
            print("="*120,'\n',rs,'\n',"="*120)
            prev_total_profit = total_profit
            total_profit = total_profit*(1+(profit/100)-0.0006)
            history = history.append(rs)
            skip_days=4

            print("{:06}\t{}\t Profit: {:.2f}%\t Total: {:.2f}% => {:.2f}%\t bottom_mean:{:.2f}\t secs:{:.2f}\n".format(
                        date_i,trading_date,profit,prev_total_profit*100,total_profit*100, change_mean, total))

    else:
        print(date_i,trading_date)

profits = pd.DataFrame(profits)
profits.to_csv('profit_changes.csv')
history.to_csv('buy_history.csv')
