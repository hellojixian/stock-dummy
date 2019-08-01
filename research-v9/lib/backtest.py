#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec

from pandas.plotting import register_matplotlib_converters

def generate_report(dataset):
    cols = ['short','median','long','close']
    cols.extend(['date'])
    df = pd.DataFrame(dataset, columns=cols)
    df = df.set_index(keys=['date'])
    return df

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[-1] - baseline['close'].iloc[0])
                    / baseline['close'].iloc[0] * 100,2)


def visualize_report(dataset,backtest):
    baseline_profits = calc_baseline_profit(backtest)

    xlabel = dataset.index.tolist()
    x = pd.to_datetime(dataset.index).tolist()
    register_matplotlib_converters()

    gs = gridspec.GridSpec(3, 3)
    fig =plt.figure(figsize=(14,8))
    ax1 =plt.subplot(gs[:2,:])
    ax1.plot(x, dataset['close'],label='Price', alpha=0.5, color='r')
    ax1.legend(loc='upper right')
    ax1.set_xticks(x)
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax1.set_xlim(x[0],x[-1])
    ax1.set_xticklabels([])
    ax1.grid(color='gray',which='major',linestyle='dashed',alpha=0.3)
    ax1.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)
    ax1.set_title("Baseline Profit: {:.2f}%".format(baseline_profits))
    ax1.set_ylabel('close price')

    ax2 =plt.subplot(gs[2,:])
    ax2.plot(x, dataset['short'],label='short_pos', alpha=0.4, color='r')
    ax2.plot(x, dataset['median'],label='median_pos', alpha=0.3, color='g')
    ax2.plot(x, dataset['long'],label='long_pos', alpha=0.15, color='b')

    ax2.set_ylabel('score')
    ax2.legend(loc='upper right')
    ax2.set_xticks(x)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.set_xticklabels(xlabel,rotation=45, rotation_mode="default",alpha=0.5)
    ax2.set_yticks(np.round(np.linspace(0,7, 8),2))
    ax2.set_ylim(0,7)
    ax2.set_xlim(x[0],x[-1])
    ax2.set_title("Features")
    ax2.grid(color='gray',which='major',linestyle='dashed',alpha=0.3)
    ax2.grid(color='gray',which='minor',linestyle='dashed',alpha=0.15)

    # 标记获利还是亏损
    # ax2.axvspan(x[3], x[4], facecolor='g', alpha=0.15)
    # ax1.axvspan(x[3], x[4], facecolor='g', alpha=0.15)
    plt.show()
    return
