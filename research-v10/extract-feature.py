#!/usr/bin/env python3

import datetime
import pandas as pd
import numpy as np
import math, sys, os
import progressbar
import multiprocessing as mp
from lib.jqdata import *

start_date=datetime.date(2008,4,15)
end_date=datetime.date(2019,7,15)
np.random.seed(0)

security_list = get_all_securites()
bar = progressbar.ProgressBar(max_value=len(security_list))

filename = 'data/dataset-labeled-2.csv'

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
    sec_i = v[0]
    row = v[1]
    security = row['security']

    history = get_price(security, start_date=start_date, end_date=end_date,
                            skip_paused=True)

    for i in range(0,10):
        history['prev_{}'.format(i)] = (history['close'].shift(periods=i) - history['close'].shift(periods=i+1) )/history['close'].shift(periods=i+1)*100
        history['prev_{}'.format(i)] = np.round(history['prev_{}'.format(i)],2)

    for i in range(0,5):
        history['fu_{}'.format(i+1)] = (history['close'].shift(periods=-i-1) - history['close'].shift(periods=0) )/history['close'].shift(periods=0)*100
        history['fu_{}'.format(i+1)] = np.round(history['fu_{}'.format(i+1)],2)

    history.drop(columns=['high','low','volume','money'])
    history=history.dropna()

    f = "{}-{}".format(filename,sec_i)
    should_output_header = False
    if sec_i == 0:
        should_output_header=True
    history.to_csv(f, index=True, header=should_output_header)

    cmd = "cat {} >> {}".format(f,filename)
    os.system(cmd)
    os.remove(f)
    finished.value+=1
    bar.update(finished.value)
    return v

pool = mp.Pool(processes=mp.cpu_count())
pool.map(do_work,security_list.iterrows())

print('done')
