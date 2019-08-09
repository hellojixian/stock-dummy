'''
触发点 按过去60日的90分位数作为触发
破了新低 追第一红
'''

import datetime
import pandas as pd
import math, sys

from lib.jqdata import *
from lib.vis import *
from lib.turn_points import *

import matplotlib.dates as mdates
import datetime,time


lookback_size = 600
# security='000786.XSHE'
security='000537.XSHE'
# end_date=datetime.date(2012,6,15)
end_date=datetime.date(2011,4,15)

history=get_price(security, end_date=end_date, count=lookback_size)
history['num_date'] = mdates.date2num(pd.to_datetime(history.index, format="%Y-%m-%d")).astype('i')
turn_points = find_turn_points(history)

buy_points = []
for i in range(1,350):
    subset = history[-250-i:-i]
    if should_buy(subset):
        x= subset['num_date'].iloc[-1]
        y= subset['close'].iloc[-1]
        buy_points.append((x,y))
buy_points = pd.DataFrame(buy_points,columns=["num_date","price"])

plt,ax1,ax2 = visualize(history)
ax1.plot(turn_points['num_date'],turn_points['price'], label="RDP", alpha=0.3)
ax1.legend(loc='upper right')

ax1.scatter(buy_points['num_date'],buy_points['price']-0.1, color="w", marker="^", alpha=1, s=10)

plt.show()
