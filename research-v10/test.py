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
filename = 'data/dataset-labeled-2.csv'

start_date=datetime.date(2008,4,15)
end_date=datetime.date(2019,7,15)
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

security_list = security_list[:10]
bar = progressbar.ProgressBar(max_value=len(security_list))

def do_work(v):
    i = v[0]
    row = v[1]
    security = row['security']
    # print(filename)
    time.sleep(0.1)
    bar.update(i+1)
    return v


pool = mp.Pool(processes=mp.cpu_count())

# for _ in progressbar.progressbar(pool.map(do_work,security_list.iterrows()),max_value=len(security_list), redirect_stdout=True):
#     # print(_)
#     pass
pool.map(do_work,security_list.iterrows())
print('done')
