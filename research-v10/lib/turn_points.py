from rdp import rdp
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import math, sys, os
import talib as ta

def _find_turn_points(points, epsilon):
    simplified = rdp(points, epsilon=epsilon)
    directions = np.diff(simplified[:,1])
    idx_keep = [points[0]]
    for i in range(directions.shape[0]-1):
        if (directions[i]>=0 and directions[i+1]<0)\
            or (directions[i]<=0 and directions[i+1]>0):
            idx_keep.append(simplified[i+1])
    idx_keep.append(points[-1])
    idx_keep = np.array(idx_keep)
    return idx_keep

def find_turn_points(history, epsilon=None, field='close'):
    points = history[['id',field]].values
    if epsilon is None:
        short_his = history[-5:].copy()
        short_his['amp'] = short_his['high'] - short_his['low']
        ma_amp = short_his['amp'].mean()
        epsilon = ma_amp
    turn_points = _find_turn_points(points, epsilon=epsilon)
    turn_points = pd.DataFrame(turn_points,columns=['id','price'])
    turn_points['direction'] = 'unknown'
    for i in range(0,turn_points.shape[0]-1):
        if turn_points['price'].iloc[i] < turn_points['price'].iloc[i+1]:
            turn_points.loc[i,'direction'] = 'up'
        else:
            turn_points.loc[i,'direction'] = 'down'
    turn_points['id'] = turn_points['id'].astype('i')

    # logic for fixing the tail
    last_tp = turn_points.iloc[-2]
    last_tp_price = turn_points.iloc[-2]['price']
    last_price = turn_points.iloc[-1]['price']
    last_id = turn_points.iloc[-1]['id']
    last_subset = history[history.id>=last_tp['id']][['id',field]]
    last_direction = turn_points.iloc[-2]['direction']
    last_min, last_max = last_subset[field].min(), last_subset[field].max()
    last_min_idx = int(last_subset[last_subset.eval("{}=={}".format(field,last_min))]['id'].iloc[0])
    last_max_idx = int(last_subset[last_subset.eval("{}=={}".format(field,last_max))]['id'].iloc[0])

    fuzzy_rate = 0.01
    if last_direction == 'up' \
        and (last_price != last_max or last_tp_price!=last_min):
        turn_points = turn_points[:-1].copy()
        # prev_idx = turn_points.iloc[-1].name
        # turn_points.loc[prev_idx,'id'] = last_min_idx
        # turn_points.loc[prev_idx,'price'] = last_min
        turn_points = turn_points.append(pd.Series({
            'id':last_max_idx,
            'price':last_max,
            'direction':'down'
            }),ignore_index=True)
        if last_price != last_max:
            turn_points = turn_points.append(pd.Series({
                'id':last_id,
                'price':last_price,
                'direction':'up'
                }),ignore_index=True)
        print('need fix up')
    if last_direction == 'down' \
        and (last_price != last_min or last_tp_price!=last_max):
        turn_points = turn_points[:-1].copy()


        turn_points = turn_points.append(pd.Series({
            'id':last_min_idx,
            'price':last_min,
            'direction':'up'
            }),ignore_index=True)
        if last_price != last_min:
            turn_points = turn_points.append(pd.Series({
                'id':last_id,
                'price':last_price,
                'direction':'down'
                }),ignore_index=True)
        print(turn_points)
        print('need fix down')
    # print(np.min(last_subset))
    # print(points['price'][:])
    # if idx_keep[-2][1] == points['price'][idx_keep['id'][-2]:].min():
    #     print('got it')
    return turn_points

def find_trend(values, history):
    history = history[int(values[0]):int(values[-1])]
    trends = []
    periods = [53, 29, 13, 7, 5, 3]
    weights = [3, 2, 1.5, 1, 0.5, 1.5]
    for period,weight in zip(periods, weights):
        subset = history[-period:]
        p_min, p_max = subset['low'].min(), subset['high'].max()
        p_min_idx = subset[subset.low==p_min].iloc[-1].name
        p_max_idx = subset[subset.high==p_max].iloc[-1].name

        trend = 0
        if p_max_idx > p_min_idx:
            # up trend
            trend =  + 1
        if p_max_idx < p_min_idx:
            # down trend
            trend = - 1
        trends.append(trend * weight)
    final_trend = np.sum(trends) / np.sum(weights)
    print("{:.10} {:.2f}".format(str(history['index'].iloc[-1]), final_trend))
    return final_trend

def HMA(data, periods = 4):
    wmaA = ta.WMA(data,timeperiod = periods / 2) * 2
    wmaB = ta.WMA(data,timeperiod = periods)
    wmaDiffs = wmaA - wmaB
    hma = ta.WMA(wmaA - wmaB, math.sqrt(periods))
    return hma
