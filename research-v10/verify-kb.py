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
cores = [DNAv1, DNAv2, DNAv3, DNAv4, DNAv5, DNAv6, DNAv7, DNAv8]

for trading_date in trading_dates:
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
                score += k.iloc[0]['wr_f1']+k.iloc[0]['wr_f2']

        l.acquire()
        finished.value+=1
        bar.update(finished.value)
        l.release()

        return {
            'date':record.name,
            'security':record.security,
            'close':record.close,
            'prev_2':(record.prev_0+record.prev_1+record.prev_2),
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
    pool = mp.Pool(processes=p)
    res = pool.map(do_work,subset.iterrows())
    pool.close()
    pool.join()

    rs = pd.DataFrame(res)
    # rs = rs.sort_values(by=['score'],ascending=False)
    score_mean=rs['score'].mean()
    score_q95=rs['score'].quantile(0.95)
    rs = rs[(rs.score>=9)]
    rs = rs.sort_values(by=['prev_2','today'],ascending=True)
    rs = rs[:5]
    rs['score'] = np.round(rs['score'],3)
    rs = rs[['date','security','close','prev_2','today','score','fu_1','fu_2','fu_3','fu_3','fu_4']]
    print("\n")
    print("="*100)
    print(rs)
    print("="*100)

    if score_mean<=4:
        print("Date: {}\t Profit: {:.2f}%\t Score(50/95): {:.3f}/{:.3f} - Ignored".format(
                trading_date,rs['fu_1'].mean(),score_mean,score_q95))
    else:
        print("Date: {}\t Profit: {:.2f}%\t Score(50/95): {:.3f}/{:.3f}".format(
                trading_date,rs['fu_1'].mean(),score_mean,score_q95))

    print("\n")
