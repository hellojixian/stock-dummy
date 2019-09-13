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

lookback_size = 30
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
for i in range(lookback_size, len(history)):
    should_buy_close = False
    subset = history[['date','open','high','low','close','change']][i-lookback_size:i]
    trading_date = subset['date'].iloc[-1]
    close = subset['close'].iloc[-1]
    low = subset['low'].iloc[-1]
    last_change = subset['change'].iloc[-1]*100
    tps = find_turn_points(subset)
    trend=''
    if len(tps)>=1:
        if tps[-1] >= close:
            trend='down'
        else:
            trend='up'
    within_days-=1

    if position == 'empty':
        if subset['low'].iloc[-5]>=subset['low'].iloc[-3] \
            and subset['low'].iloc[-4] >= subset['low'].iloc[-3] \
            and subset['low'].iloc[-3] <= subset['low'].iloc[-1] \
            and subset['low'].iloc[-2] <= subset['low'].iloc[-1] \
            and trend=='up':
            # ideal_buy_price = subset['low'].iloc[-1]
            # within_days = 3

        # if low <= ideal_buy_price*0.99 and within_days>0:
            should_buy_close = True
            should_max_hold_days = 3

        # if last_change==0 and trend!='up':
        #     should_buy_close = True
        #     should_max_hold_days =1

    if position == 'full':
        profit = (close - bought_price)/bought_price*100
        if profit>=5 or hold_days>=should_max_hold_days or last_change<-2:
            should_sell=True
        if last_change<-9:
            should_sell=False
    else:
        profit =0

    print("{}\t chg:{:6.2f}\t pft:{:6.2f}\t low:{:5.2f}\t close:{:5.2f}".format(
        trading_date,last_change,profit, low, close), end="")

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
                fund += bought_amount*close
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
# find turn point, or dense point
# step_len = np.abs(history['close'] - history['close'].shift(periods=1)).mean()
# subset = history[['open','high','low','close']][:60]
# close = subset['close'].iloc[-1]
# prices = subset.values.flatten()
# prices = np.sort(prices)
# prices = np.round(prices/step_len)
# dist = pd.Series(prices).value_counts()
# dist.index *= step_len
# dist.index = np.round(dist.index,2)
# dist = dist.sort_index()
# tps = find_turn_points(subset)
# print(tps, close)




sys.exit()
