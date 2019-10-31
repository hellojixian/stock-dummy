#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob

def fetch_dataset(fileId):
    dataset = []
    path = 'data/stock_data/'
    columns = ['date','open','high','low','close','change']
    files = [f for f in glob.glob(path + "*.csv", recursive=False)]
    # selected_files = np.random.choice(files, size=1)
    # history = pd.read_csv(selected_files[0])

    history = pd.read_csv(files[fileId])
    history = history[columns]
    history = history.sort_values(by=['date'])
    dataset = history[500:1000]
    assert(dataset.shape[0]>0)

    print("File: {} \t ({} recs)".format(files[fileId], history.shape[0]))
    print("From: {}\nTo: {}".format(dataset['date'].iloc[0],dataset['date'].iloc[-1]))
    return dataset
