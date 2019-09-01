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
temp = []
skip = False
for i,row in dataset.iterrows():
    today_change = row['profit']
    profit = 1+today_change/100
    total_profit *= profit

    temp = temp[-4:]
    temp.append(today_change)
    change_ma = np.sum(temp)
    # print ("{:5.2f}".format(np.round(change_ma,2)))
    if change_ma>2:
        skip = True
    if change_ma<-15 or today_change>0:
        skip = False

    if not skip: strategy_profit *= profit
    print("{:06d}\t profit: {:5.2f}%\t\ttotal: {:.2f}%\t strategy: {:.2f}%".format(
        i,today_change,total_profit*100,strategy_profit*100))
