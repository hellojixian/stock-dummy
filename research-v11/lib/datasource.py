#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob

np.random.seed(11)

def fetch_dataset():
    dataset = []
    path = 'data/stock_data/'
    columns = ['date','open','high','low','close','change']
    files = [f for f in glob.glob(path + "*.csv", recursive=False)]
    selected_files = np.random.choice(files, size=1)

    history = pd.read_csv(selected_files[0])
    history = history[columns]
    history = history.sort_values(by=['date'])
    dataset = history[500:1000]
    assert(dataset.shape[0]>0)

    print("File: {} \t ({} recs)".format(selected_files[0], history.shape[0]))
    print("From: {}\nTo: {}".format(dataset['date'].iloc[0],dataset['date'].iloc[-1]))
    return dataset
