import datetime
import pandas as pd
import math, sys, os
import progressbar

from lib.jqdata import *
from lib.vis import *
from lib.turn_points import *

import matplotlib.dates as mdates
import datetime,time

debug = 'OFF'

LOOKBACK_SIZE = 100
SAMPLE_SIZE = 1000

start_date=datetime.date(2008,4,15)
end_date=datetime.date(2012,4,15)
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

security_list = get_all_securites().sample(SAMPLE_SIZE)
# security_list = get_all_securites()
trade_date = end_date
env = pd.DataFrame()
for _,row in progressbar.progressbar(security_list.iterrows(),max_value=security_list.shape[0]):
    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE)

    future = get_price(security, start_date=trade_date, end_date=(trade_date+datetime.timedelta(days=10)), count=-10)
    f5_close = future['close'].iloc[4]
    f10_close = future['close'].iloc[-1]

    history['ma60'] = history['close'].rolling(window=60).mean()
    history['ma60_pos'] = (history['close'] - history['ma60'])/ history['ma60']
    close = history['close'].iloc[-1]
    change = (close - history['close'].iloc[-2]) / history['close'].iloc[-2]
    p_min,p_max = history['low'].min(), history['high'].max()
    if p_min == p_max : continue
    p_pos = (close - p_min) / (p_max - p_min)
    p_down = (p_max-close)/p_max
    p_space = (p_max-p_min)/p_max

    vol = history['volume'].iloc[-1]
    v_min,v_max = history['volume'].min(), history['volume'].quantile(0.95)
    if v_min == v_max : continue
    v_pos = (vol - v_min) / (v_max - v_min)
    ma60_pos = history['ma60_pos'].iloc[-1]

    f10_change = (f10_close - close) / close
    f5_change = (f5_close - close) / close
    env = env.append(pd.Series({
        'p_pos': p_pos,
        'p_down':p_down,
        'p_space': p_space,
        'v_pos': v_pos,
        'today_c': change,
        'f5_c':f5_change,
        'f10_c':f10_change,
    }, name=security))

    # if _%10 ==0:
    #     env = env.sort_values(by=['future'],ascending=False)
    #     env=round(env,3)
    #     print(env)

env = np.round(env,4)
env = env.sort_values(by=['future'],ascending=False)
env.to_csv('report.csv',sep="\t",index=True, header=True)
future = np.round(env['future'],2)
env=env[['p_pos','p_down','p_space','v_pos']]
env.to_csv('report.tsv',sep="\t",index=False, header=False)
future.to_csv('report.meta',sep="\t",index=False, header=False)
print(env)
