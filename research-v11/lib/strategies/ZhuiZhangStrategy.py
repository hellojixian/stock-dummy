#!/usr/bin/env python3
from ..strategy import strategy
import pandas as pd
import numpy as np
import math, sys, os, glob
import json
import pprint

class ZhuiZhangStrategy(strategy):
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
            {"max_holding_days" :   [3,15,1]},
            {"min_days_after_high" :[1,10,1]},
            {"min_days_high" :      [3,25,1]},
            {"max_droprate_after_high" : [1,10,0.5]},
            {"max_safe_zone" :      [0.35,1,0.05]},
            {"early_stop_win_rate": [1.5,9.5,0.25]},
            {"stop_win_rate" :      [1,25,0.5]},
            {"stop_loss_rate" :     [-10,1,0.5]}
        ]
        self.lookback_size = 90
        super().__init__()

        return


    def should_buy(self, subset, new_settings=None):

        def test_setting(subset, settings, setting_id='_'):
            decision = False
            close = subset['close'].iloc[-1]
            last_close = subset['close'].iloc[-2]
            change = (close - last_close) / last_close

            # 初始化临时记忆
            if setting_id not in self.knowledge_mem:
                self.knowledge_mem[setting_id] = {
                    'should_buy_cond_1':False,
                    'should_buy_last_high':None,
                    'should_buy_days_after_high':0
                }

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
                    self.knowledge_mem[setting_id]['should_buy_cond_1']=True
                    self.knowledge_mem[setting_id]['should_buy_last_high']=last_high
                    self.knowledge_mem[setting_id]['should_buy_days_after_high']=0

            # 如果创过新高了 继续观察N日
            min_days_after_high = int(settings['min_days_after_high'])
            max_droprate_after_high = settings['max_droprate_after_high']
            if self.knowledge_mem[setting_id]['should_buy_cond_1']==True:
                self.knowledge_mem[setting_id]['should_buy_days_after_high'] +=1
                if last_high < high \
                    and self.knowledge_mem[setting_id]['should_buy_days_after_high'] >= min_days_after_high \
                    and close >= self.knowledge_mem[setting_id]['should_buy_last_high']*(1-max_droprate_after_high*0.01):
                    decision = True
                    stop_win_rate = settings['stop_win_rate']
                    stop_loss_rate = settings['stop_loss_rate']
                    self.stop_winning = close*(1+stop_win_rate*0.01)
                    self.stop_lossing = close*(1-stop_loss_rate*0.01)

            # if np.random.randint(0,2) == 1: decision = True
            # reset state
            if decision == True:
                # after made decision, clear short term memory
                self.knowledge_mem = {}
                self.current_settings = settings
                self.current_settings_id = setting_id
            return decision

        decision = False
        # loop existing knowledge base
        for kb_id in self.knowledge_base:
            settings = self.knowledge_base[kb_id]
            decision = test_setting(subset, settings, kb_id)
            if decision == True: return decision

        # try the new setting
        if decision == False:
            settings = new_settings
            decision = test_setting(subset, settings)
            return decision

        return decision

    def should_sell(self, subset):
        decision = False
        settings = self.current_settings

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
