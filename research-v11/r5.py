#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob
import json
import pprint

from lib.strategy import strategy

np.random.seed(10)


'''
每种策略应该都对应自己的风险控制，由于买入原则不同 风险控制机制也应该不同
可以单独被训练


长策略
    下跌一个波段，前压力位
    变量：
    - 前压力位置

W底部匹配
    下跌后 反弹 再次回踩则买入

短策略
    最多持有3天
    - 瞬间超跌反弹


训练模式
生产模式
'''


class ZhuiZhangStg(strategy):
    '''
        追涨策略思路
            红柱之后3日高位十字星
            吃到红柱就出来
            高位：N日不破掉最近M日涨幅的X%
        超参数：
            min_days_after_high - 创新高后最少震荡了几日
            max_drop_after_high - 创新高后最大回撤了多少
            min_days_high - 多少日的新高
            stop_win_rate - 止盈比率多少    since ideal lowest
            stop_loss_rate- 止损比率是多少  since bought price
    '''
    conf = 'settings/ZhuiZhang_settings.conf'

    def __init__(self,dataset=None):
        self.settings_range = [
            {"max_safe_zone" :      [0.35,1,0.05]},
            {"max_holding_days" :   [5,15,1]},
            {"min_days_after_high" :[2,10,1]},
            {"max_droprate_after_high" : [1,5,0.5]},
            {"min_days_high" :      [5,15,1]},
            {"early_stop_win_rate": [1.5,9.5,0.25]},
            {"stop_win_rate" :      [1,15,0.5]},
            {"stop_loss_rate" :     [-10,-1,0.5]}
        ]
        self.lookback_size = 90
        super().__init__()

        self.should_buy_cond_1 = False
        self.should_buy_days_after_high = None
        self.should_buy_last_high = None
        return


    def should_buy(self, subset, settings=None):
        decision = False
        if settings is None: settings = self.settings
        close = subset['close'].iloc[-1]
        last_close = subset['close'].iloc[-2]
        change = (close - last_close) / last_close

        # 涨停禁止买入
        if change>=0.092 \
            or (change>=0.045 and change<=0.055) :
            return False

        min_days_high = int(settings['min_days_high'])
        last_high = subset['high'].iloc[-1]
        high = subset['high'][-min_days_high:].max()
        low = subset['high'][-90:].min()

        # 判断是否属于安全区域
        max_safe_zone = settings['max_safe_zone']
        if (close - low) / low <= max_safe_zone:
            # 首先要先创N日新高
            if last_high == high:
                self.should_buy_cond_1=True
                self.should_buy_last_high = last_high
                self.should_buy_days_after_high =0

        # 如果创过新高了 继续观察N日
        min_days_after_high = int(settings['min_days_after_high'])
        max_droprate_after_high = settings['max_droprate_after_high']
        if self.should_buy_cond_1==True:
            self.should_buy_days_after_high +=1
            if last_high < high \
                and self.should_buy_days_after_high >= min_days_after_high \
                and close >= self.should_buy_last_high*(1-max_droprate_after_high*0.01):
                decision = True
                stop_win_rate = settings['stop_win_rate']
                stop_loss_rate = settings['stop_loss_rate']
                self.stop_winning = close*(1+stop_win_rate*0.01)
                self.stop_lossing = close*(1-stop_loss_rate*0.01)

        # if np.random.randint(0,2) == 1: decision = True
        # reset state
        if decision == True:
            self.should_buy_cond_1 = False
            self.should_buy_days_after_high = None
            self.should_buy_last_high = None

        return decision

    def should_sell(self, subset, settings=None):
        decision = False
        if settings is None: settings = self.settings
        close = subset['close'].iloc[-1]
        last_close = subset['close'].iloc[-2]
        change = (close - last_close) / last_close

        # 跌停禁止卖出
        if change<=-0.092 \
            or (change<=-0.045 and change>=-0.055) :
            return False

        max_holding_days = int(settings['max_holding_days'])
        early_stop_win_rate = settings['early_stop_win_rate']
        if close >= self.stop_winning:
            decision = True
        elif close <= self.stop_lossing:
            decision = True
        elif change >= early_stop_win_rate:
            decision = True
        elif self.holding_days >= max_holding_days:
            decision = True

        if decision == True:
            self.stop_winning = None
            self.stop_lossing = None
        return decision



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
stg = ZhuiZhangStg()
for i in range(100):
    stg.evolve(training_set=train_ds, validation_set=val_ds)
