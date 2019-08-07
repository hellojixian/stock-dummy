'''
触发点 按过去60日的90分位数作为触发
破了新低 追第一红
'''

import datetime
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
import talib
import pandas as pd
import matplotlib as mpl
import scipy.stats as stats
import scipy.fftpack as fftpack
import math

from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *
from lib.visualize import *
from lib.strategy import Strategy

mpl.style.use('dark_background')
mpl.rcParams['toolbar'] = 'None'

lookback_size = 500
security='000786.XSHE'
security='000537.XSHE'
end_date=datetime.date(2012,6,15)

history=get_price(security, end_date=end_date, count=lookback_size)
close = talib.TYPPRICE(history['high'],history['low'],history['close'])

window_size=300

report = pd.DataFrame()
i = 0
min_vspace = 0.5
offset = 0

for start_pos in range(-window_size,0):
    record = {}
    for stat_size in [30,60,120]:
        data_range = close[start_pos-stat_size:start_pos][:]
        v_current = data_range[-1]
        data_range = close[int(start_pos-offset)-stat_size:start_pos]
        v_max = max(data_range)
        v_min = min(data_range)

        v_max_pos = data_range[data_range==v_max].index[0]
        prev_data_range = data_range[data_range.index < v_max_pos]
        if len(prev_data_range)>0:
            v_prev_min = min(prev_data_range)
            # 用上一个波段的涨跌差来修正这个波段的预期
#             if v_prev_min > v_min:
# #                 v_min *= 1-(v_prev_min-v_min)*2
#                 v_min *= 0.7


        v_space = (v_max-v_min)/v_max
        v_pos_from_top = (v_max-v_current)/(v_max)


        scaled_pos = ((v_pos_from_top/v_space)-0.65) * ((1+v_space*3)*2)
        scaled_pos = scaled_pos

        record['pos_{}'.format(stat_size)]=scaled_pos
        record['v_space_{}'.format(stat_size)]=v_space

    record['pos_mean'] = np.mean([record['pos_30'],record['pos_60'],record['pos_120']])
    record = pd.Series(record)
    report=report.append(record,ignore_index=True)
    i+=1


plt.figure(figsize=(20,12))
gs = gridspec.GridSpec(3, 3)
ax1 =plt.subplot(gs[:2,:])
ax2 =plt.subplot(gs[2,:])


ax1.plot(range(window_size), close[-window_size:],label='price')

ax2.plot(report['pos_60'],label='pos_mean',color='y', lw=1.5)
# ax2.plot(report['pos_30'],label='pos_30', color='r')
# ax2.plot(report['pos_120'],label='pos_120')

ax2.plot(report['v_space_60'],label='v_space_60')
# ax2.plot(report['v_prev_space_60'],label='v_prev_space_60')
# ax2.plot(report['v_pos_from_top'],label='v_pos_from_top')


for ax in [ax1,ax2]:
    ax.axvline(250, color="w", linewidth=0.5, alpha=0.9)
    ax.axvspan(250,300,color='#333333',alpha=0.8)
    ax.set_xlim(0,300)
    ax.legend(loc='upper right')
    ax.grid(color='gray',which='minor',linestyle='dashed',alpha=0.2)
    ax.grid(color='gray',which='major',linestyle='dashed',alpha=0.3)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(5))

ax2.set_ylim(-1,1.5)

ax2.axhline(1, color="w", linewidth=0.5, alpha=0.9)
ax2.axhline(0.7, color="y", linewidth=1, alpha=0.9, ls='--')
ax2.axhline(0, color="w", linewidth=2, alpha=0.9)

plt.subplots_adjust(left=0.05, right=0.97, top=0.95, bottom=0.12)
plt.show()
