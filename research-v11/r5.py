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
生产模式
'''

class strategy(object):

    def __init__(self,dataset=None):
        self.stop_winning = None
        self.stop_lossing = None
        self.max_holding_days = None
        self.training_set = None
        self.validation_set = None
        self.settings = {}
        self.settings_filename = os.path.join('settings',"cfg_"+self.__class__.__name__ + '.json')
        self.load()
        self.pop_size = 100
        self.n_kids = 50
        self.mut_strength = 4
        self.pop = self.gen_DNAset()
        return

    def gen_DNAset(self):
        dna_list = []
        for i in range(self.pop_size):
            dna = []
            for setting in self.settings_range:
                settings = list(setting.values())[0]
                vmin,vmax,step = settings[0],settings[1],settings[2]
                vlimit = (vmax-vmin)/step
                value = np.random.randint(0, vlimit+1)*step+vmin
                dna.append(value)
            dna_list.append(dna)
        dna_list = np.array(dna_list)
        return dna_list

    def make_kids(self):
        dna_size = len(self.pop[0])
        kids = np.empty((self.n_kids, dna_size))
        for kid in kids:
            p1, p2 = np.random.choice(np.arange(len(self.pop)), size=2, replace=False)
            cp = np.random.randint(0, 2, dna_size, dtype=np.bool)

            kid[cp] = self.pop[p1, cp]
            kid[~cp] = self.pop[p2, ~cp]

            # mutation
            i = 0
            for setting in self.settings_range:
                settings = list(setting.values())[0]
                vmin,vmax,step = settings[0],settings[1],settings[2]
                mut = int(np.random.uniform(-self.mut_strength,self.mut_strength))
                v = kid[i] + step*mut
                kid[i] = np.clip(v, vmin, vmax)
                i+=1
        return kids

    def kill_bad(self, kids):
        self.pop = np.vstack((self.pop, kids))
        fitness = self.get_fitness(self.pop)            # calculate global fitness
        idx = np.arange(self.pop.shape[0])
        good_idx = idx[fitness.argsort()][-self.pop_size:]   # selected by fitness ranking (not value)
        self.pop = self.pop[good_idx]
        return

    def get_fitness(self, dna_series):
        v = np.zeros(len(dna_series))
        for i in range(len(dna_series)):
            score = self.evaluate_dna(dna_series[i])['score']
            v[i]=score
        return v

    def evaluate_dna(self,DNA):
        setting = self.parseDNA(DNA)
        report = self.backtest(self.training_set, setting)
        return report

    def evolve(self,training_set,validation_set=None):
        # 生成一批新的DNA，然后逐个回测，保留最优解
        self.training_set = training_set
        self.validation_set = validation_set
        self.kill_bad(self.make_kids())
        self.settings = self.pop[-1]
        return


    def should_buy(dataset):
        decision = False
        return
    def should_sell(self, dataset):
        return

    def load(self):
        if os.path.isfile(self.settings_filename):
            with open(self.settings_filename) as json_file:
                self.settings = json.load(json_file)
        return

    def save(self):
        with open(self.settings_filename, 'w') as outfile:
            json.dump(self.settings, outfile)
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
        self.settings_range = [
            {"min_days_after_high" : [2,10,1]},
            {"max_droprate_after_high" : [1,5,0.5]},
            {"min_days_high" : [5,15,1]},
            {"stop_win_rate" : [1,15,0.5]},
            {"stop_loss_rate" : [-10,-1,0.5]}
        ]
        super().__init__()
        return

    def parseDNA(self, DNA):
        setting = {}
        i = 0
        for s in self.settings_range:
            key = list(s.keys())[0]
            setting[key] = DNA[i]
            i+=1
        return setting

    def backtest(self, dataset, settings=None):
        report = {
            "win_rate": 0,
            "profit": 0,
            "max_drawback":0,
            "alpha": 0,
            "score": 0
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
stg.gen_DNAset()
stg.evolve(training_set=history, validation_set=history)
