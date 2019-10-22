#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os

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
    入口点是 fitting()
    用基因算法动态微调参数 然后决定去留

生产模式
    入口点就是 should_buy()
'''

class strategy(object):
    def __init__(self,dataset):
        self.stop_winning = NULL
        self.stop_lossing = NULL
        self.max_holding_days = NULL
        return

    def should_buy(dataset):
        decision = False
        return
    def should_sell(self, dataset):
        return

    def fitting(dataset):
        # 基于基因算法 生成超参数列表，然后分别测试保留最优解
        pass

    def _update(self, dataset):
        return


class ZhuiZhangStg(strategy):
    '''
        追涨策略
            红柱之后3日高位十字星
            吃到红柱就出来
            高位：N日不破掉最近M日涨幅的40%
        超参数：
            - 创新高后最少震荡了几日
            - 创新高后最大回撤了多少
            - 多少日的新高
            - 止盈比率多少
    '''
    def __init__(self,dataset):
        super().__init__()


        # load settings
        pass

    def fitting(dataset):

        pass


SECURITY = 'sz000001'
columns = ['date','open','high','low','close','change']
data_file = 'data/stock_data/{}.csv'.format(SECURITY)
history = pd.read_csv(data_file)
history = history[columns]
history = history.sort_values(by=['date'])
history = history[1000:]

ZhuiZhangStg.fitting(history)
