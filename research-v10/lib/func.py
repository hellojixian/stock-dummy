import datetime
import pandas as pd
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



def extract_feature_worker(v):
    i = v[0]
    row = v[1]
    security = row['security']
    dataset = pd.DataFrame()
    # history = get_price(security, start_date=start_date, end_date=end_date,
    #                         skip_paused=True)
    #
    # for i in range(0,10):
    #     history['prev_{}'.format(i)] = (history['close'].shift(periods=i) - history['close'].shift(periods=i+1) )/history['close'].shift(periods=i+1)*100
    #     history['prev_{}'.format(i)] = np.round(history['prev_{}'.format(i)],2)
    #
    # for i in range(0,5):
    #     history['fu_{}'.format(i+1)] = (history['close'].shift(periods=-i-1) - history['close'].shift(periods=0) )/history['close'].shift(periods=0)*100
    #     history['fu_{}'.format(i+1)] = np.round(history['fu_{}'.format(i+1)],2)
    #
    # history.drop(columns=['high','low','volume','money'])
    # history=history.dropna()
    # dataset = dataset.append(history)
    # dataset.to_csv(filename)

    print(i, security)
    return v
