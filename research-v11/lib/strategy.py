#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob
import json
import pprint
import uuid
import progressbar

POP_SIZE = 10
MAX_POP_SIZE = 30
NEW_KIDS = 60
MUT_STRENGTH = 6
MIN_WIN_RATE = 0.7

LINE_WIDTH=100

class strategy(object):

    def __init__(self,dataset=None):
        self.stop_winning = None
        self.stop_lossing = None
        self.max_holding_days = None
        self.training_set = None
        self.validation_set = None
        self.current_settings = None
        self.latest_best_settings = None
        self.knowledge_base = {}
        self.knowledge_mem = {}
        self.settings_filename = os.path.join('settings',"cfg_"+self.__class__.__name__ + '.json')
        self.pop = []
        self.load()
        self.pop_size = POP_SIZE
        self.n_kids = NEW_KIDS
        self.mut_strength = MUT_STRENGTH
        if len(self.pop)==0: self.pop = self.gen_DNAset()

        self.init_fund = 100000
        self.fund = 0
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
        bar = progressbar.ProgressBar(max_value=len(dna_series))
        for i in range(len(dna_series)):
            bar.update(i+1)
            score = self.evaluate_dna(dna_series[i])
            v[i]=score
        print("")
        print('-'*LINE_WIDTH)
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
        improving=0
        self.training_set = training_set
        self.validation_set = validation_set
        self.kill_bad(self.make_kids())

        new_settings = self.parseDNA(self.pop[-1])
        new_result = self.backtest(training_set[0], new_settings)
        if self.latest_best_settings is not None:
            old_result = self.backtest(training_set[0], self.latest_best_settings)
            improving = new_result['score'] - old_result['score']
        else:
            improving = new_result['score']

        pprint.pprint({
            'new_setting':new_settings,
            'new_result':new_result,
            'improving':improving })

        if improving>0:
            self.latest_best_settings = new_settings.copy()
            self.save()
            print("[saved]")
            self.pop_size = POP_SIZE
            self.n_kids = NEW_KIDS
            self.mut_strength = MUT_STRENGTH
        else:
            # adjust pop seetings
            if self.pop_size < MAX_POP_SIZE:
                self.pop_size += POP_SIZE
                self.n_kids += int(NEW_KIDS/2)
                self.mut_strength = MUT_STRENGTH*2
                print("Adjusted POP_SIZE to {}".format(self.pop_size))
            else:
                # save last best settings into knowledge base
                if new_result['win_rate']>= MIN_WIN_RATE:
                    kb_id = str(uuid.uuid4())
                    self.knowledge_base[kb_id] = self.latest_best_settings.copy()
                    self.save()
                    self.pop = self.gen_DNAset()
                    self.latest_best_settings = None
                    self.pop_size = POP_SIZE
                    self.n_kids = NEW_KIDS
                    self.mut_strength = MUT_STRENGTH
                    print("Knowledge base updated:  {} items".format(len(self.knowledge_base.keys())))
                else:
                    print('Early stop learning')
                    return False


        print("="*LINE_WIDTH)
        return True

    def should_buy(dataset):
        decision = False
        return decision

    def should_sell(self, dataset):
        decision = False
        return decision

    def load(self):
        if os.path.isfile(self.settings_filename):
            with open(self.settings_filename) as json_file:
                data = json.load(json_file)
                self.latest_best_settings = data['latest_best_settings']
                self.knowledge_base = data['knowledge_base']
                self.pop = np.array(data['pop'])
                print("Knowledge base loaded:  {} items".format(len(self.knowledge_base.keys())))
        return

    def save(self):
        self.pop = np.round(self.pop,2)
        data = { "latest_best_settings":self.latest_best_settings,
                 "knowledge_base":self.knowledge_base,
                 "pop":self.pop.tolist() }
        with open(self.settings_filename, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        return

    def backtest(self, dataset, settings=None):
        self.fund = self.init_fund
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
                        'bought_date': self.bought_date,
                        'sold_date': date,
                        'holding_days':  self.holding_days,
                        'session_profit': (close-self.bought_price)/self.bought_price,
                        'kb_id': self.current_settings['kb_id']
                    }
                    self.bought_price = 0
                    self.fund += self.bought_amount*close
                    self.bought_amount = 0
                    self.bought_date = None
                    self.current_settings = None
                    self.holding_days = 0
                    sessions = sessions.append(pd.Series(stat),ignore_index=True)

            if self.bought_amount == 0:
                if self.should_buy(subset, settings):
                    self.bought_date = date
                    self.bought_price = close
                    self.holding_days = 0
                    self.bought_amount = int(self.fund / (close *100))*100
                    self.fund -= self.bought_amount * close

        self.fund += self.bought_amount*close
        self.bought_amount = 0


        win_rate, profit,profit_per_day,profit_per_session,holding_days=0,0,0,0,0
        baseline_profit = (dataset['close'].iloc[-1] - dataset['close'].iloc[self.lookback_size] )/ dataset['close'].iloc[self.lookback_size]
        if sessions.shape[0]>0:
            profit = (self.fund - self.init_fund) / self.init_fund
            win_rate = sessions[sessions.eval('session_profit>0')].shape[0] / sessions.shape[0]
            holding_days = sessions['holding_days'].sum()

            ns_sessions = sessions[sessions.eval('kb_id=="_"')]
            new_strategy_profit = 1
            for _, row in ns_sessions.iterrows():
                new_strategy_profit *= (1+row['session_profit'])

            new_strategy_profit = new_strategy_profit - 1
            new_strategy_win_rate = ns_sessions[ns_sessions.eval('session_profit>0')].shape[0] / ns_sessions.shape[0]
            new_strategy_holding_days = ns_sessions['holding_days'].sum()

        report = {  "baseline":{
                        "baseline_profit": baseline_profit,
                        "trading_days": dataset.shape[0],
                    },
                    "overall":{
                        "sessions": sessions.shape[0],
                        "win_rate": win_rate,
                        "profit": profit,
                        "holding_days": holding_days,
                    },
                    "new_strategy":{
                        "sessions": ns_sessions.shape[0],
                        "win_rate": new_strategy_win_rate,
                        "profit": new_strategy_profit,
                        "holding_days": new_strategy_holding_days,
                    },
                    "score": new_strategy_profit * new_strategy_win_rate
                }


        return report
