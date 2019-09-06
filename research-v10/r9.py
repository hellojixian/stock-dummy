#!/usr/bin/env python3
import datetime
import pandas as pd
import math, sys, os

from lib.jqdata import *
# from lib.func import *

debug = 'OFF'

LOOKBACK_SIZE = 1000
SAMPLE_SIZE = 1000
TREND_OBSERVE_LEN = 75

start_date=datetime.date(2008,4,15)
end_date=datetime.date(2013,4,15)
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

security_list = get_all_securites().sample(SAMPLE_SIZE)
row = security_list.iloc[29]
security = row['security']

init_fund = 100000
skip_days = 0
hold_days = 0
bought_amount,bought_price = 0,0
position = 'empty'
should_buy, should_sell = False, False
should_buy_open = False

fund = init_fund
trading_dates = get_all_trading_dates()

def _calc_down_days(values):
    values = list(values)
    values.reverse()

    days = 0
    for i in range(len(values)):
        v=values[i]
        if v>0: break
        days+=1
    return days


i=0
for trading_date in trading_dates:
    i+=1
    # if i< 770:continue
    backlook = 8
    history = get_price(security, end_date=trading_date, count=backlook, skip_paused=True)
    if history.shape[0]<backlook: continue
    history['open_jump'] = (history['open'].shift(periods=0) - history['close'].shift(periods=1) )/history['close'].shift(periods=1)*100
    history['change'] = (history['close'].shift(periods=0) - history['close'].shift(periods=1) )/history['close'].shift(periods=1)*100
    history['down_days'] = history['change'].rolling(window=7).apply(_calc_down_days,raw=True)

    open_jump = history.iloc[-1]['open_jump']
    open = history.iloc[-1]['open']
    close = history.iloc[-1]['close']
    last_change = history.iloc[-1]['change']
    prev_change = history.iloc[-2]['change']
    down_days = history.iloc[-1]['down_days']


    if position == 'empty':
        if (open_jump>=2 and open_jump<=8):
            should_buy_open = True
        # if open_jump<=-2 and open_jump>=-9:
        #     should_buy_open = True

        if last_change>=0.5 and prev_change<last_change:
            should_buy=True

        # if up_days>=4 and last_change<=0:
        #     should_buy=True


    profit = (close - bought_price)/bought_price*100
    if position == 'full':
        if profit>=12 or hold_days>=4 or last_change<1.5:
            should_sell=True

    print("{:03d}\t{}\t p1:{:6.2f}\t p2:{:6.2f}\t profit:{:6.2f}\t close:{}".format(
        i,trading_date,open_jump,profit,last_change, close), end="")

    if skip_days>0:
        skip_days-=1
        should_buy,should_buy_open=False,False
    else:
        if position == 'empty':
            if should_buy:
                bought_price = close
            if should_buy_open:
                bought_price = open

            if should_buy or should_buy_open:
                bought_amount = fund / close
                fund -= bought_amount*close
                position = 'full'
                should_buy = False
                should_buy_open = False


        if position == 'full':
            hold_days +=1
            if should_sell:
                hold_days = 0
                position = 'empty'
                fund += bought_amount*close
                bought_amount = 0
                should_sell = False

    profit = ((fund + bought_amount*close - init_fund) / init_fund) * 100
    print("\tdays:{:03d}\t profit: {:6.2f}%".format(hold_days, profit))
print(security)
