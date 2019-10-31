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
MAX_POP_SIZE = 20
NEW_KIDS = 60
MUT_STRENGTH = 6
MIN_WIN_RATE = 0.7

STRATEGY_MIN_rounds = 2 #策略最少匹配几次交易
LINE_WIDTH=100

class strategy(object):

    def __init__(self,dataset=None):
        self.stop_winning = None
        self.stop_lossing = None
        self.max_holding_days = None
        self.training_set = None

        self.current_settings = None
        self.current_settings_id = None

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
        return self.backtest(setting)['score']

    def parseDNA(self, DNA):
        setting = {}
        i = 0
        for s in self.settings_range:
            key = list(s.keys())[0]
            setting[key] = DNA[i]
            i+=1
        return setting

    def evolve(self,training_set):
        # 生成一批新的DNA，然后逐个回测，保留最优解
        improving=0
        # pre-process data with existing knowledge before evolve it
        self.training_set = self.preprocess_dataset(training_set)

        self.kill_bad(self.make_kids())

        new_settings = self.parseDNA(self.pop[-1])
        new_result = self.backtest(new_settings)
        if self.latest_best_settings is not None:
            old_result = self.backtest(self.latest_best_settings)
            improving = new_result['score'] - old_result['score']
        else:
            improving = new_result['score']

        self.rounds = self.rounds[['kb_id','bought_date','sold_date','holding_days','round_profit','sold_reason']]
        print("Trading transcations:")
        print("-"*LINE_WIDTH)
        print(self.rounds)
        print("-"*LINE_WIDTH)

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
            if self.should_save_knowledge(new_result):
                self.save_knowledge()
        else:
            # adjust pop seetings
            if self.pop_size < MAX_POP_SIZE:
                self.pop_size += POP_SIZE
                self.n_kids += int(NEW_KIDS/2)
                self.mut_strength = MUT_STRENGTH*2
                print("Adjusted POP_SIZE to {}".format(self.pop_size))
            else:
                # save last best settings into knowledge base
                if new_result['new_strategy']['rounds']>0 \
                    and new_result['new_strategy']['win_rate']>=0.7:
                    self.save_knowledge()
                else:
                    print('Early stop learning')
                    return False

        print("="*LINE_WIDTH)
        return True

    def should_save_knowledge(self,result):
        decision = False
        node = result['new_strategy']
        if node['win_rate']<1 and node['win_rate']>=0.7 \
            and node['holding_days']>node['rounds']*1.5:
            decision = True
        if node['rounds']>0 and node['profit']/node['rounds']>0.1:
            decision = True
        return decision

    def save_knowledge(self):
        kb_id = str(uuid.uuid4())
        self.knowledge_base[kb_id] = self.latest_best_settings.copy()
        self.save()
        self.latest_best_settings = None
        self.pop_size = POP_SIZE
        self.n_kids = NEW_KIDS
        self.mut_strength = MUT_STRENGTH
        self.pop = self.gen_DNAset()
        print("Knowledge base updated:  {} items".format(len(self.knowledge_base.keys())))
        return

    def should_buy(self, subset, new_settings=None):
        return self.test_buy_setting(subset, new_settings)

    def should_sell(self, subset):
        if self.forbidden_sell(subset): return False
        decision = False
        settings = self.current_settings

        close = subset['close'].iloc[-1]
        last_close = subset['close'].iloc[-2]
        change = (close - last_close) / last_close
        drop_from_high_after_bought = (close - self.highest_price_after_bought) / self.highest_price_after_bought
        grow_from_low_after_bought = (close - self.lowset_price_after_bought) / self.lowset_price_after_bought

        max_holding_days = int(settings['max_holding_days'])
        early_stop_win_rate = settings['early_stop_win_rate']*0.01
        early_stop_lose_rate = settings['early_stop_win_rate']*0.01

        profit = (close - self.bought_price )/self.bought_price

        if close >= self.stop_winning:
            self.sell_reason = 'stop_winning'
            decision = True
        elif close <= self.stop_lossing:
            self.sell_reason = 'stop_lossing'
            assert(profit<0)
            decision = True
        elif grow_from_low_after_bought >= early_stop_win_rate:
            if profit>0:
                self.sell_reason = 'early_stop_win'
                decision = True
        elif drop_from_high_after_bought <= early_stop_lose_rate:
            if profit>0:
                self.sell_reason = 'early_stop_lose'
                decision = True
        elif self.holding_days >= max_holding_days:
            self.sell_reason = 'max_holding_days_exceed'
            decision = True

        if decision == True:
            self.stop_winning = None
            self.stop_lossing = None
        return decision

    def forbidden_buy(self, subset):
        change = (subset['close'].iloc[-1] - subset['close'].iloc[-2]) \
                 / subset['close'].iloc[-2]

        # 涨停禁止买入
        if change>=0.092 \
            or (change>=0.045 and change<=0.055) :
            return True
        return False

    def forbidden_sell(self, subset):
        change = (subset['close'].iloc[-1] - subset['close'].iloc[-2]) \
                / subset['close'].iloc[-2]
        # 跌停禁止卖出
        if change<=-0.092 \
            or (change<=-0.045 and change>=-0.055) :
            return True
        return False

    def load(self):
        if os.path.isfile(self.settings_filename):
            with open(self.settings_filename) as json_file:
                data = json.load(json_file)
                self.latest_best_settings = data['learning']['latest_best_settings']
                self.pop = np.array(data['learning']['pop'])
                self.knowledge_base = data['knowledge_base']
                print("Knowledge base loaded:  {} items".format(len(self.knowledge_base.keys())))
        return

    def save(self):
        self.pop = np.round(self.pop,2)
        data = { "learning":{
                    "latest_best_settings":self.latest_best_settings,
                    "pop":self.pop.tolist()
                  },
                  "knowledge_base":self.knowledge_base,
                  }
        with open(self.settings_filename, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        return

    # pre-process data with existing knowledge before evolve it
    def preprocess_dataset(self, dataset):
        self.fund = self.init_fund
        dataset['covered'] = 0
        dataset['round_profit'] = 0
        self.rounds = pd.DataFrame()
        if len(self.knowledge_base)>0:
            for i in range(dataset.shape[0]):
                if i<=self.lookback_size: continue

                subset = dataset.iloc[(i-self.lookback_size):i]
                close = subset['close'].iloc[-1]
                date = subset['date'].iloc[-1]
                idx = subset.index[-1]

                # update fund
                dataset.loc[idx,'round_profit'] = 0
                if self.bought_amount > 0:
                    self.holding_days += 1
                    if close > self.highest_price_after_bought:
                        self.highest_price_after_bought = close
                    if close < self.lowset_price_after_bought:
                        self.lowset_price_after_bought = close
                    # mark covered date
                    dataset.loc[idx,'covered'] = 1
                    if self.should_sell(subset):
                        stat = {
                            'bought_date': self.bought_date,
                            'sold_date': date,
                            'sold_reason': self.sell_reason,
                            'holding_days':  self.holding_days,
                            'round_profit': (close-self.bought_price)/self.bought_price,
                            'kb_id': self.current_settings_id
                        }
                        dataset.loc[idx,'round_profit'] = stat['round_profit']
                        dataset.loc[idx,'covered'] = 0
                        self.bought_price = 0
                        self.highest_price_after_bought = 0
                        self.lowset_price_after_bought = 0
                        self.fund += self.bought_amount*close
                        self.bought_amount = 0
                        self.bought_date = None
                        self.sell_reason = None
                        self.current_settings = None
                        self.current_settings_id = None
                        self.holding_days = 0
                        self.rounds = self.rounds.append(pd.Series(stat),ignore_index=True)

                if self.bought_amount == 0:
                    for kb_id in self.knowledge_base:
                        settings = self.knowledge_base[kb_id]
                        if self.test_buy_setting(subset, settings, kb_id):
                            dataset.loc[idx,'covered'] = 1
                            self.bought_date = date
                            self.bought_price = close
                            self.highest_price_after_bought = close
                            self.lowset_price_after_bought = close
                            self.holding_days = 0
                            self.bought_amount = int(self.fund / (close *100))*100
                            self.fund -= self.bought_amount * close
                            break

            self.fund += self.bought_amount * dataset['close'].iloc[-1]
            self.bought_amount = 0
        return dataset

    def backtest(self, settings=None):
        self.fund = self.init_fund
        rounds = self.rounds.copy()
        for i in range(self.training_set.shape[0]):
            if i<=self.lookback_size: continue
            subset = self.training_set.iloc[(i-self.lookback_size):i]
            close = subset['close'].iloc[-1]
            date = subset['date'].iloc[-1]

            if subset['round_profit'].iloc[-1]!=0:
                self.fund*=(1+subset['round_profit'].iloc[-1])

            if subset['covered'].iloc[-1] == 1:
                continue

            if self.bought_amount > 0:
                self.holding_days += 1
                if close > self.highest_price_after_bought:
                    self.highest_price_after_bought = close
                if close < self.lowset_price_after_bought:
                    self.lowset_price_after_bought = close
                if self.should_sell(subset):
                    stat = {
                        'bought_date': self.bought_date,
                        'sold_date': date,
                        'sold_reason': self.sell_reason,
                        'holding_days':  self.holding_days,
                        'round_profit': (close-self.bought_price)/self.bought_price,
                        'kb_id': self.current_settings_id
                    }
                    self.bought_price = 0
                    self.highest_price_after_bought = 0
                    self.lowset_price_after_bought = 0
                    self.fund += self.bought_amount*close
                    self.bought_amount = 0
                    self.bought_date = None
                    self.sell_reason = None
                    self.current_settings = None
                    self.current_settings_id = None
                    self.holding_days = 0
                    rounds = rounds.append(pd.Series(stat),ignore_index=True)

            if self.bought_amount == 0:
                if self.should_buy(subset, settings):
                    self.bought_date = date
                    self.bought_price = close
                    self.highest_price_after_bought = close
                    self.lowset_price_after_bought = close
                    self.holding_days = 0
                    self.bought_amount = int(self.fund / (close *100))*100
                    self.fund -= self.bought_amount * close

        self.fund += self.bought_amount * self.training_set['close'].iloc[-1]
        self.bought_amount = 0


        win_rate, profit,profit_per_day,profit_per_round,holding_days=0,0,0,0,0
        new_strategy_profit,new_strategy_win_rate, \
        new_strategy_holding_days,new_strategy_round_count=0,0,0,0
        baseline_profit = (self.training_set['close'].iloc[-1] - self.training_set['close'].iloc[self.lookback_size] )/ self.training_set['close'].iloc[self.lookback_size]
        if rounds.shape[0]>0:
            profit = (self.fund - self.init_fund) / self.init_fund
            win_rate = rounds[rounds.eval('round_profit>0')].shape[0] / rounds.shape[0]
            holding_days = rounds['holding_days'].sum()

            ns_rounds = rounds[rounds.eval('kb_id=="_"')]
            if ns_rounds.shape[0]>=STRATEGY_MIN_rounds:
                new_strategy_profit = 1
                for _, row in ns_rounds.iterrows():
                    new_strategy_profit *= (1+row['round_profit'])
                new_strategy_profit = new_strategy_profit - 1
                new_strategy_win_rate = ns_rounds[ns_rounds.eval('round_profit>0')].shape[0] / ns_rounds.shape[0]
                new_strategy_holding_days = ns_rounds['holding_days'].sum()
                new_strategy_round_count = ns_rounds.shape[0]
            rounds = rounds.sort_values(by=['bought_date'], ascending=True)

        report = {  "baseline":{
                        "baseline_profit": baseline_profit,
                        "trading_days": self.training_set.shape[0],
                    },
                    "overall":{
                        "rounds": rounds.shape[0],
                        "win_rate": win_rate,
                        "profit": profit,
                        "holding_days": holding_days,
                    },
                    "new_strategy":{
                        "rounds": new_strategy_round_count,
                        "win_rate": new_strategy_win_rate,
                        "profit": new_strategy_profit,
                        "holding_days": new_strategy_holding_days,
                    },
                    "score": new_strategy_win_rate*4 + new_strategy_profit + new_strategy_round_count/100
                }

        # 100% is overfitting
        # if new_strategy_win_rate==1: report['score']=0
        # print(rounds)
        return report
