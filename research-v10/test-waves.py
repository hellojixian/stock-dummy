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

LOOKBACK_SIZE = 500
SAMPLE_SIZE = 1000

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
    if _ != 10: continue
    security = row['security']
    history = get_price(security, end_date=trade_date, count=LOOKBACK_SIZE, skip_paused=True)
    future = get_price(security, start_date=trade_date, end_date=(trade_date+datetime.timedelta(days=12)), count=10, skip_paused=True)
    if history.shape[0]<=10 or future.shape[0]<10: continue


    f5_close = future['close'].iloc[4]
    f10_close = future['close'].iloc[-1]
    close = history['close'].iloc[-1]

    history['num_date'] = mdates.date2num(history.index.to_pydatetime())
    history['de_noised'] = savgol_filter(history['close'], 21, 3)
    points = find_turn_points(history,epsilon=close*0.1,field='close')

    plt,ax1,ax2 = visualize(history)
    # ax1.plot(points['num_date'], points['price'], label="turnpoints")
    # ax1.plot(history['num_date'], history['close'], label="smooth_close")
    plt.show()
    break
# print(env)
