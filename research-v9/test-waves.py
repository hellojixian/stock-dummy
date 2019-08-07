'''
触发点 按过去60日的90分位数作为触发
破了新低 追第一红
'''

import datetime
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
import talib
import pandas as pd
import math, sys

from lib.jqdata import *
from lib.vis import *


mpl.style.use('dark_background')
mpl.rcParams['toolbar'] = 'None'

lookback_size = 500
security='000786.XSHE'
security='000537.XSHE'
end_date=datetime.date(2012,6,15)

history=get_price(security, end_date=end_date, count=lookback_size)

visualize(history)

#
# window_size=300
# report = pd.DataFrame()
# i = 0
# min_vspace = 0.5
# offset = 0
#
# for start_pos in range(-window_size,0):
#     record = {}
#     for stat_size in [30,60,120]:
#         data_range = close[start_pos-stat_size:start_pos][:]
#         v_current = data_range[-1]
#         data_range = close[int(start_pos-offset)-stat_size:start_pos]
#         v_max = max(data_range)
#         v_min = min(data_range)
#
#         v_max_pos = data_range[data_range==v_max].index[0]
#         prev_data_range = data_range[data_range.index < v_max_pos]
#         if len(prev_data_range)>0:
#             v_prev_min = min(prev_data_range)
#
#
#         v_space = (v_max-v_min)/v_max
#         v_pos_from_top = (v_max-v_current)/(v_max)
#
#
#         scaled_pos = ((v_pos_from_top/v_space)-0.65) * ((1+v_space*3)*2)
#         scaled_pos = scaled_pos
#
#         record['pos_{}'.format(stat_size)]=scaled_pos
#         record['v_space_{}'.format(stat_size)]=v_space
#
#     record['pos_mean'] = np.mean([record['pos_30'],record['pos_60'],record['pos_120']])
#     record = pd.Series(record)
#     report=report.append(record,ignore_index=True)
#     i+=1
