#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys,os,datetime,time
import gc
from lib.prediction import *

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('Loading knowledge base ...\t',end="")
kb = pd.read_csv("data/knowledge_base_1800.csv")
print('{} records'.format(kb.shape[0]))

print('Loading test set .........\t',end="")
test_set = pd.read_csv("data/test_set-min.csv")
print('{} records'.format(test_set.shape[0]))



kb = optimize_df(kb)
test_set = optimize_df(test_set)
gc.collect()


for _ in range(60):
    future = ['future_profit','future_risk']
    sample = test_set.sample(1).iloc[0]
    pred = predict(sample)
    if pred['result']==False:
        print("No enough samples - Skip")
        print("samples: {:d}=>{:d} \tdurtion: {:d}s ".format(
            int(pred['samples_count']),int(pred['reduced_count']),int(pred['durtion'])))
    else:
        measure = {"future_profit":{},"future_risk":{}}
        for f in future:
            measure[f]["actual"] = sample[f]
            measure[f]["predict_med"] = pred[f+"_med"]
        measure = pd.DataFrame(measure)
        measure = measure.T
        cols = ['actual','predict_med','predict_mean']
        print(measure[cols])

        print("samples: {:d}=>{:d} \tdurtion: {:2.2f}s \t loss: {:.2f}".format(
            int(pred['samples_count']),int(pred['reduced_count']),pred['durtion'],pred['similarity_loss']))

    print("-"*100)
