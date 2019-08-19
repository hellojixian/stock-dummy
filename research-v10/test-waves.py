import datetime
import pandas as pd
import math, sys, os
import progressbar

from lib.jqdata import *
from lib.vis import *
from lib.turn_points import *
from scipy.signal import savgol_filter

import matplotlib.dates as mdates
import datetime,time
import talib as ta

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
# security_list = get_all_securites()
trade_date = end_date
env = pd.DataFrame()
# for _,row in progressbar.progressbar(security_list.iterrows(),max_value=security_list.shape[0]):
    # if _ <= 25: continue
if True:
    row = security_list.iloc[14]

    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE, skip_paused=True)
    future = get_price(security, start_date=trade_date, end_date=(trade_date+datetime.timedelta(days=12)), count=10, skip_paused=True)

    f5_close = future['close'].iloc[4]
    f10_close = future['close'].iloc[-1]
    close = history['close'].iloc[-1]
    history = history.reset_index()
    history['id'] = history.index
    history['change'] = (history['close'] - history['close'].shift(periods=1))/history['close'].shift(periods=1)

    history['amp'] = history['high'] - history['low']
    history['amp_wma'] = HMA(history['amp'])
    history['vol_ma'] = HMA(history['volume'])

    history['p_pos'] = history['id'].rolling(window=TREND_OBSERVE_LEN).apply(find_price_pos, raw=True, args=[history])
    history['p_pos_wma'] = ta.WMA(history['p_pos'],2)
    history['p_pos_wma_ma10'] = ta.WMA(history['p_pos'],17)
    history['p_pos_wma_ma10'] = HMA(history['p_pos_wma_ma10'],4)
    history['p_pos_bais'] = (history['p_pos'] - history['p_pos_wma_ma10']) * np.abs(history['p_pos'])

    history['vp_r'] = (history['amp_wma']/history['close'].shift(periods=1) * 100) **3 / (history['vol_ma'] / 10**6) **3

    history['amp_wma'] = (history['amp_wma']*100) **3

    # visualization code below
    history = history[TREND_OBSERVE_LEN:]
    plt,ax1,ax2,ax3 = visualize(history)

    ax2.bar(range(history.shape[0]), history['vp_r'], label="vp_r", color='#34a4eb',alpha=0.5)
    ax2.set_ylim(0, 6)

    ax3.bar(range(history.shape[0]), history['p_pos_bais'] , label="p_pos_bais", alpha=0.5, color='#34a4eb',zorder=10)
    ax3.plot(range(history.shape[0]), history['p_pos'] , label="p_pos", alpha=1, color='#77d879',zorder=10)
    ax3.plot(range(history.shape[0]), history['p_pos_wma_ma10'] , label="p_pos_ma10", color='#db3f3f',alpha=1, zorder=10)

    ax3.set_ylim(-1,+1)
    ax3.axhline(y=0, color="w", linewidth=1, alpha=1)
    ax3.legend(loc='upper right')

    plt.show()

# print(env)
