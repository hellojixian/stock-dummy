# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import matplotlib as mpl
import matplotlib.ticker as ticker
from mpl_finance import candlestick_ohlc

import datetime,time
from lib.turn_points import *

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

DATE_FORMAT = "%Y-%m-%d"

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[-1] - baseline['close'].iloc[0])
                    / baseline['close'].iloc[0] * 100,2)

right_offest = 0
ds = None
def visualize(dataset, max_width=150):
    dataset = dataset.copy()


    dataset.index = pd.to_datetime(dataset.index, format=DATE_FORMAT)
    baseline_profits = calc_baseline_profit(dataset)
    c_down, c_up = '#77d879','#db3f3f'

    # transform data
    if 'change' not in dataset.columns:
        dataset['change'] = (dataset['close'] - dataset['close'].shift(periods=1))/dataset['close'].shift(periods=1)


    dataset = dataset.reset_index()
    dataset['date'] = dataset['index']
    dataset = dataset.drop(columns=['index'])

    mpl.style.use('dark_background')
    mpl.rcParams['toolbar'] = 'None'

    fig =plt.figure(figsize=(12,9))
    gs = gridspec.GridSpec(5, 3)
    ax1 =plt.subplot(gs[:3,:])
    ax2 =plt.subplot(gs[3,:])
    ax3 =plt.subplot(gs[4,:])

    title = "Baseline: {:.2f}%".format(baseline_profits)
    subtitle = "From {:.10}    to {:.10}    Duration: {} days".format(str(dataset['date'].iloc[0]), str(dataset['date'].iloc[-1]), len(dataset))
    fig.text(0.05, 0.96, title, fontsize=10, weight='bold')
    fig.text(0.94, 0.96, subtitle, ha='right', fontsize=10)

    profit_label = fig.text(0.2, 0.96, "", fontsize=10, weight='bold')
    date_label = fig.text(0.07, 0.92, "")
    price_label = fig.text(0.07, 0.895, "")
    vol_label = fig.text(0.07, 0.87, "", alpha=0.5)

    def update_price_label(pos):
        rec = dataset.iloc[pos]
        date = rec['date']
        idx = rec.name
        price = dataset['close'].iloc[idx]
        change = dataset['change'].iloc[idx]
        vol = dataset['volume'].iloc[idx]
        c = c_up
        if dataset['open'].iloc[idx] > dataset['close'].iloc[idx]: c = c_down
        date_label.set_text("Date: {:.10}".format(str(date)))
        price_label.set_text("Price: {} ({:5.2f}%)".format(price, change*100))
        price_label.set_color(c)
        vol_label.set_text("Vol: {}k".format(vol/1000))
        return

    def onClick(event):
        if not event.xdata: return
        if event.xdata<0: return
        if event.xdata>len(dataset): return
        pos = int(event.xdata)

        for vline in cursor_vlines:
            vline.set_data([pos,pos], [0, 1])

        price = dataset['close'].iloc[pos]
        cursor_hline.set_data([0, 1],[price,price])
        update_price_label(pos)

        subset = dataset[:pos+1]
        res = test_feature(subset,[ax1,ax2])

        plt.draw()
        return

    def onPress(event):
        offest = 0
        step = 20
        pos = cursor_vlines[0].get_data()[0][0]
        if event.key.lower()=='a' or event.key=='left':
            if pos-1 >=0:
                event.xdata = pos-1
                onClick(event)
        elif event.key.lower()=='d' or event.key=='right':
            if pos+1 <len(dataset):
                event.xdata = pos+1
                onClick(event)
        if event.key.lower()=='z':
            offest = -step
        elif event.key.lower()=='c':
            offest = step
        x_start_num_date,x_end_num_date = ax1.get_xlim()
        x_start_num_date+=offest
        x_end_num_date+=offest

        xlim = ax1.get_xlim()
        width = xlim[1]-xlim[0]
        if x_start_num_date<=0:
            x_start_num_date = 0
            x_end_num_date = width

        if x_end_num_date>=len(dataset):
            x_end_num_date = len(dataset)
            x_start_num_date = x_end_num_date-width

        x_start_num_date = int(x_start_num_date)
        x_end_num_date = int(x_end_num_date)

        subset = dataset[x_start_num_date:x_end_num_date]
        for ax in [ax1, ax2, ax3]:
            ax.set_xlim(x_start_num_date, x_end_num_date)
        ax1.set_ylim(np.min(subset['low'])*0.9, np.max(subset['high'])*1.1)

        ax2.set_ylim(0, np.max(subset['vp_r'])*1.1)
        # ax3.set_ylim(subset['trend_wma'].min(), subset['trend_wma'].max())
        plt.draw()
        return

    x_start_pos = len(dataset)-max_width-right_offest-1
    x_end_pos = len(dataset)-right_offest-1
    subset = dataset[x_start_pos:x_end_pos]
    x_start_idx = subset.iloc[0].name
    x_end_idx = subset.iloc[-1].name
    cursor_vlines = []
    for ax in [ax1, ax2, ax3]:
        ax.grid(color='gray',which='major',linestyle='dashed',alpha=0.3)
        ax.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.set_xlim(x_start_idx, x_end_idx+2)
        cursor_vlines.append(ax.axvline(x=dataset.index[-1], color="w", linewidth=0.5, alpha=0.6))
        cursor_vlines.append(ax.axvline(x=dataset.index[-1], color="w", linewidth=0.5, alpha=0.6))
    ax1.set_ylim(np.min(subset['low'])*0.9, np.max(subset['high'])*1.1)
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    cursor_hline = ax1.axhline(y=0, color="w", linewidth=0.5, alpha=0.5)

    candlestick_ohlc(ax1, zip(
        dataset.index,
        dataset['open'], dataset['high'],
        dataset['low'],  dataset['close'], dataset['volume']
    ), width=0.4, colordown=c_down, colorup=c_up)
    ax_vol = ax1.twinx()
    ax_vol.bar(dataset.index, dataset['volume'])
    ax_vol.set_ylim(0, max(dataset['volume'])*4)
    ax2.set_ylim(0,1)

    global ds
    ds = dataset
    def format_date(x, pos=None):
        global ds
        label = ds['date'].iloc[int(x)]
        return label.strftime("%m/%d")
    ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))

    fig.canvas.mpl_connect('button_press_event', onClick)
    fig.canvas.mpl_connect('key_press_event', onPress)

    update_price_label(-1)
    if 'action' in dataset.columns:
        mark_buysell_range(dataset, [ax1, ax2], profit_label)

    plt.subplots_adjust(left=0.05, right=0.97, top=0.95, bottom=0.12)
    return [plt,ax1, ax2, ax3]

def mark_buysell_range(dataset, axs, profit_label=None):
    return

g={}
def test_feature(dataset,axs):
    close = dataset['close'].iloc[-1]
    len=60
    for key,rate in [
        ('short_rdp_10',0.10),
    ]:
        points = find_turn_points(dataset[-len:], epsilon=close*rate)
        if key not in g.keys():
            g[key], = axs[0].plot(points['id'],points['price'], label=key, alpha=0.5 )
        else:
            g[key].set_xdata(points['id'])
            g[key].set_ydata(points['price'])
    axs[0].legend(loc='upper right')
    return
