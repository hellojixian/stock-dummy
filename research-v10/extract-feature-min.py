#!/usr/bin/env python3

import datetime
import pandas as pd
import numpy as np
import math, sys, os
import progressbar
import multiprocessing as mp
from lib.jqdata import *
from lib.func import *

start_date=datetime.date(2008,4,15)
end_date=datetime.date(2019,7,15)
np.random.seed(0)

security_list = get_all_securites()
bar = progressbar.ProgressBar(max_value=len(security_list))

filename = 'data/dataset-labeled-min.csv'

start_date=datetime.date(2008,4,15)
end_date=datetime.date(2019,7,15)
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


finished = mp.Value('i', 0)
def do_work(v):
    global finished
    global lock
    lock = l
    sec_i = v[0]
    row = v[1]
    security = row['security']

    history = get_price(security, start_date=start_date, end_date=end_date,
                            skip_paused=True)

    for i in range(0,3):
        history['prev_{}'.format(i)] = (history['close'].shift(periods=i) - history['close'].shift(periods=i+1) )/history['close'].shift(periods=i+1)
        history['prev_{}'.format(i)] = np.round(history['prev_{}'.format(i)]*100,2)

    for i in range(0,1):
        history['fu_{}'.format(i+1)] = (history['close'].shift(periods=-i-1) - history['close'].shift(periods=0) )/history['close'].shift(periods=0)
        history['fu_{}'.format(i+1)] = np.round(history['fu_{}'.format(i+1)]*100,2)

    # for i in [10]:
    #     history['trend_{}'.format(i)] = history['close'].rolling(window=i).apply(find_trend,raw=True)

    # for i in [5,10,15,20,25]:
    #     history['money_ma_{}'.format(i)] = history['money'].rolling(window=i).mean()
    #
    # for i in [20,15,10,7,6,5]:
    #     history['amp_{}'.format(i)] = (history['close'].rolling(window=i).max() - history['close'].rolling(window=i).min()) / history['close'].rolling(window=i).min()
    #     history['amp_{}'.format(i)] = np.round(history['amp_{}'.format(i)]*100,2)
    #
    # for i in [5,6,7,8,10,60,90,120]:
    #     history['pos_{}'.format(i)] = history['close'].rolling(window=i).apply(find_pos,raw=True)
    #     for j in range(1,4):
    #         history['prev_pos_{}_{}'.format(i,j)] = history['pos_{}'.format(i)].shift(periods=j)
    #
    # # for i in [15,10,5]:
    #     history['change_ma_{}'.format(i)] = history['prev_0'].rolling(window=i).apply(calc_change_ma,raw=True)

    for i in [25]:
        history['prev_changes_{}'.format(i)] = history['prev_0'].rolling(window=i).apply(calc_changes,raw=True)

    for i in [120]:
        history['down_rate'.format(i)] = history['close'].rolling(window=i).apply(calc_down_rate,raw=True)
        history['up_rate'.format(i)] = history['close'].rolling(window=i).apply(calc_up_rate,raw=True)

    for i in [3]:
        history['down_rate_ma'.format(i)] = history['down_rate'].rolling(window=i).mean()
    # for i in range(0,3):
    #     history['down_rate_ma_{}'.format(i)] = history['down_rate_ma'].shift(periods=i)
    for i in range(0,3):
        history['prev_down_rate_{}'.format(i)] = history['down_rate'].shift(periods=i)

    # for i in [10,20,60]:
    #     history['pos_vol_{}'.format(i)] = history['volume'].rolling(window=i).apply(find_pos,raw=True)

    # for i in [5,10,15]:
    #     history['pos_vol_10_ma_{}'.format(i)] = history['pos_vol_10'].rolling(window=i).mean()
    #
    # for i in range(0,2):
    #     history['prev_vol_{}'.format(i)] = (history['volume'].shift(periods=i) - history['volume'].shift(periods=i+1) )/history['volume'].shift(periods=i+1)
    #     history['prev_vol_{}'.format(i)] = np.round(history['prev_vol_{}'.format(i)]*100,2)



    history.drop(columns=['high','low','volume','money'])
    history=history.dropna()

    f = "{}-{}".format(filename,sec_i)
    should_output_header = False
    if sec_i == 0:
        should_output_header=True
    lock.acquire()
    history.to_csv(f, index=True, header=should_output_header)

    cmd = "cat {} >> {}".format(f,filename)
    os.system(cmd)
    os.remove(f)
    finished.value+=1
    lock.release()
    bar.update(finished.value)
    return v

m = mp.Manager()
l = m.Lock()
if os.path.isfile(filename): os.remove(filename)
p = mp.cpu_count()
if mp.cpu_count()>4: p = mp.cpu_count()-1
pool = mp.Pool(processes=p)
do_work((0,security_list.iloc[0]))
pool.map(do_work,security_list[1:].iterrows())
pool.close()
pool.join()
print('done')
