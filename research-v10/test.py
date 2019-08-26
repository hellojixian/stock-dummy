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



finished = mp.Value('i', 0)
def do_work(dna):
    global finished
    global DNA_LEN,DNAset
    global l

    l.acquire()
    finished.value+=1
    print("{:.2f}% {}".format(finished.value/len(DNAset)*100, finished.value))
    l.release()
    record = 1
    return record

filename = 'data/dataset-labeled-2.csv'


DNA_LEN = 16
DNAset = gen_bits(DNA_LEN)
bar = progressbar.ProgressBar(max_value=len(DNAset))
qtable = pd.DataFrame()

m = mp.Manager()
l = m.Lock()
pool = mp.Pool(processes=mp.cpu_count())
res = pool.map(do_work,DNAset)
pool.close()
pool.join()

print('done')
print(finished.value, len(res))
