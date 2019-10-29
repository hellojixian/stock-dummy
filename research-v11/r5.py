#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob
import json
import pprint

from lib.strategies.ZhuiZhangStrategy import ZhuiZhangStrategy

np.random.seed(10)
# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

'''
每种策略应该都对应自己的风险控制，由于买入原则不同 风险控制机制也应该不同
可以单独被训练


长策略
    下跌一个波段，前压力位
    变量：
    - 前压力位置win_rate

W底部匹配
    下跌后 反弹 再次回踩则买入

短策略
    最多持有3天
    - 瞬间超跌反弹


训练模式
生产模式
'''


def fetch_dataset(quantity=1):
    dataset = []
    path = 'data/stock_data/'
    columns = ['date','open','high','low','close','change']
    files = [f for f in glob.glob(path + "*.csv", recursive=False)]
    selected_files = np.random.choice(files, size=quantity)

    for data_file in selected_files:
        history = pd.read_csv(data_file)
        history = history[columns]
        history = history.sort_values(by=['date'])
        dataset.append(history)
    return dataset

train_ds = fetch_dataset(quantity=1)
val_ds = fetch_dataset(quantity=2)
stg = ZhuiZhangStrategy()
for i in range(100):
    if stg.evolve(training_set=train_ds, validation_set=val_ds) == False:
        print("TODO: Should pick up another dataset to continue learning")
        break
