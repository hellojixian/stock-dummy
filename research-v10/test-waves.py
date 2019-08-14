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
min_len = 120
lookback_size =200
start_date=datetime.date(2008,4,15)
end_date=datetime.date(2012,4,15)
np.random.seed(0)

print('start testing')

security_list = get_all_securites().sample(300)

trade_date = end_date
env = pd.DataFrame()
for _,row in progressbar.progressbar(security_list.iterrows()):
    security = row['security']

    history = get_price(security, end_date=trade_date, count=lookback_size)
    if history.shape[0] == 0: continue

    close = history['close'].iloc[-1]
    v_min,v_max = history['low'].min(), history['high'].max()
    v_pos = (close - v_min) / (v_max - v_min)
    env = env.append(pd.Series({
        'v_pos':v_pos
    }, name=security))

env = env.sort_values(by=['v_pos'])
print(env)
