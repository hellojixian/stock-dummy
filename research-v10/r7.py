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
skip_days = 0

init_fund = 100000
fund = init_fund
position = pd.DataFrame()


for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    subset = dataset[dataset.index==trading_date]
    total = subset.shape[0]
    # if date_i>550:break

    if skip_days>0:
        skip_days-=1
        print("skiped days:{}".format(skip_days))
        continue

    security=""
    # 如果舱里有票 查看价格 判断是否需要卖出
    if len(position)>0:
        security = position.iloc[0]['security']
        bought_price = position.iloc[0]['close']
        amount = position.iloc[0]['amount']

        rs = subset[subset.security==security]
        if len(rs)>0:
            rec = rs[['security','close','prev_0']].iloc[0]

            close = rec['close']
            change = rec['prev_0']
            min_close = position['close'].min()
            max_close = position['close'].max()
            days = len(position)
            profit = (close - bought_price) / bought_price *100
            min_profit = (min_close - bought_price) / bought_price*100
            max_profit = (max_close - bought_price) / bought_price*100
            should_sell = False

            if profit - min_profit>5:
                should_sell = True
            if min_profit<-1.5 and profit>1:
                should_sell = True
            if days ==1 and profit>0.5:
                should_sell = True
            if days ==2  and profit>1:
                should_sell = True
            if days >=3  and profit>1:
                should_sell = True
            if days >=4  and profit>1:
                should_sell = True
            if days >=5:
                should_sell = True
            # if profit>=8:
            #     should_sell = True
            if profit<-1.5:skip_days=1
            if profit<-5.5:
                should_sell = True
                skip_days=3
            # if change<-7:should_sell = False

            position = position.append(rec)
            print(position)
            print('hold {} days, profit: {:.2f}'.format(days, profit))
            if should_sell:
                print('sold {}'.format(security))
                position = pd.DataFrame()
                fund += close*amount

    # 如果空仓就选股
    if len(position)==0:
        query = "(prev_0<4 & prev_0>-2) and (high!=low) and security!='{}' ".format(security)
        subset = subset[subset.eval(query)]
        factors = ['pos_5','prev_changes_25','money']
        rs_f1 = subset.sort_values(by=[factors[0]],ascending=True)[:30]
        rs_f2 = subset.sort_values(by=[factors[1]],ascending=True)[:10]
        rs = pd.merge(rs_f1,rs_f2,how='inner',on='security',suffixes=("","_y"))
        rs = rs.sort_values(by=[factors[2]],ascending=True)
        if len(rs)==0:
            rs = subset.sort_values(by=[factors[0]],ascending=True)[:30]
            rs = rs.sort_values(by=[factors[2]],ascending=True)
        rs = rs[:1]
        rs = rs[['security','close','prev_0']]
        if len(rs)>0:
            rec = rs.iloc[0].copy()
            rec.name = trading_date
            amount = int(fund / rec['close'] /100)*100
            rec['amount'] = amount
            fund -= rec['close']*amount
            position = pd.DataFrame()
            position = position.append(rec)
            print('bought {}'.format(rec['security']))
            print(position)
        else:
            print('skipped')

    total_value = fund
    if len(position)>0:
        security = position.iloc[0]['security']
        amount = position.iloc[0]['amount']
        rs = subset[subset.security==security]
        if len(rs)>0:
            rec = rs.iloc[0]
            total_value += rec['close']*amount

    total_profit = (total_value)/init_fund*100
    print("-"*120)
    print("{:06}\t{}\t Total: {:.2f}%\t ".format(date_i,trading_date,total_profit))
    print("")
