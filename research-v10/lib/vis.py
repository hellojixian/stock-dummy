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
from lib.turn_points import *

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

DATE_FORMAT = "%Y-%m-%d"

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[-1] - baseline['close'].iloc[0])
                    / baseline['close'].iloc[0] * 100,2)

right_offest = 0
def visualize(dataset, max_width=150):
    dataset = dataset.copy()
    dataset.index = pd.to_datetime(dataset.index, format=DATE_FORMAT)
    baseline_profits = calc_baseline_profit(dataset)
    c_down, c_up = '#77d879','#db3f3f'

    # transform data
    if 'num_date' not in dataset.columns:
        dataset['num_date'] = mdates.date2num(dataset.index.to_pydatetime())
    if 'change' not in dataset.columns:
        dataset['change'] = (dataset['close'] - dataset['close'].shift(periods=1))/dataset['close'].shift(periods=1)

    x = pd.to_datetime(dataset.index).tolist()

    mpl.style.use('dark_background')
    mpl.rcParams['toolbar'] = 'None'

    fig =plt.figure(figsize=(12,9))
    gs = gridspec.GridSpec(4, 3)
    ax1 =plt.subplot(gs[:3,:])
    ax2 =plt.subplot(gs[3,:])

    title = "Baseline: {:.2f}%".format(baseline_profits)
    subtitle = "From {:.10}    to {:.10}    Duration: {} days".format(str(dataset.index[0]), str(dataset.index[-1]), len(dataset))
    fig.text(0.05, 0.96, title, fontsize=10, weight='bold')
    fig.text(0.97, 0.96, subtitle, ha='right', fontsize=10)

    profit_label = fig.text(0.2, 0.96, "", fontsize=10, weight='bold')
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

    def onClick(event):
        if not event.xdata: return
        pos = int(event.xdata)
        date = mdates.num2date(pos).strftime(DATE_FORMAT)
        if date not in dataset.index:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
            date = dataset[dataset.index<date].iloc[-1].name
            pos = mdates.date2num(date)

        for vline in cursor_vlines:
            vline.set_data([pos,pos], [0, 1])

        date = mdates.num2date(pos)
        price = dataset['close'].loc[date]
        cursor_hline.set_data([0, 1],[price,price])
        update_price_label(pos)

        subset = dataset[:dataset.index.get_loc(date)+1]
        res = test_feature(subset,[ax1,ax2])

        plt.draw()
        return

    def onPress(event):
        offest = 0
        step = 20
        pos = cursor_vlines[0].get_data()[0][0]
        if event.key.lower()=='a' or event.key=='left':
            event.xdata = pos-1
            onClick(event)
        elif event.key.lower()=='d' or event.key=='right':
            pos += 1
            date = mdates.num2date(pos).strftime(DATE_FORMAT)
            if date not in dataset.index:
                date = datetime.datetime.strptime(date, DATE_FORMAT)
                date = dataset[dataset.index>date].iloc[0].name
                pos = mdates.date2num(date)

            event.xdata = pos
            onClick(event)
        if event.key.lower()=='z':
            offest = -step
        elif event.key.lower()=='c':
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

    # ax1.plot(x, dataset['close'], label='Price', alpha=0.3)

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
    ax1.set_ylim(np.min(subset['low'])*0.9, np.max(subset['high'])*1.1)
    ax1.set_xticklabels([])

    cursor_vlines = []
    cursor_vlines.append(ax1.axvline(x=x[-1], color="w", linewidth=0.5, alpha=0.6))
    cursor_vlines.append(ax2.axvline(x=x[-1], color="w", linewidth=0.5, alpha=0.6))
    cursor_hline = ax1.axhline(y=0, color="w", linewidth=0.5, alpha=0.5)

    minmax_hspan = ax1.axhspan(0, 0, facecolor='y', alpha=0.08)

    candlestick_ohlc(ax1, zip(
        dataset['num_date'],
        dataset['open'], dataset['high'],
        dataset['low'],  dataset['close']
    ), width=0.4, colordown=c_down, colorup=c_up)

    ax2.set_ylim(0,1)

    fig.canvas.mpl_connect('button_press_event', onClick)
    fig.canvas.mpl_connect('key_press_event', onPress)

    update_price_label(dataset['num_date'].iloc[-1])
    if 'action' in dataset.columns:
        mark_buysell_range(dataset, [ax1, ax2], profit_label)

    plt.subplots_adjust(left=0.05, right=0.97, top=0.95, bottom=0.12)
    return [plt,ax1, ax2]

