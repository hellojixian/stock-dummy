import datetime
import pandas as pd
import math, sys, os
import progressbar

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
    query=""
    for i in range(len(dna)):
        op='<'
        if int(dna[i])==1: op='>'
        query += "(prev_{}{}0) & ".format(i,op)
    query = query[:-2]
    return query

filename = 'data/dataset-labeled.csv'
dataset = pd.read_csv(filename,index_col=0)


DNA_LEN = 8
qtable = pd.DataFrame()
DNAset = gen_bits(DNA_LEN)

for dna in DNAset:
    q = to_query(dna)
    subset = dataset[dataset.eval(q)]
    total = subset.shape[0]
    if total>0:
        cond = "(fu_1) >0 or (fu_1+fu_2)>0 or (fu_1+fu_2+fu_3)>0"
        win_r = subset[subset.eval(cond)].shape[0]/total
        qtable = qtable.append(pd.Series({
        'dna':dna,
        'win_r':win_r,
        'samples':total
        }, name=int(dna,2)))
        print("{}\t{}\twin_r:{:.2f}\tsamples:{}".format(int(dna,2),dna,win_r,total,total))

qtable = qtable.sort_values(by=['win_r'],ascending=False)
qtable.to_csv('data/report_len{}.csv'.format(DNA_LEN))
print(qtable)
