'''
触发点 按过去60日的90分位数作为触发
破了新低 追第一红
'''

import datetime
import pandas as pd
import math, sys, os

from lib.jqdata import *
from lib.vis import *
from lib.turn_points import *

import matplotlib.dates as mdates
import datetime,time

debug = 'ON'
lookback_size = 600
# security='000786.XSHE'
# security='000537.XSHE'
# security='000919.XSHE'
# security='600822.XSHG'
security='600001.XSHG'
# end_date=datetime.date(2012,6,15)
end_date=datetime.date(2011,4,15)
tmp_cache_file = 'data/cache/tmp_cache_file'

buy_points = []
sell_points = []
turn_points = []

os.environ['DEBUG'] = str(debug)

if os.path.isfile(tmp_cache_file):
    history = pd.read_csv(tmp_cache_file, index_col=0)
    sell_points = pd.read_csv(tmp_cache_file+'_sell', index_col=0)
    buy_points = pd.read_csv(tmp_cache_file+'_buy', index_col=0)
else:
    history=get_price(security, end_date=end_date, count=lookback_size)
    history['num_date'] = mdates.date2num(pd.to_datetime(history.index, format="%Y-%m-%d")).astype('i')
    turn_points = find_turn_points(history)

    history['action'] = ""
    for i in range(1,350):
        action = ""
        subset = history[-250-i:-i]
        x= subset['num_date'].iloc[-1]
        y= subset['close'].iloc[-1]

        if should_buy(subset):
            buy_points.append((x,y))
            action="buy"
        if should_sell(subset):
            sell_points.append((x,y))
            action="sell"
        history.loc[subset.iloc[-1].name,'action'] = action

    buy_points  = pd.DataFrame(buy_points, columns=["num_date","price"])
    sell_points = pd.DataFrame(sell_points,columns=["num_date","price"])

    sell_points.to_csv(tmp_cache_file+'_sell')
    buy_points.to_csv(tmp_cache_file+'_buy')
    history.to_csv(tmp_cache_file)

plt,ax1,ax2 = visualize(history)
if len(turn_points)>0:
    ax1.plot(turn_points['num_date'],turn_points['price'], label="RDP", alpha=0.3)
    ax1.legend(loc='upper right')
if len(buy_points)>0:  ax1.scatter(buy_points['num_date'],buy_points['price']-0.3, color="w", marker="^", alpha=1, s=10)
if len(sell_points)>0: ax1.scatter(sell_points['num_date'],sell_points['price']+0.3, color="w", marker="v", alpha=1, s=10)

plt.show()
