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

from pandas.plotting import register_matplotlib_converters

DATE_FORMAT = "%Y-%m-%d"

def generate_report(dataset):
    cols = ['short','median','long','close']
    cols.extend(['date'])
    df = pd.DataFrame(dataset, columns=cols)
    df = df.set_index(keys=['date'])
    df['change'] = (df['close'] - df['close'].shift(periods=1)) /  df['close'].shift(periods=1)
    return df

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[-1] - baseline['close'].iloc[0])
                    / baseline['close'].iloc[0] * 100,2)

def visualize_report(dataset,backtest):
    dataset = dataset.copy()
    dataset.index = pd.to_datetime(dataset.index, format=DATE_FORMAT)
    baseline_profits = calc_baseline_profit(backtest)

    xlabel = dataset.index.strftime(DATE_FORMAT).tolist()
    x = pd.to_datetime(dataset.index).tolist()
    register_matplotlib_converters()

    max_width = min(len(x), 100)

    dataset['ma5'] = dataset['close'].rolling(window=5).mean()
    dataset['ma10'] = dataset['close'].rolling(window=10).mean()
    dataset['ma30'] = dataset['close'].rolling(window=30).mean()
    dataset['ma60'] = dataset['close'].rolling(window=60).mean()

    mpl.rcParams['toolbar'] = 'None'
    gs = gridspec.GridSpec(3, 3)
    fig =plt.figure(figsize=(15,8))
    ax1 =plt.subplot(gs[:2,:])
    ax1.plot(x, dataset['close'],label='Price', alpha=0.5)
    ax1.plot(x, dataset['ma5'],label='MA5', alpha=0.5)
    ax1.plot(x, dataset['ma10'],label='MA10', alpha=0.5)
    ax1.plot(x, dataset['ma30'],label='MA30', alpha=0.5)
    ax1.plot(x, dataset['ma60'],label='MA60', alpha=0.5)
    ax1.legend(loc='upper right')
    ax1.set_xticks(x)
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax1.set_xlim(x[-max_width],x[-1])
    ax1.set_xticklabels([])
    ax1.grid(color='gray',which='major',linestyle='dashed',alpha=0.3)
    ax1.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)
    ax1.set_title("Baseline Profit: {:.2f}%".format(baseline_profits))
    ax1.set_ylabel('close price')
    ax1.set_ylim(dataset['close'].min()*0.95,dataset['close'].max()*1.05)

    candlestick_ohlc(ax1, zip(
        mdates.date2num(dataset.index.to_pydatetime()),
        backtest['open'], backtest['high'],
        backtest['low'], backtest['close']
    ), width=0.4, colordown='#77d879', colorup='#db3f3f')


    ax2 =plt.subplot(gs[2,:])
    ax2.plot(x, dataset['short'],label='short_pos', marker=".", alpha=0.4, color='r')
    ax2.plot(x, dataset['median'],label='median_pos', alpha=0.3, color='g')
    ax2.plot(x, dataset['long'],label='long_pos', alpha=0.2, color='b')

    ax2.set_ylabel('score')
    ax2.legend(loc='upper right')
    ax2.set_xticks(x)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))
    ax2.set_xticklabels(xlabel,rotation=45, rotation_mode="default",alpha=0.5)
    ax2.set_yticks(np.round(np.linspace(0,7, 8),2))
    ax2.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax2.set_ylim(0,7)
    ax2.set_xlim(x[-max_width],x[-1])
    ax2.set_title("Features")
    ax2.grid(color='gray',which='major',linestyle='dashed',alpha=0.35)
    ax2.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)
    ax2.axhspan(2, 5, facecolor='blue', alpha=0.05)

    # 标记获利还是亏损
    # ax2.axvspan(x[3], x[4], facecolor='g', alpha=0.15)
    # ax1.axvspan(x[3], x[4], facecolor='g', alpha=0.15)
    n_date = dataset.index[-30]
    init_pos = mdates.date2num(n_date)

    axvline1 = ax1.axvline(x=init_pos, color="k", linewidth=0.5, alpha=0.9)
    axvline2 = ax2.axvline(x=init_pos, color="k", linewidth=0.5, alpha=0.9)
    price = dataset['close'].loc[n_date]
    change = dataset['change'].loc[n_date]
    anno1 = ax1.annotate(price, (init_pos, price), rotation=45)


    date_label = fig.text(0.07, 0.92, "Date: {:.10}".format(str(n_date)))
    price_label = fig.text(0.07, 0.895, "Price: {}  ({:5.2f}%)".format(price, change*100))

    def onClick(event):
        if not event.xdata: return
        pos = int(event.xdata)
        date = mdates.num2date(pos).strftime(DATE_FORMAT)
        if date not in dataset.index:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
            ns = dataset[dataset.index<date]
            date = dataset[dataset.index<date].iloc[-1].name
            pos = mdates.date2num(date)

        axvline1.set_data([pos,pos], [0, 1])
        axvline2.set_data([pos,pos], [0, 1])

        price = dataset['close'].loc[date]
        change = dataset['change'].loc[date]
        date_label.set_text("Date: {:.10}".format(str(date)))
        price_label.set_text("Price: {}  ({:5.2f}%)".format(price, change*100))
        anno1.set_text(price)
        anno1.set_position((pos,price))
        plt.draw()

    zoom_level = None
    def onPress(event):
        global zoom_level
        data = axvline1.get_data()
        pos  = data[0][0]
        date = mdates.num2date(pos).strftime(DATE_FORMAT)
        if date not in dataset.index:
            date = dataset[dataset.index<date].iloc[-1].name
        date_idx = dataset.index.get_loc(date)

        step = 20
        try:
            zoom_level
        except:
            zoom_level = None
        if event.key.lower()=='a' or event.key=='left':
            if len(dataset[date_idx-1:date_idx])>0:
                date = dataset[date_idx-1:date_idx].index[0]
                pos = mdates.date2num(date)
                date_idx = dataset.index.get_loc(date)
        elif event.key.lower()=='d' or event.key=='right':
            if len(dataset[date_idx+1:date_idx+2])>0:
                date = dataset[date_idx+1:date_idx+2].index[0]
                pos = mdates.date2num(date)
                date_idx = dataset.index.get_loc(date)
        elif event.key.lower()=='z':
            if len(dataset[date_idx-step:date_idx])>0:
                date = dataset[date_idx-step:date_idx].index[0]
                pos = mdates.date2num(date)
                date_idx = dataset.index.get_loc(date)
        elif event.key.lower()=='c':
            if len(dataset[date_idx+step:date_idx+step+1])>0:
                date = dataset[date_idx+step:date_idx+step+1].index[0]
                pos = mdates.date2num(date)
                date_idx = dataset.index.get_loc(date)
        elif event.key=='Q':
            zoom_level = 30
        elif event.key.lower()=='w' or event.key=='up':
            zoom_level = 20
        elif event.key.lower()=='e':
            zoom_level = 10
        elif event.key=='escape' \
            or event.key=='down' or event.key.lower()=='s':
            zoom_level = None

        axvline1.set_data([pos,pos], [0, 1])
        axvline2.set_data([pos,pos], [0, 1])


        if zoom_level is None:
            zoom_level = 64
            slice = dataset[date_idx-zoom_level:date_idx+zoom_level]
            if len(slice)>0:
                ax1.set_ylim(slice['close'].min()*0.95,slice['close'].max()*1.05)
            ax1.set_xlim(max(pos-zoom_level,0),pos+zoom_level)
            ax2.set_xlim(max(pos-zoom_level,0),pos+zoom_level)
        else:
            slice = dataset[date_idx-zoom_level:date_idx+zoom_level]
            if len(slice)>0:
                ax1.set_ylim(slice['close'].min()*0.95,slice['close'].max()*1.05)
            ax1.set_xlim(pos-zoom_level,pos+zoom_level)
            ax2.set_xlim(pos-zoom_level,pos+zoom_level)

        price = dataset['close'].loc[date]
        change = dataset['change'].loc[date]
        price_label.set_text("Price: {}  ({:5.2f}%)".format(price, change*100))
        date_label.set_text("Date: {:.10}".format(str(date)))
        anno1.set_text(price)
        anno1.set_position((pos,price))

        plt.draw()

    fig.canvas.mpl_connect('button_press_event', onClick)
    fig.canvas.mpl_connect('key_press_event', onPress)

    # def updateData(i):
    #     yield 1
    # ani = animation.FuncAnimation(fig,  func=updateData, interval=100)
    plt.subplots_adjust(left=0.05, right=0.97, top=0.95, bottom=0.12)
    plt.show()
    return
