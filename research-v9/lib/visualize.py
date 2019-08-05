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
    # cols = ['short','median','long','close','pos_5','pos_3','pos_10']
    # cols.extend(['date'])
    df = pd.DataFrame(dataset)
    df = df.set_index(keys=['date'])
    return df

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[-1] - baseline['close'].iloc[0])
                    / baseline['close'].iloc[0] * 100,2)

def visualize_report(dataset,backtest,strategy):
    dataset = dataset.copy()
    dataset.index = pd.to_datetime(dataset.index, format=DATE_FORMAT)
    baseline_profits = calc_baseline_profit(backtest)

    xlabel = dataset.index.strftime(DATE_FORMAT).tolist()
    x = pd.to_datetime(dataset.index).tolist()


    register_matplotlib_converters()

    max_width = min(len(x), 100)
    if 'action' not in dataset.columns:
        dataset['action']=""

    dataset['ma3'] = dataset['close'].rolling(window=3).mean()
    dataset['ma5'] = dataset['close'].rolling(window=5).mean()
    dataset['ma10'] = dataset['close'].rolling(window=10).mean()
    dataset['ma30'] = dataset['close'].rolling(window=30).mean()
    dataset['ma60'] = dataset['close'].rolling(window=60).mean()
    dataset['num_date'] = mdates.date2num(dataset.index.to_pydatetime())

    mpl.style.use('dark_background')
    mpl.rcParams['toolbar'] = 'None'
    gs = gridspec.GridSpec(3, 3)
    fig =plt.figure(figsize=(15,8))
    ax1 =plt.subplot(gs[:2,:])

    buy_points = dataset[dataset.buy==1]
    buy_points_x = pd.to_datetime(buy_points.index).tolist()
    ax1.scatter(buy_points_x, buy_points['low']-0.1, alpha=0.8,color='w',s=10)

    if 'buy_pred' in dataset.columns:
        buy_preds = dataset[dataset.buy_pred>0.5]
        buy_preds_x = pd.to_datetime(buy_preds.index).tolist()
        # ax1.scatter(buy_preds_x, buy_preds['low']-0.15, alpha=0.9,color='#34ebde',s=6, marker="^")
        idx = 0
        while idx <= len(buy_preds)-1:
            end_date = buy_preds.iloc[idx].name
            buy_pred = buy_preds.iloc[idx]['buy_pred']
            v_pos = buy_preds.iloc[idx]['low']-0.15
            end_date = mdates.date2num(end_date)
            ax1.scatter(end_date, v_pos, alpha=buy_pred,color='#34ebde',s=20, marker="x")
            # ax1.annotate("<        {:.1f}".format(buy_pred),(end_date, v_pos),
            #     weight='bold',ha='left', va='bottom', color='#34ebde', fontsize=7,rotation=-90)
            idx+=1

    ax1.plot(x, dataset['ma3'],label='MA3', alpha=0.9, color='r')
    ax1.plot(x, dataset['ma3'],label='MA3', alpha=0.9, color='r')
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
    ax1.set_ylabel('close price')
    ax1.set_ylim(dataset['close'][-max_width:].min()*0.95,dataset['close'][-max_width:].max()*1.05)

    title = "Baseline: {:.2f}%   Strategy: {:.2g}% ".format(
        baseline_profits,strategy.get_profit(backtest['close'].iloc[-1]))
    subtitle = "From {:.10}    to {:.10}    Duration: {} days".format(str(dataset.index[0]), str(dataset.index[-1]), len(dataset))
    fig.text(0.05, 0.96, title, fontsize=10, weight='bold')
    fig.text(0.97, 0.96, subtitle, ha='right', fontsize=10)

    candlestick_ohlc(ax1, zip(
        dataset['num_date'],
        backtest['open'], backtest['high'],
        backtest['low'], backtest['close']
    ), width=0.4, colordown='#77d879', colorup='#db3f3f')


    ax2 =plt.subplot(gs[2,:])
    ax2.plot(x, dataset['f1d_pos'],  label='f1d_pos',  alpha=0.7, marker=".")
    ax2.plot(x, dataset['f2d_pos'],  label='f2d_pos', alpha=0.4)
    ax2.plot(x, dataset['f3d_pos'],  label='f3d_pos', alpha=0.4)
    ax2.plot(x, dataset['f5d_pos'],  label='f5d_pos', alpha=0.4)
    ax2.plot(x, dataset['f8d_pos'],  label='f8d_pos', alpha=0.4)

    ax2.set_ylabel('score')
    ax2.legend(loc='upper right')
    ax2.set_xticks(x)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))
    ax2.set_xticklabels(xlabel,rotation=45, rotation_mode="default",alpha=0.5)
    ax2.set_yticks(np.round(np.linspace(0,9, 10),2))
    ax2.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax2.set_ylim(-0.5,9.5)
    ax2.set_xlim(x[-max_width],x[-1])
    ax2.set_title("Features")
    ax2.grid(color='gray',which='major',linestyle='dashed',alpha=0.35)
    ax2.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)
    ax2.axhspan(2, 5, facecolor='blue', alpha=0.05)

    # 标记获利还是亏损

    idx = 0
    while idx <= len(dataset)-1:
        row = dataset.iloc[idx]
        if row['action']=='buy':
            start_date_n =row['num_date']
            start_date = row.name
            bought_price = row['close']
            while idx <= len(dataset)-1:
                row = dataset.iloc[idx]

                if row['action']=='sell':
                    end_date_n = row['num_date']
                    end_date = row.name
                    sell_price = row['close']
                    color = '#177508'
                    annon_y_pos  = sell_price*0.95
                    sell_marker = "v"
                    profit = (sell_price - bought_price) / bought_price
                    if profit>0:
                        color = '#960e0e'
                        annon_y_pos = sell_price*1.05
                        sell_marker = "^"
                    ax2.axvspan(start_date, end_date, facecolor=color, alpha=0.15)
                    ax1.axvspan(start_date, end_date, facecolor=color, alpha=0.15)
                    ax1.plot(start_date, bought_price, marker=6, color='w')
                    ax1.plot(end_date, sell_price, marker="_", color="w")
                    ax1.plot(end_date, annon_y_pos, marker=sell_marker, color=color)
                    ax1.annotate("  {:.1f}%".format(profit*100),(end_date, annon_y_pos),
                        weight='bold',ha='left', va='center', color=color, rotation=0)
                    break
                idx+=1
        else:
            idx+=1




    n_date = dataset.index[-30]
    init_pos = mdates.date2num(n_date)

    axvline1 = ax1.axvline(x=init_pos, color="w", linewidth=0.5, alpha=0.9)
    axvline2 = ax2.axvline(x=init_pos, color="w", linewidth=0.5, alpha=0.9)
    price = dataset['close'].loc[n_date]
    change = dataset['change'].loc[n_date]


    date_label = fig.text(0.07, 0.92, "Date: {:.10}".format(str(n_date)))
    price_label = fig.text(0.07, 0.895, "Price: {}  ({:5.2f}%)".format(price, change*100))

    # pos5_label = fig.text(0.07, 0.34,  "05D_POS: {}".format( dataset['f5d_pos'].loc[n_date] ))
    # pos10_label = fig.text(0.07, 0.315, "10D_POS: {}".format( dataset['f10d_pos'].loc[n_date] ))
    # pos30_label = fig.text(0.07, 0.315-0.025, "30D_POS: {}".format( dataset['f30d_pos'].loc[n_date] ))
    # pos60_label = fig.text(0.07, 0.315-0.05, "60D_POS: {}".format( dataset['f60d_pos'].loc[n_date] ))

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

        # pos5_label.set_text("05D_POS: {}".format( dataset['f5d_pos'].loc[date] ))
        # pos10_label.set_text("10D_POS: {}".format( dataset['f10d_pos'].loc[date] ))
        # pos30_label.set_text("30D_POS: {}".format( dataset['f30d_pos'].loc[date] ))
        # pos60_label.set_text("60D_POS: {}".format( dataset['f60d_pos'].loc[date] ))

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

                date = mdates.num2date(pos).strftime(DATE_FORMAT)
                if date not in dataset.index:
                    date = datetime.datetime.strptime(date, DATE_FORMAT)
                    ns = dataset[dataset.index<date]
                    date = dataset[dataset.index<date].iloc[-1].name
                    pos = mdates.date2num(date)
                date_idx = dataset.index.get_loc(date)
        elif event.key.lower()=='d' or event.key=='right':
            if len(dataset[date_idx+1:date_idx+2])>0:
                date = dataset[date_idx+1:date_idx+2].index[0]
                pos = mdates.date2num(date)

                date = mdates.num2date(pos).strftime(DATE_FORMAT)
                if date not in dataset.index:
                    date = datetime.datetime.strptime(date, DATE_FORMAT)
                    ns = dataset[dataset.index>date]
                    date = dataset[dataset.index>date].iloc[-1].name
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
        elif event.key.lower()=='w' or event.key=='up':
            zoom_level = 30
        elif event.key.lower()=='e':
            zoom_level = 20
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

        # pos5_label.set_text("05D_POS: {}".format( dataset['f5d_pos'].loc[date] ))
        # pos10_label.set_text("10D_POS: {}".format( dataset['f10d_pos'].loc[date] ))
        # pos30_label.set_text("30D_POS: {}".format( dataset['f30d_pos'].loc[date] ))
        # pos60_label.set_text("60D_POS: {}".format( dataset['f60d_pos'].loc[date] ))

        plt.draw()

    fig.canvas.mpl_connect('button_press_event', onClick)
    fig.canvas.mpl_connect('key_press_event', onPress)

    plt.subplots_adjust(left=0.05, right=0.97, top=0.95, bottom=0.12)
    plt.show()
    return
