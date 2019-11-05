#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob
import json
import pprint
import uuid
import progressbar

from .strategies import strategies

POP_SIZE = 10
MAX_POP_SIZE = 20
NEW_KIDS = 60
MUT_STRENGTH = 6
MIN_WIN_RATE = 0.7

STRATEGY_MIN_rounds = 2 #策略最少匹配几次交易
LINE_WIDTH=100

class backtest(object):
    def __init__(self,dataset=None):
        self.dataset = dataset
        self.init_fund = 100000
        self.fund = 0
        self.holding_days = 0
        self.bought_price = None
        self.bought_amount = 0
        return

    def run(self):
        self.fund = self.init_fund
        rounds = self.rounds.copy()
        for i in range(self.dataset.shape[0]):
            if i<=self.lookback_size: continue
            subset = self.dataset.iloc[(i-self.lookback_size):i]
            close = subset['close'].iloc[-1]
            date = subset['date'].iloc[-1]

            if subset['round_profit'].iloc[-1]!=0:
                self.fund*=(1+subset['round_profit'].iloc[-1])

            if self.bought_amount > 0:
                self.holding_days += 1
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

                    self.fund += self.bought_amount*close
                    self.bought_amount = 0
                    self.bought_date = None

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

        self.fund += self.bought_amount * self.dataset['close'].iloc[-1]
        self.bought_amount = 0

        win_rate, profit,profit_per_day,profit_per_round,holding_days=0,0,0,0,0
        new_strategy_profit,new_strategy_win_rate, \
        new_strategy_holding_days,new_strategy_round_count=0,0,0,0
        baseline_profit = (self.dataset['close'].iloc[-1] - self.dataset['close'].iloc[self.lookback_size] )/ self.dataset['close'].iloc[self.lookback_size]
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
        return report
