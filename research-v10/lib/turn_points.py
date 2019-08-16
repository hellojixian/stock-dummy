from rdp import rdp
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import math, sys, os

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
    points = history[['num_date',field]].values
    if epsilon is None:
        short_his = history[-5:].copy()
        short_his['amp'] = short_his['high'] - short_his['low']
        ma_amp = short_his['amp'].mean()
        epsilon = ma_amp
    turn_points = _find_turn_points(points, epsilon=epsilon)
    turn_points = pd.DataFrame(turn_points,columns=['num_date','price'])
    turn_points['direction'] = 'unknown'
    for i in range(0,turn_points.shape[0]-1):
        if turn_points['price'].iloc[i] < turn_points['price'].iloc[i+1]:
            turn_points.loc[i,'direction'] = 'up'
        else:
            turn_points.loc[i,'direction'] = 'down'
    return turn_points
