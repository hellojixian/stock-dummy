#!/usr/bin/env python3

import datetime
import math, sys, os
import progressbar
import multiprocessing as mp
import numpy as np
import pandas as pd

from lib.jqdata import *


# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def gen_bits(len):
    bits=[]
    max = "0b"+(''.join(str(e) for e in ['1']*len))
    for i in range(int(max,2)):
        s =  ("{0:0"+str(DNA_LEN)+"b}").format(i)
        bits.append(s)
    return bits


def to_query_v1(dna):
    # 4bits for trend
    # 4bits for prev_4-7
    # 8bits for prev_0-4
    step = 2
    query="(trend_60=={}) & (trend_30=={}) & (trend_20=={}) & (trend_10=={}) & (trend_5=={}) & ".format(
            dna[0],dna[1],dna[2],dna[3],dna[4])
    for i in range(5,10):
        op='<'
        if int(dna[i])==1: op='>'
        query += "(prev_{}{}0) & ".format(8+4-i,op)
    for i in range(10,16,2):
        val, op = 0,'<'
        if int(dna[i+1])==1: val,op=-step,'<='
        if int(dna[i])==1:
            val, op = 0,'>'
            if int(dna[i+1])==1: val,op=step,'>='


        query += "(prev_{}{}{}) & ".format(3+int(4-i/2),op,val)
    query = query[:-2]
    return query


finished = mp.Value('i', 0)
def do_work(dna):
    global finished
    global lock
    global DNA_LEN,DNAset
    lock = l

    q = to_query_v1(dna)
    subset = dataset[dataset.eval(q)]
    total = subset.shape[0]
    if total==0: return None
    wr_f1 = subset[subset.eval("(fu_1)>0")].shape[0]/total
    wr_f2 = subset[subset.eval("(fu_2)>0")].shape[0]/total
    wr_f3 = subset[subset.eval("(fu_3)>0")].shape[0]/total
    wr_f4 = subset[subset.eval("(fu_4)>0")].shape[0]/total
    wr_f5 = subset[subset.eval("(fu_5)>0")].shape[0]/total
    record = pd.Series({
        'ver':'v1',
        'dna':dna,
        'wr_f1':wr_f1,
        'wr_f2':wr_f2,
        'wr_f3':wr_f3,
        'wr_f4':wr_f4,
        'wr_f5':wr_f5,
        'samples':total
    }, name=int(dna,2))

    print("{:.2f}%\t{}\twr_f1:{:.2f}\twr_f2:{:.2f}\twr_f3:{:.2f}\ttotal:{}".format(finished.value/len(DNAset)*100,dna,wr_f1,wr_f2,wr_f3,total))
    finished.value+=1
    return record

filename = 'data/dataset-labeled-2.csv'
dataset = pd.read_csv(filename,index_col=0)

print(dataset.shape)

DNA_LEN = 16
DNAset = gen_bits(DNA_LEN)
bar = progressbar.ProgressBar(max_value=len(DNAset))


m = mp.Manager()
l = m.Lock()
pool = mp.Pool(processes=mp.cpu_count())
res = pool.map(do_work,DNAset)
pool.close()
pool.join()

qtable = pd.DataFrame()
for r in res:
    if r is not None: qtable = qtable.append(r)
qtable = qtable.sort_values(by=['wr_f1'],ascending=False)
qtable.to_csv('data/report_len{}.csv'.format(DNA_LEN))
print(qtable)