def mark_buysell_range(dataset, axs, profit_label=None):
    # 标记获利还是亏损
    idx = 0
    strategy_profit = 1
    baseline_profit = 1
    profit_stat = pd.DataFrame()
    # print(dataset[:20])
    # assert(False)
    buy_actions = pd.DataFrame()
    sell_actions = pd.DataFrame()
    while idx <= len(dataset)-1:
        row = dataset.iloc[idx]
        if row['action']=='buy':
            start_date_n =row['num_date']
            buy_actions = buy_actions.append(pd.Series({
                'num_date': start_date_n,
                'strategy_profit': (strategy_profit-1) *100
            },name=start_date_n))
            start_date = row.name
            bought_price = row['close']
            b_row = row
            while idx <= len(dataset)-1:
                row = dataset.iloc[idx]
                if row['action']=='sell':
                    # strategy_profit *=(1+row['change'])
                    end_date_n = row['num_date']
                    end_date = row.name
                    sell_price = row['close']
                    color = '#44ff26'
                    text_color = '#44ff26'
                    annon_y_pos  = sell_price*0.98
                    sell_marker = "v"
                    profit = (sell_price - bought_price) / bought_price
                    rotation = -15
                    if profit>0:
                        color = '#ff3636'
                        text_color = '#ff0000'
                        annon_y_pos = sell_price*1.02
                        sell_marker = "^"
                        rotation = abs(rotation)
                    # strategy_profit *= (1+profit)
                    axs[0].axvspan(start_date, end_date, facecolor=color, alpha=0.15)
                    axs[1].axvspan(start_date, end_date, facecolor=color, alpha=0.15)
                    axs[0].scatter(end_date, annon_y_pos, alpha=1, marker=sell_marker,s=10, color=color)
                    axs[0].annotate("  {:.1f}%".format(profit*100),(end_date, annon_y_pos),
                        weight='bold',ha='left', va='center', color=text_color)

                    strategy_profit = strategy_profit*(1+row['change'])
                    sell_actions = sell_actions.append(pd.Series({
                        'num_date': end_date_n,
                        'strategy_profit': (strategy_profit-1) *100,
                        'color': color,
                        'mark': sell_marker
                    },name=start_date_n))
                    break
                idx+=1
                baseline_profit *=(1+row['change'])

                if row['action']!='buy':
                    strategy_profit = strategy_profit*(1+row['change'])
                    # print('hold',row.name,strategy_profit,row['change'])
                rec = pd.Series({
                    "num_date":row['num_date'],
                    "baseline_profit":(baseline_profit-1) * 100,
                    "strategy_profit":(strategy_profit-1) * 100
                }, name="{:.10}".format(str(mdates.num2date(row['num_date']))))
                profit_stat = profit_stat.append(rec)
        else:
            idx+=1
            baseline_profit *=(1+row['change'])
            rec = pd.Series({
                "num_date":row['num_date'],
                "baseline_profit":(baseline_profit-1) * 100,
                "strategy_profit":(strategy_profit-1) * 100
            }, name="{:.10}".format(str(mdates.num2date(row['num_date']))))
            profit_stat = profit_stat.append(rec)

    axs[1].plot(profit_stat['num_date'],profit_stat['baseline_profit'], label="baseline_profit", color='#f54242')
    axs[1].fill_between(profit_stat['num_date'],profit_stat['baseline_profit'],0, alpha=0.1, color="#f54242")

    axs[1].plot(profit_stat['num_date'],profit_stat['strategy_profit'], label="strategy_profit",alpha=1, color="#4287f5")
    axs[1].fill_between(profit_stat['num_date'],profit_stat['strategy_profit'],0, alpha=0.2, color="#4287f5")
    axs[1].legend(loc='upper left')
    axs[1].set_ylim(np.min([profit_stat['baseline_profit'],profit_stat['strategy_profit']])*0.95,
        np.max([profit_stat['baseline_profit'],profit_stat['strategy_profit']])*1.05)


    dataset['strategy_profit'] = profit_stat['strategy_profit']

    axs[1].scatter(buy_actions['num_date'],buy_actions['strategy_profit'], label="strategy_profit",alpha=1,lw=1, marker="|", s=20, color='#ffffff',zorder=10)
    for _,action in sell_actions.iterrows():
        axs[1].scatter(action['num_date'],action['strategy_profit'], alpha=1, marker='|',s=20, lw=1,color=action['color'],zorder=10)
    if profit_label is not None:
        strategy_profit -= 1
        profit_label.set_text("Strategy: {:.2f}%".format(strategy_profit*100))

    return

g={}
def test_feature(dataset,axs):
    close = dataset['close'].iloc[-1]

    for key,rate in [
        ('short_rdp_2',0.025),
        ('short_rdp_5',0.05),
        ('short_rdp_10',0.10),
    ]:
        points = find_turn_points(dataset[-120:], epsilon=close*rate)
        if key not in g.keys():
            g[key], = axs[0].plot(points['num_date'],points['price'], label=key, alpha=0.5 )
        else:
            g[key].set_xdata(points['num_date'])
            g[key].set_ydata(points['price'])
    axs[0].legend(loc='upper right')
    return points
