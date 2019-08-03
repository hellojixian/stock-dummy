#!/usr/bin/env python3

import pandas as pd
import numpy as np

BUY_CONDS = [
    # ["feature['pos_3']<1"],
    #
    # ["self.prev['pos_3']==7",
    #  "feature['change']<=-0.03",
    #  "feature['pos_3']<=2"],
    #
    # ["feature['pos_3']<self.prev['pos_3']",
    #  "feature['change']>0",
    #  "feature['pos_3']<=2"],
    #
    # ["self.prev2['pos_3']==7",
    #  "feature['pos_3']<=2"],
]

SELL_CONDS = [
    # ["feature['pos_3']<self.prev['pos_3']",
    #  "self.prev['pos_3']>5",
    #  "ideal_profit>0.02"],
    #
    # ["feature['pos_3']==self.prev['pos_3']",
    #  "feature['pos_3']>2",
    #  "feature['pos_3']<=4",
    #  "ideal_profit<0.02"],
    #
    # ['self.lowest_price_until_today==2',
    #  'feature["change"]<0.09',
    #  'ideal_profit>0.12'],
    #
    # ['self.prev["change"]<-0.09',
    #  'ideal_profit<0.02'],
    #
    # ['self.prev["long"]<=3',
    #  'self.prev["long"]>0.5',
    #  'self.prev["change"]<-0.09',
    #  'ideal_profit>0.065'],
    #
    # ['feature["pos_20"]==3',
    #  'ideal_profit>0.12'],
    #
    # ['self.prev_ideal_profit>0.03',
    #  'ideal_profit==0'],
    #
    # ['actual_profit<=-0.02'],
]

MAX_ALLOWED_CONTINUOUS_FAILED = 2


class Strategy(object):
    def __init__(self, cash=100000, kb=None):
        self.position = 'empty'
        self.prev = None
        self.prev2 = None
        self.bought_price = None
        self.lowest_price_since_bough = None
        self.lowest_price_until_today = None
        self.cash = cash
        self.init_cash = cash
        self.sell_conds = SELL_CONDS
        self.buy_conds = BUY_CONDS
        self.amount = 0
        self.prev_ideal_profit = None
        self.failed_count = 0
        self.actual_profit = None
        self.ideal_profit = None
        return

    def handle_data(self, feature):
        action = ""
        if self.position == 'full':
            if self.lowest_price_until_today is not None:
                self.lowest_price_until_today += 1
            if feature['close']<self.lowest_price_since_bough:
                self.lowest_price_since_bough = feature['close']
                self.lowest_price_until_today = 0
            if self.should_sell(feature) \
                and not self.should_buy(feature):
                action = "sell"
            self.ideal_profit = (feature['close'] - self.lowest_price_since_bough)/self.lowest_price_since_bough
            self.actual_profit = (feature['close'] - self.bought_price)/self.bought_price
        elif self.should_buy(feature):
            action = 'buy'
            if self.failed_count >= MAX_ALLOWED_CONTINUOUS_FAILED:
                self.failed_count = 0
                print(feature['date'],'should skip')
                action = ""

        if action =="buy":
            self.position ='full'
            self.bought_price = feature['close']
            self.lowest_price_since_bough = feature['close']
            self.lowest_price_until_today = 0
            self.prev_ideal_profit =0
            self.amount = np.round(self.cash/feature['close']/100)*100
            self.cash -= feature['close']*self.amount
            self.actual_profit = 0
            self.ideal_profit = 0
        elif action =="sell":
            if self.actual_profit>0:
                self.failed_count = 0
            else:
                self.failed_count += 1
            self.position ='empty'
            self.cash = feature['close']*self.amount
            self.amount = 0
            self.bought_price = None
            self.lowest_price_since_bough = None
            self.lowest_price_until_today = None
            self.prev_ideal_profit = None
            self.actual_profit = None
            self.ideal_profit = None

        # save history data
        self.prev2 = self.prev
        self.prev = feature
        if self.ideal_profit is not None:
            self.prev_ideal_profit = self.ideal_profit
        if self.actual_profit is not None:
            self.prev_actual_profit = self.actual_profit

        return action

    def should_buy(self, feature):
        decision = False
        if self.prev is None or self.prev2 is None:return decision

        for i in range(len(self.buy_conds)):
            settings = self.buy_conds[i]
            test = ""
            for cond in settings:
                test += cond+" and "
            test = test[:-4]
            if eval(test):
                decision = True
                break
        return decision

    def should_sell(self, feature):
        decision = False
        actual_profit = (feature['close'] - self.bought_price)/self.bought_price
        ideal_profit = (feature['close'] - self.lowest_price_since_bough)/self.lowest_price_since_bough
        feature['ideal_profit'] = ideal_profit

        for i in range(len(self.sell_conds)):
            settings = self.sell_conds[i]
            test = ""
            for cond in settings:
                test += cond+" and "
            test = test[:-4]
            if eval(test):
                decision = True
                break


        return decision

    def get_value(self, last_close):
        return self.cash + self.amount*last_close

    def get_profit(self, last_close):
        now_cash = self.cash + self.amount*last_close
        profit = (now_cash - self.init_cash )/self.init_cash
        profit = np.round(profit*100,2)
        return profit
