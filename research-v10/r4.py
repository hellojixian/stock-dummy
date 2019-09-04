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
history = pd.DataFrame()
max_security_pool = 4
slice = 10
prev_subset = None
for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    if date_i<8:continue
    subset = dataset[dataset.index==trading_date]
    if prev_subset is None:
        prev_subset = subset
        continue


    prev_total = prev_subset.shape[0]
    slice_size = int(prev_total/slice)

    q = ""
    factors = ['money','prev_changes_7']
    print("\n\n{}\t{}\tsize:{}".format(date_i,trading_date,slice_size))
    best_ranges = pd.DataFrame()
    for f in factors:
        prev_subset = prev_subset.sort_values(by=[f],ascending=True)
        f_pd = pd.DataFrame()
        for i in range(slice):
            start_pos = slice_size*i
            end_pos = slice_size*(i+1)
            rs = prev_subset[start_pos:end_pos]
            wr,value = 0,0
            if len(rs)>0:
                wr = len(rs[rs.prev_0>0.5])/len(rs)
                value = rs['prev_0'].mean()
            # print("{}\t{}\t wr:{:.2f}\t value:{:.2f}".format(f,i,wr,value))
                f_pd = f_pd.append(pd.Series({
                'i':i,
                'f':f,
                'value':value,
                'wr':wr
                },name=i))
        f_pd = f_pd.sort_values(by=['value'],ascending=False)
        best_slice = f_pd.iloc[0]
        best_ranges=best_ranges.append(best_slice)


    query = "(prev_0<=9 & prev_0>-4) and (high!=low) and prev_1<9"
    subset = subset[subset.eval(query)]
    prev_subset = subset

    total = subset.shape[0]
    slice_size = int(total/slice)
    rs_list = pd.DataFrame()
    for _,row in best_ranges.iterrows():
        range_id = row['i']
        factor = row['f']
        rs = subset.sort_values(by=[factor],ascending=True)
        rs = rs[slice_size*i:slice_size*i+3]
        rs_list = rs_list.append(rs)

    if len(rs_list)>0:
        rs_list = rs_list[['security','close','prev_1','prev_0','fu_1','fu_2','fu_3','fu_4','fu_5','fu_6']]
        profit = rs_list['fu_1'].mean()
        prev_total_profit = total_profit
        total_profit = total_profit*(1+(profit/100)-0.0006)
        print("="*120,'\n',rs_list,'\n',"="*120)
        print("{:06}\t{}\t Profit: {:.2f}%\t Total: {:.2f}% => {:.2f}%\t skip:{}\t secs:{:.2f}\n".format(
                    date_i,trading_date,profit,prev_total_profit*100,total_profit*100, skip_days, total))

    print("="*100)
