# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import matplotlib as mpl
import matplotlib.ticker as ticker
from mpl_finance import candlestick_ohlc

import datetime,time
import talib as ta
from talib import MA_Type

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

DATE_FORMAT = "%Y-%m-%d"

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[-1] - baseline['close'].iloc[0])
                    / baseline['close'].iloc[0] * 100,2)

right_offest = 0
def visualize(dataset, max_width=100):
    dataset = dataset.copy()
    dataset.index = pd.to_datetime(dataset.index, format=DATE_FORMAT)
    baseline_profits = calc_baseline_profit(dataset)
    c_down, c_up = '#77d879','#db3f3f'

    # transform data
    dataset['num_date'] = mdates.date2num(dataset.index.to_pydatetime())
    dataset['change'] = (dataset['close'] - dataset['close'].shift(periods=1))/dataset['close'].shift(periods=1)

    x = pd.to_datetime(dataset.index).tolist()

    mpl.style.use('dark_background')
    mpl.rcParams['toolbar'] = 'None'
    gs = gridspec.GridSpec(3, 3)
    fig =plt.figure(figsize=(15,8))
    ax1 =plt.subplot(gs[:2,:])
    ax2 =plt.subplot(gs[2,:])

    title = "Baseline: {:.2f}%".format(baseline_profits)
    subtitle = "From {:.10}    to {:.10}    Duration: {} days".format(str(dataset.index[0]), str(dataset.index[-1]), len(dataset))
    fig.text(0.05, 0.96, title, fontsize=10, weight='bold')
    fig.text(0.97, 0.96, subtitle, ha='right', fontsize=10)

    date_label = fig.text(0.07, 0.92, "")
    price_label = fig.text(0.07, 0.895, "")

    def update_price_label(pos):
        date = mdates.num2date(pos)
        price = dataset['close'].loc[date]
        change = dataset['change'].loc[date]
        c = c_up
        if dataset['open'].loc[date] > dataset['close'].loc[date]: c = c_down
        date_label.set_text("Date: {:.10}".format(str(date)))
        price_label.set_text("Price: {} ({:5.2f}%)".format(price, change*100))
        price_label.set_color(c)
        return

    update_price_label(dataset['num_date'].iloc[-1])

    x_start_pos = len(dataset)-max_width-right_offest-1
    x_end_pos = len(dataset)-right_offest-1
    subset = dataset[x_start_pos:x_end_pos]
    x_start_num_date = mdates.date2num(subset.iloc[0].name)
    x_end_num_date = mdates.date2num(subset.iloc[-1].name)
    for ax in [ax1, ax2]:
        ax.set_xticks(x)
        ax.grid(color='gray',which='major',linestyle='dashed',alpha=0.3)
        ax.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.set_xlim(x_start_num_date, x_end_num_date)
        ax.legend(loc='upper right')
    ax1.set_ylim(np.min(subset['low'])*0.9, np.max(subset['high'])*1.1)
    ax1.set_xticklabels([])

    cusor_vlines = []
    cusor_vlines.append(ax1.axvline(x=x[-1], color="w", linewidth=0.5, alpha=0.9))
    cusor_vlines.append(ax2.axvline(x=x[-1], color="w", linewidth=0.5, alpha=0.9))

    candlestick_ohlc(ax1, zip(
        dataset['num_date'],
        dataset['open'], dataset['high'],
        dataset['low'],  dataset['close']
    ), width=0.4, colordown=c_down, colorup=c_up)

    ax2.set_ylim(0,1)


    # ax2.axhline(y=0, color="w", linewidth=0.5, alpha=0.9)
    # ax2.axhspan(2, 5, facecolor='blue', alpha=0.05)



    def onClick(event):
        if not event.xdata: return
        pos = int(event.xdata)
        date = mdates.num2date(pos).strftime(DATE_FORMAT)
        if date not in dataset.index:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
            ns = dataset[dataset.index<date]
            date = dataset[dataset.index<date].iloc[-1].name
            pos = mdates.date2num(date)

        for vline in cusor_vlines:
            vline.set_data([pos,pos], [0, 1])

        update_price_label(pos)
        plt.draw()
        return

    def onPress(event):
        offest = 0
        step = 10
        if event.key.lower()=='a' or event.key=='left':
            offest = -step
        elif event.key.lower()=='d' or event.key=='right':
            offest = step
        x_start_num_date,x_end_num_date = ax1.get_xlim()
        x_start_num_date+=offest
        x_end_num_date+=offest

        subset = dataset[dataset.eval("num_date>={} & num_date<={}"
            .format(x_start_num_date, x_end_num_date))]

        for ax in [ax1, ax2]:
            ax.set_xlim(x_start_num_date, x_end_num_date)
        ax1.set_ylim(np.min(subset['low'])*0.9, np.max(subset['high'])*1.1)
        plt.draw()
        return

    fig.canvas.mpl_connect('button_press_event', onClick)
    fig.canvas.mpl_connect('key_press_event', onPress)

    plt.subplots_adjust(left=0.05, right=0.97, top=0.95, bottom=0.12)
    plt.show()
    return
