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


def to_query(dna):
    # 4bits for trend
    # 4bits for prev_4-7
    # 8bits for prev_0-4
    step = 2
    query="(trend_60=={}) & (trend_30=={}) & (trend_20=={}) & (trend_10=={}) & ".format(
            dna[0],dna[1],dna[2],dna[3])
    for i in range(4,8):
        op='<'
        if int(dna[i])==1: op='>'
        query += "(prev_{}{}0) & ".format(7+4-i,op)
    for i in range(8,16,2):
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
    global qtable,DNA_LEN
    lock = l

    q = to_query(dna)
    subset = dataset[dataset.eval(q)]
    total = subset.shape[0]
    if total==0: return
    wr_f1 = subset[subset.eval("(fu_1)>0")].shape[0]/total
    wr_f2 = subset[subset.eval("(fu_2)>0")].shape[0]/total
    wr_f3 = subset[subset.eval("(fu_3)>0")].shape[0]/total
    qtable = qtable.append(pd.Series({
        'dna':dna,
        'wr_f1':wr_f1,
        'wr_f2':wr_f2,
        'wr_f3':wr_f3,
        'samples':total
    }, name=int(dna,2)))

    print("{}\t{}\twr_f1:{:.2f}\twr_f2:{:.2f}\twr_f3:{:.2f}\ttotal:{}".format(int(dna,2),dna,wr_f1,wr_f2,wr_f3,total))


    lock.acquire()
    finished.value+=1
    if len(qtable) % 100 ==0:
        qtable = qtable.sort_values(by=['win_r'],ascending=False)
        qtable.to_csv('data/report_len{}.csv'.format(DNA_LEN))
    # bar.update(finished.value)
    lock.release()


filename = 'data/dataset-labeled-2.csv'
dataset = pd.read_csv(filename,index_col=0)

print(dataset.shape)

DNA_LEN = 16
qtable = pd.DataFrame()
DNAset = gen_bits(DNA_LEN)
bar = progressbar.ProgressBar(max_value=len(DNAset))


m = mp.Manager()
l = m.Lock()
pool = mp.Pool(processes=mp.cpu_count())
pool.map(do_work,DNAset)
pool.close()
pool.join()


qtable = qtable.sort_values(by=['win_r'],ascending=False)
qtable.to_csv('data/report_len{}.csv'.format(DNA_LEN))
print(qtable)
