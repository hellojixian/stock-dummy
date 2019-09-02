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
skip_days = 8
history = pd.DataFrame()

for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    # if date_i>412:break
    subset = dataset[dataset.index==trading_date]
    total = subset.shape[0]

    query = "(prev_0<=9 & prev_0>-3)"
    subset = subset[subset.eval(query)]

    factors = ['money','prev_changes_6']

    rs = subset

    rs = rs.sort_values(by=[factors[0]],ascending=True)
    # rs = rs[:int(total*0.05)]
    # rs = rs.sort_values(by=[factors[1]],ascending=True)
    rs = rs[:8]
    rs = rs[['security','close',factors[1],'prev_1','prev_0','fu_1']]

    if rs.shape[0]>4 :
        print("="*120,'\n',rs,'\n',"="*120)

        profit = rs['fu_1'].mean()
        profits.append({'id':date_i,'date':trading_date,'profit':profit})
        temp.append(profit)

        if skip_days>0:
            skip_days-=1
        else:
            total_profit = total_profit*(1+(profit/100))

        print("{:06}\t{}\t Profit: {:.2f}%\t Total: {:.2f}%\t skip:{}\t secs:{:.2f}\n".format(
                    date_i,trading_date,profit,total_profit*100, skip_days, total))

        if skip_days==0:
            if np.sum(temp[-2:])>=11: skip_days = 3
            if temp[-1]<=0 and temp[-2]>=0 and temp[-3]<=0 and temp[-4]>=0 and temp[-5]>=0: skip_days = 1
            if temp[-1]<=0 and temp[-2]<=0 and temp[-3]>=0 and temp[-4]<=0 and temp[-5]<=0: skip_days = 1
            if temp[-1]<=0 and temp[-2]<=0 and temp[-3]<=0 and temp[-4]<=0 and temp[-5]>=0: skip_days = 1

profits = pd.DataFrame(profits)
profits.to_csv('profit_changes.csv')
history.to_csv('buy_history.csv')
