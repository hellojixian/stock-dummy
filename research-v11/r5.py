#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os
import json

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

    def __init__(self,dataset=None):
        self.stop_winning = None
        self.stop_lossing = None
        self.max_holding_days = None
        self.settings = {}
        self.settings_filename = os.path.join('settings',"cfg_"+self.__class__.__name__ + '.json')
        self.load()
        self.pop_size = 100
        self.pop = self.gen_DNAset()
        return

    def gen_DNAset(self):
        dna_list = []
        for i in range(self.pop_size):
            dna = []
            for setting in self.settings_range:
                vmin,vmax,step = self.settings_range[setting][0],\
                                self.settings_range[setting][1],\
                                self.settings_range[setting][2]
                vlimit = (vmax-vmin)/step
                value = int(np.round(np.random.rand()*vlimit,0))*step+vmin
                dna.append(value)
            dna_list.append(dna)
            # print(dna)
        return dna_list

    def make_kids(self):
        # generate empty kid holder
        kids = {'DNA': np.empty((self.n_kid, self.DNA_size))}
        kids['mut_strength'] = np.empty_like(kids['DNA'])

        for kv, ks in zip(kids['DNA'], kids['mut_strength']):
            # crossover (roughly half p1 and half p2)
            p1, p2 = np.random.choice(np.arange(self.pop_size), size=2, replace=False)

            cp = np.random.randint(0, 2, self.DNA_size, dtype=np.bool)  # crossover points
            kv[cp] = self.pop['DNA'][p1, cp]
            kv[~cp] = self.pop['DNA'][p2, ~cp]
            ks[cp] = self.pop['mut_strength'][p1, cp]
            ks[~cp] = self.pop['mut_strength'][p2, ~cp]

            # mutate (change DNA based on normal distribution)
            ks[:] = np.maximum(ks + (np.random.randn(*ks.shape)-0.5), 0.)    # must > 0
            kv += ks * np.random.randn(*kv.shape)
            kv[:] = np.clip(kv, *self.DNA_bound)    # clip the mutated value
        return kids

    def should_buy(dataset):
        decision = False
        return
    def should_sell(self, dataset):
        return

    def load(self):
        with open(self.settings_filename) as json_file:
            self.settings = json.load(json_file)
        return

    def save(self):
        with open(self.settings_filename, 'w') as outfile:
            json.dump(self.settings, outfile)
        return

    def evolve(self,dataset):
        # 生成一批新的DNA，然后逐个回测，保留最优解
        self.kill_bad(self.make_kids())
        self.settings = self.parseDNA(self.pop["DNA"][-1])
        return

    def evalution(self, dataset):
        # 返回本策略对当前结果的胜率把握
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
            min_days_after_high - 创新高后最少震荡了几日
            max_drop_after_high - 创新高后最大回撤了多少
            min_days_high - 多少日的新高
            stop_win_rate - 止盈比率多少    since ideal lowest
            stop_loss_rate- 止损比率是多少  since bought price
    '''
    conf = 'settings/ZhuiZhang_settings.conf'

    def __init__(self,dataset=None):

        self.settings_range = {
            "min_days_after_high" : [2,10,1],
            "max_droprate_after_high" : [1,5,0.5],
            "min_days_high" : [5,15,1],
            "stop_win_rate" : [1,15,0.5],
            "stop_loss_rate" : [-10,-1,0.5]
        }

        super().__init__()
        return

    def parseDNA(self,DNA):
        pass

    def backtest(self, dataset):
        report = {
            "win_rate": 0,
            "profit": 0,
            "max_drawback":0,
            "alpha": 0
        }
        return report




SECURITY = 'sz000001'
columns = ['date','open','high','low','close','change']
data_file = 'data/stock_data/{}.csv'.format(SECURITY)
history = pd.read_csv(data_file)
history = history[columns]
history = history.sort_values(by=['date'])
history = history[1000:]

stg = ZhuiZhangStg()
# stg.evolve(history)
stg.gen_DNAset()
