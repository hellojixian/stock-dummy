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
TREND_OBSERVE_LEN = 67

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
    row = security_list.iloc[0]

    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE, skip_paused=True)
    future = get_price(security, start_date=trade_date, end_date=(trade_date+datetime.timedelta(days=12)), count=10, skip_paused=True)

    f5_close = future['close'].iloc[4]
    f10_close = future['close'].iloc[-1]
    close = history['close'].iloc[-1]
    history = history.reset_index()
    history['id'] = history.index
    history['change'] = (history['close'] - history['close'].shift(periods=1))/history['close'].shift(periods=1)

    history['trend'] = history['id'].rolling(window=TREND_OBSERVE_LEN).apply(find_trend, raw=True, args=[history])
    history['trend_wma'] = ta.WMA(history['trend'],5)
    history['trend_wma_ma10'] = ta.WMA(history['trend'],24)

    history['amp'] = history['high'] - history['low']
    history['amp_wma'] = HMA(history['amp'])
    history['vol_ma'] = HMA(history['volume'])

    history['vp_r'] = (history['amp_wma']/history['close'].shift(periods=1) * 100) **3 / (history['vol_ma'] / 10**6) **3
    history['amp_wma'] = (history['amp_wma']*100) **3
    plt,ax1,ax2,ax3 = visualize(history)

    ax2.bar(history.index.tolist(), history['vp_r'], label="vp_r", color='#34a4eb',alpha=0.5)
    ax3.plot(history.index.tolist(), history['trend'] , label="trend", color='#FFFFFF',alpha=0.3, zorder=10)
    ax3.plot(history.index.tolist(), history['trend_wma'] , label="trend_wma", color='#77d879',alpha=1, zorder=10)
    ax3.plot(history.index.tolist(), history['trend_wma_ma10'] , label="trend_wma_ma10", color='#db3f3f',alpha=1, zorder=10)
    ax2.set_ylim(history['vp_r'].min(), history['vp_r'].max())
    ax3.set_ylim(history['trend_wma'].min(), history['trend_wma'].max())
    # ax3.set_ylim(-1.2,1.2)
    ax3.axhline(y=0, color="w", linewidth=0.5, alpha=1)
    plt.show()

# print(env)
