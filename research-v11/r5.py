#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob
import json

np.random.seed(0)


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
        self.pop = []
        self.load()
        self.pop_size = 100
        self.n_kids = 50
        self.mut_strength = 4
        if len(self.pop)==0: self.pop = self.gen_DNAset()

        self.fund = 100000
        self.holding_days = 0
        self.bought_price = None
        self.bought_amount = 0
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
            score = self.evaluate_dna(dna_series[i])
            v[i]=score
        return v

    def evaluate_dna(self,DNA):
        setting = self.parseDNA(DNA)
        scores = []
        for dataset in self.training_set:
            report = self.backtest(dataset, setting)
            scores.append(report['score'])
        return np.mean(scores)

    def parseDNA(self, DNA):
        setting = {}
        i = 0
        for s in self.settings_range:
            key = list(s.keys())[0]
            setting[key] = DNA[i]
            i+=1
        return setting

    def evolve(self,training_set,validation_set=None):
        # 生成一批新的DNA，然后逐个回测，保留最优解
        self.training_set = training_set
        self.validation_set = validation_set
        self.kill_bad(self.make_kids())
        self.settings = self.pop[-1]
        self.save()
        return

    def should_buy(dataset):
        decision = False
        return
    def should_sell(self, dataset):
        return

    def load(self):
        if os.path.isfile(self.settings_filename):
            with open(self.settings_filename) as json_file:
                data = json.load(json_file)
                self.settings = data['settings']
                self.pop = data['pop']
        return

    def save(self):
        data = { "settings":self.settings,
                 "pop":self.pop }
        with open(self.settings_filename, 'w') as outfile:
            json.dump(data, outfile)
        return



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
            {"min_days_after_high" : [2,10,1]},
            {"max_droprate_after_high" : [1,5,0.5]},
            {"min_days_high" : [5,15,1]},
            {"stop_win_rate" : [1,15,0.5]},
            {"stop_loss_rate" : [-10,-1,0.5]}
        ]
        self.lookback_size = 90
        super().__init__()
        return


    def should_buy(self, subset, settings=None):
        decision = False
        close = subset['close'].iloc[-1]
        # if np.random.randint(0,2) == 1: decision = True
        return decision

    def should_sell(self, subset, settings=None):
        decision = False
        close = subset['close'].iloc[-1]
        # if np.random.randint(0,2) == 1: decision = True

        return decision

    def backtest(self, dataset, settings=None):
        self.fund = 100000
        sessions = pd.DataFrame()

        for i in range(dataset.shape[0]):
            if i<=self.lookback_size: continue
            subset = dataset.iloc[(i-self.lookback_size):i]
            close = subset['close'].iloc[-1]
            date = subset['date'].iloc[-1]

            if self.bought_amount > 0:
                self.holding_days += 1
                if self.should_sell(subset):
                    stat = {
                        'bought_date':self.bought_date,
                        'sold_date':date,
                        'holding_days':  self.holding_days,
                        'session_profit': (close-self.bought_price)/self.bought_price
                    }
                    self.bought_price = 0
                    self.fund += self.bought_amount*close
                    self.bought_amount = 0
                    self.bought_date = None
                    self.holding_days = 0
                    sessions = sessions.append(pd.Series(stat),ignore_index=True)
                    print('fund',self.fund)

            if self.bought_amount == 0:
                if self.should_buy(subset, settings):
                    self.bought_date = date
                    self.bought_price = close
                    self.holding_days = 0
                    self.bought_amount = int(self.fund / (close *100))*100
                    self.fund -= self.bought_amount * close

        self.fund += self.bought_amount*close
        self.bought_amount = 0
        print(sessions)
        print(self.fund)
        assert(False)
        report = {  "win_rate": 0,
                    "profit": 0,
                    "max_drawback":0,
                    "alpha": 0,
                    "score": 0 }
        return report


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

train_ds = fetch_dataset(quantity=5)
val_ds = fetch_dataset(quantity=2)
stg = ZhuiZhangStg()
stg.evolve(training_set=train_ds, validation_set=val_ds)
