#!/usr/bin/env python3

import datetime
import pandas as pd
import math, sys, os
import progressbar
import multiprocessing as mp

from lib.jqdata import *
from lib.func import *
from lib.dna import *

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

filename = 'data/dataset-labeled-2.csv'
np.random.seed(0)
dataset = pd.read_csv(filename,index_col=0)
print('Data loaded')
trading_dates = dataset['security'].groupby(dataset.index).count().index.tolist()
print('Trading dates loaded')

kb = load_kb()
cores = [DNAv4, DNAv5, DNAv6, DNAv7, DNAv8]
total_profit = 1

for trading_date in trading_dates:
    date_i = trading_dates.index(trading_date)
    if date_i<=50:continue

    subset = dataset[dataset.index==trading_date]
    subset = subset[(subset.prev_0<9.5) & (subset.prev_0>-9.5)]
    finished = mp.Value('i', 0)
    def do_work(v):
        global rs
        score = 0
        i = v[0]
        record = v[1]
        for core in cores:
            dna = core.to_dna(record)
            q="(dna=='{}') & (ver=='{}')".format(dna,core.name)
            k = kb[kb.eval(q)]
            if k.shape[0]==0:
                score += 0.5
            else:
                score += k.iloc[0]['wr_f1']

        l.acquire()
        finished.value+=1
        bar.update(finished.value)
        l.release()

        return {
            'date':record.name,
            'security':record.security,
            'close':record.close,
            'prev_2':(record.prev_0+record.prev_1+record.prev_2+record.prev_2),
            'today':record.prev_0,
            'score':score,
            'fu_1':record['fu_1'],
            'fu_2':record['fu_2'],
            'fu_3':record['fu_3'],
            'fu_4':record['fu_4'],
        }

    bar = progressbar.ProgressBar(max_value=len(subset))
    m = mp.Manager()
    l = m.Lock()
    p = mp.cpu_count()
    # pool = mp.Pool(processes=p)
    # res = pool.map(do_work,subset.iterrows())
    # pool.close()
    # pool.join()
    # rs = pd.DataFrame(res)
    rs = subset

    rs['prev_past'] = rs['prev_0']+rs['prev_1']+rs['prev_2']+rs['prev_3']+rs['prev_4']+rs['prev_5']
    today_wr = rs[rs.prev_0>0].shape[0] / rs.shape[0]


    rs = rs[(rs.prev_0>0) & (rs.prev_1<0) & (rs.prev_2<0) & (rs.prev_3<0) ]
    rs = rs.sort_values(by=['prev_past'],ascending=True)
    rs = rs[:15]
    rs = rs.sort_values(by=['prev_0'],ascending=True)
    rs = rs[:4]



    rs = rs[['security','close','prev_past','prev_0','fu_1','fu_2','fu_3','fu_3','fu_4']]
    print("\n")
    print("="*100)
    print(rs)
    print("="*100)

    if rs.shape[0]>0:
        total_profit = total_profit*(1+(rs['fu_1'].mean()/100))
    else:
        print('Ignored')

    print("{:06}\tDate: {}\t Profit: {:.2f}%\t Total: {:.2f}%\t\t wr: {:.3f}".format(
                date_i,trading_date,rs['fu_1'].mean(),total_profit*100,today_wr))

    print("\n")
