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
security='000786.XSHE'
security='000537.XSHE'
# end_date=datetime.date(2012,6,15)
end_date=datetime.date(2011,4,15)

history=get_price(security, end_date=end_date, count=lookback_size)
history['med'] = history[['open','close','high','low']].median(axis=1)
history['num_date'] = mdates.date2num(pd.to_datetime(history.index, format="%Y-%m-%d")).astype('i')

points = history[['num_date','close']].values

epsilon = history['med'].mean()*0.10
turn_points = find_turn_points(points, epsilon=epsilon)
turn_points = pd.DataFrame(turn_points,columns=['num_date','price'])
# turn_points['theta']=theta
# print(turn_points)

plt,ax1,ax2 = visualize(history)
ax1.plot(turn_points['num_date'],turn_points['price'], label="RDP", alpha=0.6)
ax1.legend(loc='upper right')
# ax2.plot(turn_points['num_date'],turn_points['theta'], label="theta", alpha=0.6)
plt.show()
