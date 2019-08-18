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
TREND_OBSERVE_LEN = 60

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
    # if history.shape[0]<=10 or future.shape[0]<10: continue

    f5_close = future['close'].iloc[4]
    f10_close = future['close'].iloc[-1]
    close = history['close'].iloc[-1]
    history = history.reset_index()
    history['id'] = history.index
    history['change'] = (history['close'] - history['close'].shift(periods=1))/history['close'].shift(periods=1)

    for i in range(1,len(history)):
    #     open = history.loc[i,'open']
    #     close = history.loc[i,'close']
    #     high = history.loc[i,'high']
    #     low = history.loc[i,'low']
    #     vol = history.loc[i,'volume'] / 10**6
    #     prev_close = history.loc[i-1,'close']
    #     change = (close - prev_close) / prev_close

        if i >= TREND_OBSERVE_LEN:
            subset = history[i-TREND_OBSERVE_LEN+1:i+1]
            history.loc[i,'trend'] = find_trend(subset)

    history['trend_ma_short'] = history['trend'].rolling(window=3).mean()
    history['trend_ma_long'] = history['trend'].rolling(window=7).mean()
    history['trend_wma'] = (history['trend_ma_long']+history['trend_ma_short']+history['trend'])/3
    history['trend_wma_ma10'] = history['trend_wma'].rolling(window=24).mean()
    history = history.drop(columns=['trend','trend_ma_short','trend_ma_long'])

    history['amp'] = history['high'] - history['low']
    history['amp_ma_short'] = history['amp'].rolling(window=3).mean()
    history['amp_ma_long'] = history['amp'].rolling(window=7).mean()
    history['amp_wma'] = (history['amp_ma_long']+history['amp_ma_short']+history['amp'])/3
    history = history.drop(columns=['amp','amp_ma_short','amp_ma_long'])

    history['vol_ma_short'] = history['volume'].rolling(window=3).mean()
    history['vol_ma_long'] = history['volume'].rolling(window=7).mean()
    history['vol_ma'] = (history['vol_ma_long']+history['vol_ma_short']+history['volume'])/3
    history = history.drop(columns=['vol_ma_short','vol_ma_long'])

    history['vp_r'] = (history['amp_wma']/history['close'].shift(periods=1) * 100) **3 / (history['vol_ma'] / 10**6) **3
    history['amp_wma'] = (history['amp_wma']*100) **3
    plt,ax1,ax2,ax3 = visualize(history)

    ax2.bar(history.index.tolist(), history['vp_r'], label="vp_r", color='#34a4eb',alpha=0.5)
    ax3.plot(history.index.tolist(), history['trend_wma'] , label="trend_wma", color='#77d879',alpha=1, zorder=10)
    ax3.plot(history.index.tolist(), history['trend_wma_ma10'] , label="trend_wma_ma10", color='#db3f3f',alpha=1, zorder=10)
    ax2.set_ylim(history['vp_r'].min(), history['vp_r'].max())
    # ax3.set_ylim(history['trend_wma'].min(), history['trend_wma'].max())
    ax3.set_ylim(-1,1)
    ax3.axhline(y=0, color="w", linewidth=0.5, alpha=1)
    plt.show()

# print(env)
