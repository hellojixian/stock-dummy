#!/usr/bin/env python3

import datetime
import pandas as pd
import math, sys, os
import progressbar

from lib.jqdata import *
from lib.vis import *
from lib.func import *

import matplotlib.dates as mdates
import datetime,time
import talib as ta

debug = 'OFF'

LOOKBACK_SIZE = 1000
SAMPLE_SIZE = 1000
TREND_OBSERVE_LEN = 75

filename = 'data/dataset-labeled.csv'
start_date=datetime.date(2005,4,15)
end_date=datetime.date(2018,4,15)
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

security_list = get_all_securites().sample(SAMPLE_SIZE)
# security_list = get_all_securites()
trade_date = end_date

dataset = pd.DataFrame()
i=0
for _,row in progressbar.progressbar(security_list.iterrows(),max_value=security_list.shape[0]):
    i+=1
    # if i<91: continue
    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE, skip_paused=True)
    if history.shape[0]<=10: break

    close = history['close'].iloc[-1]
    history = history.reset_index()
    history = history.rename(columns={'index':'date'})
    history['id'] = history.index
    history['change'] = (history['close'] - history['close'].shift(periods=1))/history['close'].shift(periods=1)

    _,_, history = find_buysell_points(history)
    history.loc[:, 'security'] = security

    dataset = dataset.append(history)
    # rate = history[history.action=='buy'].shape[0] / history.shape[0]
    # print(rate)
    # rate = history[history.hold==1].shape[0] / history.shape[0]
    # print(rate)

    # plt,ax1,ax2,ax3 = visualize(history[:-5])
    # ax1.scatter(turnup_points['id'], turnup_points['close']-0.1, label='buy point', color="#ffffff", marker='^')
    # ax1.scatter(turndown_points['id'], turndown_points['close']+0.1, label='sell point', color="#ffffff", marker='v')
    # ax1.legend(loc='upper right')
    # plt.show()
    if i % 20 == 0:
        dataset.to_csv(filename, index=False)
dataset.to_csv(filename, index=False)
