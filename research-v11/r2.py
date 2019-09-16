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
for i in range(1330, len(history)):
# for i in range(60, len(history)):
    should_buy_close = False
    subset = history[['date','open','high','low','close','change']][i-lookback_size:i]
    trading_date = subset['date'].iloc[-1]
    close   = subset['close'].iloc[-1]
    open    = subset['open'].iloc[-1]
    low     = subset['low'].iloc[-1]
    high    = subset['high'].iloc[-1]
    last_change = subset['change'].iloc[-1]*100

    ideal_buy_price = np.min(subset['close'][:-3].values)
    bar_body = abs(open-close)/subset['close'].iloc[-2]
    upline = abs(high - max([open,close]))/subset['close'].iloc[-2]

    trend = 'down'
    v_min, v_max = np.min(subset['close'][-10:]), np.max(subset['close'][-10:])
    v_min_id, v_max_id = subset['close'][-10:][subset.close==v_min].index[-1],subset['close'][-10:][subset.close==v_max].index[-1]
    if v_max_id<=v_min_id: trend ='up'

    # if skip_until_price_lower_than <= close and skip_until_price_lower_than>0:
    #     skip_days=10
    # else:
    #     skip_until_price_lower_than = 0


    if position == 'empty':
        if subset['change'].iloc[-1]>=0.015 \
            and subset['change'].iloc[-1]<=0.07 \
            and subset['change'].iloc[-2]<=-0.005:
            should_buy_close = True
            should_max_hold_days = 10

        # if subset['change'].iloc[-2]<=-0.07 \
        #     and subset['change'].iloc[-1]>=0.01:
        #     should_buy_close = True
        #     should_max_hold_days = 10

        #一绿吃掉5日涨幅则买入 并且属于上升波段
        # if subset['close'][-5:-1].min() > subset['close'].iloc[-1].min() \
        #     and last_change <-0.02 and trend=='up':
        #     should_buy_close = True
        #     should_max_hold_days = 10

    if position == 'full':
        profit = (close - bought_price)/bought_price*100
        if profit>=10 or hold_days>=should_max_hold_days or last_change<-1:
            should_sell=True

        #如果上影线大于实体
        if upline>bar_body and bar_body>=0.005 :
            should_sell=True

        if subset['change'].iloc[-1]<0 \
            and subset['change'].iloc[-2]>0 \
            and subset['change'].iloc[-3]<0 \
            and subset['change'].iloc[-4]<0:
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
                fund += bought_amount*close*0.9985
                bought_amount = 0
                should_sell = False
                action="sold"
                total_session+=1
                if profit>0: win_session+=1
                # v_min2, v_max2 = np.min(subset['close'][-60:]), np.max(subset['close'][-60:])
                # if close == v_max2:
                #     recent_changes = (v_max2 - v_min2) / v_min2
                #     if recent_changes>0.15 :
                #         skip_until_price_lower_than=close* (1-recent_changes*0.5)


    profit = ((fund + bought_amount*close - init_fund) / init_fund) * 100
    wr = 0
    if total_session>0:
        wr = win_session/total_session*100
    print("\tdays:{:02d}\t total: {:6.2f}%\t wr:{:5.2f}%\t {}".format(hold_days, profit,wr,action))
    action =""

print(SECURITY)
print("win: {}\t totol:{}\t".format(win_session,total_session))
