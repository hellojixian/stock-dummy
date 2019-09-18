#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os

SECURITY = 'sz002627'
# SECURITY = 'sz002620'
np.random.seed(0)

def find_turn_points(subset):
    subset['prev_1'] = subset['low'].shift(periods=1)
    subset['prev_2'] = subset['low'].shift(periods=2)
    subset['fu_1'] = subset['low'].shift(periods=-1)
    subset['fu_2'] = subset['low'].shift(periods=-2)
    query = "prev_2>prev_1 & prev_1>low & low<fu_1 & fu_1<fu_2"
    tps = subset[subset.eval(query)]['low'].values
    return tps

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

columns = ['date','open','high','low','close','change','money','turnover']
data_file = 'data/stock_data/{}.csv'.format(SECURITY)
history = pd.read_csv(data_file)
history = history[columns]
history = history.sort_values(by=['date'])

# transform
history = history.drop(columns=['money'])
history['turnover'] = np.round(history['turnover']*100,2)
history['change'] = np.round(history['change']*100,2)
history['bar'] = np.round((history['close'] - history['open']) / history['close'].shift(periods=1)*100,2)
history['open_jump'] = np.round((history['open']-history['close'].shift(periods=1)) / history['close'].shift(periods=1)*100,2)
history['amp'] = np.round((history['high']-history['low']) / history['close'].shift(periods=1)*100,2)
history['upline'] = np.round((history['high']-history['open']) / history['close'].shift(periods=1)*100,2)
history['downline'] = np.round((history['open']-history['low']) / history['close'].shift(periods=1)*100,2)

slices=10
for i in range(0,slices):
    print("{:3d}  amp:{}\t bar:{}\t chg:{}\t open:{}\t  turnover:{}\t".format(i,
        np.round(history['amp'].quantile(i/slices),2),
        np.round(history['bar'].quantile(i/slices),2),
        np.round(history['change'].quantile(i/slices),2),
        np.round(history['open_jump'].quantile(i/slices),2),
        np.round(history['turnover'].quantile(i/slices),2),
        ))
assert(False)

lookback_size = 60
init_fund = 100000
skip_days = 0
hold_days = 0
skip_until = 0
bought_amount,bought_price = 0,0
position = 'empty'
should_buy_close, should_sell = False, False

total_session = 0
win_session=0
fund = init_fund
ideal_buy_price = 0
within_days=0
recent_changes,skip_until_price_lower_than = 0,0
drop_rate = 0
for i in range(1330, len(history)):
# for i in range(60, len(history)):
    should_buy_close = False
    subset = history[i-lookback_size:i]
    trading_date = subset['date'].iloc[-1]
    close   = subset['close'].iloc[-1]
    open    = subset['open'].iloc[-1]
    low     = subset['low'].iloc[-1]
    high    = subset['high'].iloc[-1]
    last_change = subset['change'].iloc[-1]*100
    turnover = subset['turnover'].iloc[-1]

    prev_change = subset['change'].iloc[-2]*100
    prev_close = subset['close'].iloc[-2]

    r = last_change/turnover

    if position == 'empty':
        if subset['change'].iloc[-1]>=0.015 \
            and subset['change'].iloc[-1]<=0.07 \
            and subset['change'].iloc[-2]<=-0.005:
            should_buy_close = True
            should_max_hold_days = 10

        if last_change>0 and prev_change<0:
            lowest_since_days = 1
            for i in range(2,60):
                if subset['close'][(-i):-1].min() < prev_close:
                    # highest = subset['close'][(-i):].max()
                    # drop_rate = (highest - subset['close'][(-i):].min()) / highest
                    break
                lowest_since_days+=1
            print("{} {:.4f}".format(lowest_since_days, drop_rate))

            if lowest_since_days>=5:
                should_buy_close = True
                should_max_hold_days = 3

    if position == 'full':
        profit = (close - bought_price)/bought_price*100
        if profit>=10 or hold_days>=should_max_hold_days or last_change<0.:
            should_sell=True

        if last_change<-9:
            should_sell=False
    else:
        profit =0

    print("{}\t chg:{:6.2f}\t pft:{:6.2f}\t r:{:5.2f}\t close:{:5.2f}".format(
        trading_date,last_change,profit, r, close), end="")

    if skip_days>0 :
        skip_days-=1
        should_buy_close = False
    else:
        skip_until = 0
        action =""
        if position == 'empty':
            if should_buy_close:
                bought_price = close

            if should_buy_close:
                bought_amount = fund / close
                fund -= bought_amount*close
                position = 'full'
                should_buy_close = False
                should_buy_open = False
                action="bought"


        if position == 'full':
            hold_days +=1
            if should_sell:
                hold_days = 0
                position = 'empty'
                fund += bought_amount*close*0.9985
                bought_amount = 0
                should_sell = False
                action="sold"
                total_session+=1
                if profit>0: win_session+=1


    profit = ((fund + bought_amount*close - init_fund) / init_fund) * 100
    wr = 0
    if total_session>0:
        wr = win_session/total_session*100
    print("\tdays:{:02d}\t total: {:6.2f}%\t wr:{:5.2f}%\t {}".format(hold_days, profit,wr,action))
    action =""

print(SECURITY)
print("win: {}\t totol:{}\t".format(win_session,total_session))
