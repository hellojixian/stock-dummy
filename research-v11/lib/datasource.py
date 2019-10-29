#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os, glob

np.random.seed(10)

def fetch_dataset(quantity=1):
    dataset = []
    path = 'data/stock_data/'
    columns = ['date','open','high','low','close','change']
    files = [f for f in glob.glob(path + "*.csv", recursive=False)]
    selected_files = np.random.choice(files, size=quantity)

    for data_file in selected_files:
        history = pd.read_csv(data_file)
        history = history[columns]
        history = history.sort_values(by=['date'])
        history = history[500:1000]
        dataset.append(history)
    return dataset
