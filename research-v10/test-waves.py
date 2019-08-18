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

debug = 'OFF'

LOOKBACK_SIZE = 1000
SAMPLE_SIZE = 1000
TREND_OBSERVE_LEN = 30

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
for _,row in progressbar.progressbar(security_list.iterrows(),max_value=security_list.shape[0]):
    if _ <= 25: continue
    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE, skip_paused=True)
    future = get_price(security, start_date=trade_date, end_date=(trade_date+datetime.timedelta(days=12)), count=10, skip_paused=True)
    if history.shape[0]<=10 or future.shape[0]<10: continue

    f5_close = future['close'].iloc[4]
    f10_close = future['close'].iloc[-1]
    close = history['close'].iloc[-1]
    history = history.reset_index()
    history['id'] = history.index
    history['change'] = (history['close'] - history['close'].shift(periods=1))/history['close'].shift(periods=1)

    for i in range(1,len(history)):
        open = history.loc[i,'open']
        close = history.loc[i,'close']
        high = history.loc[i,'high']
        low = history.loc[i,'low']
        vol = history.loc[i,'volume'] / 10**6
        prev_close = history.loc[i-1,'close']
        change = (close - prev_close) / prev_close

        history.loc[i,'ud_r'] = ((high - low)/ prev_close *100)**3 / vol **3

        # history.loc[i,'ud_r'] = (history.loc[i,'amp']) *100)**2
        # if i >= TREND_OBSERVE_LEN:
        #     subset = history[i-TREND_OBSERVE_LEN:i]
        #     points = find_turn_points(subset,epsilon=close*0.1,field='close')
        #     print(points)
        #     break

    plt,ax1,ax2,ax3 = visualize(history)


    # history['vol_ratio'] = np.abs(history['vol_ratio'])
    # ax2.bar(history.index.tolist(), history['up'], label="up", color='#db3f3f')
    # ax2.bar(history.index.tolist(), history['down'], label="down", color='#77d879')
    ax2.plot(history.index.tolist(), history['ud_r'], label="ud_r", color='#34a4eb',alpha=0.5)
    ax2.bar(history.index.tolist(), history['ud_r'], label="ud_r", color='#34a4eb',alpha=0.5)
    # ax2.bar(history.index.tolist(), history['change_r'], label="change_r", color='#77d879',alpha=1, zorder=10)
    ax2.set_ylim(history['ud_r'].min(), history['ud_r'].max())
    plt.show()
    break
# print(env)
