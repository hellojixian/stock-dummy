#!/usr/bin/env python3

import datetime
import math, sys, os
import progressbar
import multiprocessing as mp
import numpy as np
import pandas as pd
import argparse

from lib.jqdata import *
from lib.dna import *


# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


parser = argparse.ArgumentParser(description='extract qtable regarding the DNA.')
parser.add_argument('-v','--ver', dest='dna_version', nargs=1, type=str,
                    default='v1',help='specify the DNA version number, (default: v1)')

args = parser.parse_args()
DNA_VERSION = vars(args)['dna_version'][0]


finished = mp.Value('i', 0)
def do_work(dna):
    global finished
    global DNA_LEN,DNAset,DNA_VERSION
    global l

    func = "to_query_{}('{}')".format(DNA_VERSION, dna)
    q = eval(func)
    subset = dataset[dataset.eval(q)]
    total = subset.shape[0]
    if total==0: return None
    wr_f1 = subset[subset.eval("(fu_1)>0")].shape[0]/total
    wr_f2 = subset[subset.eval("(fu_2)>0")].shape[0]/total
    wr_f3 = subset[subset.eval("(fu_3)>0")].shape[0]/total
    wr_f4 = subset[subset.eval("(fu_4)>0")].shape[0]/total
    wr_f5 = subset[subset.eval("(fu_5)>0")].shape[0]/total
    record = pd.Series({
        'ver':DNA_VERSION,
        'dna':dna,
        'wr_f1':wr_f1,
        'wr_f2':wr_f2,
        'wr_f3':wr_f3,
        'wr_f4':wr_f4,
        'wr_f5':wr_f5,
        'samples':total
    }, name=int(dna,2))

    l.acquire()
    print("{:.2f}%\t{}\twr_f1:{:.2f}\twr_f2:{:.2f}\twr_f3:{:.2f}\ttotal:{}".format(finished.value/len(DNAset)*100,dna,wr_f1,wr_f2,wr_f3,total))
    finished.value+=1
    l.release()
    return record

filename = 'data/dataset-labeled-2.csv'
dataset = pd.read_csv(filename,index_col=0)

print(dataset.shape)

DNA_LEN = 16
DNAset = gen_DNAset(DNA_LEN)
bar = progressbar.ProgressBar(max_value=len(DNAset))
qtable = pd.DataFrame()

m = mp.Manager()
l = m.Lock()
pool = mp.Pool(processes=mp.cpu_count())
res = pool.imap(do_work,DNAset)
pool.close()
pool.join()


for r in res:
    if r is not None: qtable = qtable.append(r)
qtable = qtable.sort_values(by=['wr_f1'],ascending=False)
qtable.to_csv('data/dna_{}_qtable.csv'.format(DNA_VERSION))
print(qtable)
