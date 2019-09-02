#!/usr/bin/env python3

import datetime
import pandas as pd
import math, sys, os
import progressbar
import multiprocessing as mp

from lib.jqdata import *
from lib.func import *
from lib.dna import *

total_profit = 1
strategy_profit = 1
dataset = pd.read_csv('profit_changes.csv')
# dataset = pd.read_csv('profit_changes_bak.csv')
temp = [0]
skip_days = 5
h1,h2=0,0
for i,row in dataset.iterrows():
    today_change = row['profit']
    profit = 1+today_change/100
    total_profit *= profit

    temp.append(today_change)

    # print ("{} {:5.2f}".format(row['date'], np.round(today_change,2)))

    if skip_days>0:
        skip_days-=1
    else:
        strategy_profit *= profit


    if skip_days==0:
        if np.sum(temp[-6:])>=18: skip_days = 2
        if np.sum(temp[-2:])>=11: skip_days = 3
        if temp[-1]<=0 and temp[-2]>=0 and temp[-3]<=0 and temp[-4]>=0 and temp[-5]>=0: skip_days = 1
        if temp[-1]<=0 and temp[-2]<=0 and temp[-3]>=0 and temp[-4]<=0 and temp[-5]<=0: skip_days = 1
        if temp[-1]<=0 and temp[-2]<=0 and temp[-3]<=0 and temp[-4]<=0 and temp[-5]>=0: skip_days = 1
        # if np.where(np.array(temp[-7:])<=0)[0].shape[0]==7: skip_days=1
        # if np.where(np.array(temp[-10:])<=0)[0].shape[0]==9: skip_days=1
    else:
        # if np.sum(temp[-2:])<=-12: skip_days =0
        pass


    print("{:06d}\t {}\t profit: {:5.2f}%\t\ttotal: {:.2f}%\t strategy: {:.2f}%\t skip: {}".format(
        i,row['date'],today_change,total_profit*100,strategy_profit*100, skip_days))
print(h1,h2)
