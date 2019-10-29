#!/usr/bin/env python3
from ..strategy import strategy
import pandas as pd
import numpy as np
import math, sys, os, glob
import json
import pprint

class FanTanStrategy(strategy):
    '''
        反弹策略思路
            绿柱之后赌反弹
        超参数：
            max_holding_days - 最大持仓的天数
            min_days_low - 多少日的新低
            min_days_after_low - 创新低后几日不在破位
            max_grow_after_low - 创新低后最多反弹了多少
            safe_zone_start - 跌多少以后才触发这个策略
            safe_zone_width - 安全区域大宽度 从起点开始最多跌多少，防止那种跌吐血的
            early_stop_win_rate - 吃到大红后提前止盈
            stop_win_rate - 止盈比率多少    since ideal lowest
            stop_loss_rate- 止损比率是多少  since bought price


    '''

    def __init__(self,dataset=None):
        self.settings_range = [
            {"max_holding_days" :   [1,15,1]},
            {"min_days_low" :       [5,90,5]},
            {"min_days_after_low" : [2,5,1]},
            {"max_grow_after_low" : [1,10,0.5]},
            {"safe_zone_start" :    [15,60,5]},
            {"safe_zone_width" :    [1,60,5]},
            {"early_stop_win_rate": [1.5,9.5,0.25]},
            {"stop_win_rate" :      [1,25,0.5]},
            {"stop_loss_rate" :     [-10,1,0.5]}
        ]
        self.lookback_size = 90
        super().__init__()
        return


    def test_buy_setting(self, subset, settings, setting_id='_'):
        if self.forbidden_buy(subset): return False
        decision = False
        close = subset['close'].iloc[-1]
        last_close = subset['close'].iloc[-2]
        change = (close - last_close) / last_close

        # 初始化临时记忆
        if setting_id not in self.knowledge_mem:
            self.knowledge_mem[setting_id] = {
                'should_buy_cond_1':False,
                'should_buy_last_low':None,
                'should_buy_days_after_low':0
            }

        min_days_low = int(settings['min_days_low'])
        last_low = subset['low'].iloc[-1]
        low = subset['low'][-min_days_low:].min()
        high = subset['high'][-90:].max()

        # 判断是否属于安全区域
        safe_zone_start = settings['safe_zone_start']
        safe_zone_width = settings['safe_zone_width']
        safe_zone_end = safe_zone_start+safe_zone_width
        drop_from_high = (high - close) / high
        if drop_from_high >= safe_zone_start*0.01 and safe_zone_start<=safe_zone_end*0.01:
            # 首先要先创N日新高
            if last_low == low:
                self.knowledge_mem[setting_id]['should_buy_cond_1']=True
                self.knowledge_mem[setting_id]['should_buy_last_low']=last_low
                self.knowledge_mem[setting_id]['should_buy_days_after_low']=0

        # 如果创过新低了 继续观察N日
        min_days_after_low = int(settings['min_days_after_low'])
        max_grow_after_low = settings['max_grow_after_low']
        if self.knowledge_mem[setting_id]['should_buy_cond_1']==True:
            self.knowledge_mem[setting_id]['should_buy_days_after_low'] +=1

            if last_low > low \
                and self.knowledge_mem[setting_id]['should_buy_days_after_low'] >= min_days_after_low \
                and close <= self.knowledge_mem[setting_id]['should_buy_last_low']*(1-max_grow_after_low*0.01):
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
