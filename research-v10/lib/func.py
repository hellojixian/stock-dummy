import datetime
import pandas as pd
import numpy as np
import math, sys, os

def find_turnup_points(history):
    points = []
    for i in range(10,history.shape[0]-5):
        closes = history['close']
        past = closes[i-6:i+1]
        future = closes[i:i+6]
        if  past.min() == closes.iloc[i] and \
            future.min() == closes.iloc[i] and \
            (future.max() - future.min()) / future.min() > 0.04 and \
            closes.iloc[i+1] > closes.iloc[i]:
            points.append(history.iloc[i])
    return pd.DataFrame(points)

def find_turndown_points(history):
    points = []
    for i in range(10,history.shape[0]-5):
        closes = history['close']
        past = closes[i-6:i+1]
        future = closes[i:i+6]
        if  past.max() == closes.iloc[i] and \
            future.max() == closes.iloc[i] and \
            (past.max() - past.min()) / past.min() > 0.05 and \
            (future.max() - future.min()) / future.max() > 0.02 and \
            closes.iloc[i+1] < closes.iloc[i]:
            points.append(history.iloc[i])
    return pd.DataFrame(points)

def find_buysell_points(history):
    turnup_points = find_turnup_points(history)
    turndown_points = find_turndown_points(history)

    for i in range(turnup_points.shape[0]-1):
        sp = turnup_points['id'].iloc[i]
        ep = turnup_points['id'].iloc[i+1]
        query = "(id>{}) & (id<{})".format(sp,ep)
        if turndown_points[turndown_points.eval(query)].shape[0]==0:
            subset = history[history.eval(query)]
            tp = subset[subset.close==subset['close'].max()].iloc[0]
            turndown_points = turndown_points.append(tp)
            turndown_points = turndown_points.sort_values(by=['id'], ascending=True)

    for i in range(turndown_points.shape[0]-1):
        sp = turndown_points['id'].iloc[i]
        ep = turndown_points['id'].iloc[i+1]
        query = "(id>{}) & (id<{})".format(sp,ep)
        if turnup_points[turnup_points.eval(query)].shape[0]==0:
            # need to add turn down point
            subset = history[history.eval(query)]
            tp = subset[subset.close==subset['close'].min()].iloc[0]
            turnup_points = turnup_points.append(tp)
            turnup_points = turnup_points.sort_values(by=['id'], ascending=True)

    drop_uppoints, drop_downpoints = [],[]
    for i in range(turnup_points.shape[0]-1):
        limit = 0.03
        price_low = turnup_points['close'].iloc[i]
        price_high = turndown_points['close'].iloc[i]
        if (price_high-price_low)/price_low < limit:
            drop_uppoints.append(turnup_points.index[i])
            drop_downpoints.append(turndown_points.index[i])

    turnup_points = turnup_points.drop(labels=drop_uppoints)
    turndown_points = turndown_points.drop(labels=drop_downpoints)

    history['action'] = ''
    history['hold'] = 0

    if turnup_points.shape[0]>0 and turndown_points.shape[0]>0 \
        and turnup_points.iloc[0].name > turndown_points.iloc[0].name:
            turndown_points = turndown_points[1:]

    if turnup_points.shape[0]>0 and turndown_points.shape[0]>0 \
        and turnup_points.iloc[-1].name > turndown_points.iloc[-1].name:
            turnup_points = turnup_points[:-1]

    if turnup_points.shape[0]>0 and turndown_points.shape[0]>0:
        for i in range(turnup_points.shape[0]):
            sp = turnup_points.iloc[i].name
            ep = turndown_points.iloc[i].name
            history.loc[sp+1:ep,'hold']=1
            history.loc[sp,'action']='buy'
            history.loc[ep,'action']='sell'

    return turnup_points,turndown_points, history


def get_prime_numbers(vmin,vmax):
    pn=[]
    for a in range(vmin,vmax):
        k = 0
        for i in range(2,a):
            if a % i == 0 : k += 1
        if k == 0 : pn.append(a)
    return pn

def find_trend(values):
    values = list(values)
    p_min, p_max = np.min(values), np.max(values)
    p_min_idx, p_max_idx = values.index(p_min), values.index(p_max)
    # down trend
    trend = 0
    if p_max_idx > p_min_idx:
        # up trend
        trend = 1
    return trend

def find_pos(values):
    values = list(values)
    close = values[-1]
    p_min, p_max = np.min(values), np.max(values)
    pos = (close - p_min) / (p_max - p_min) * 100
    pos = np.round(pos,2)
    return pos

def find_ma_pos(values):
    values = list(values)
    close = values[-1]
    v_mean = np.mean(values)
    pos = (close - v_mean) / v_mean * 100
    pos = np.round(pos,2)
    return pos

def calc_changes(values):
    values = list(values)
    p = 1
    for v in values:
        p *= (1+v/100)
    c = np.round((p-1)*100,2)
    return c

def calc_down_trend_days(values):
    print(values)
    assert(False)
    values = list(values)
    values.reverse()

    days = 0
    for i in range(len(values)):
        v=values[i]
        if v>=0.5: break
        days+=1
    return days

def calc_up_rate(values):
    values = list(values)
    v_min = np.min(values)
    last = values[-1]
    return (last - v_min) / v_min

def calc_down_rate(values):
    values = list(values)
    v_max = np.max(values)
    last = values[-1]
    rate = (v_max - last) / v_max
    return rate

def calc_change_ma(values):
    values = list(values[:-1])
    return np.mean(np.abs(values))


def load_kb():
    kb = pd.DataFrame()
    data_folder = 'data'
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file[:5] == 'dna_v' and file[-4:]=='.csv':
                subset = pd.read_csv(os.path.join(data_folder,file),index_col=0,dtype=str)
                print('Load {} records from {}'.format( subset.shape[0], file ))
                kb = kb.append(subset)
    kb = kb.reset_index()
    kb = kb.drop(columns=['index'])
    for col in kb.columns:
        if col[:3]=='wr_':
            kb[col] = kb[col].astype(float)
    return kb
