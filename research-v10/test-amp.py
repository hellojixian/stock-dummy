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

start_date=datetime.date(2005,4,15)
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

def find_price_range(values, history):
    history = history[int(values[0]):int(values[-1])]
    close = history['close'].iloc[-1]
    p_min, p_max = history['close'].min(), history['close'].max()
    pos = (close-p_min)/ (p_max - p_min)
    if pos == 0: pos=0.15
    return pos

if True:
    row = security_list.iloc[10]

    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE, skip_paused=True)

    close = history['close'].iloc[-1]
    history = history.reset_index()
    history['id'] = history.index
    history['change'] = (history['close'] - history['close'].shift(periods=1))/history['close'].shift(periods=1)

    history['amp_90'] = history['id'].rolling(window=60).apply(find_price_range, raw=True, args=[history])
    # history['amp_90'] = HMA(history['amp_90'],5)

    print(history['amp_90'].min(), history['amp_90'].max())
    print('mean: {:.2f}'.format(history['amp_90'].mean()))
    print('quantile75: {:.2f}'.format(history['amp_90'].quantile(0.75)))
    print('quantile80: {:.2f}'.format(history['amp_90'].quantile(0.8)))
    print('quantile90: {:.2f}'.format(history['amp_90'].quantile(0.9)))

    plt,ax1,ax2,ax3 = visualize(history)

    ax2.plot(range(history.shape[0]), history['amp_90'], label='amp90')
    ax2.legend(loc='upper right')
    ax2.set_ylim(0, 1)
    plt.show()

# print(env)
