#!/usr/bin/env python3

import pandas as pd
import numpy as np
import time, datetime, os, gc, sys

DATABASE_FILE = 'data/raw_dataset_2005-01-01-2016-12-30-3740.csv'
SLICE_CACHE_FILE = 'data/cache/{}-full.cache'

MEM_CACHE_KEY = '{}'
MEM_CACHE = {}

def get_price(security, end_date, count, skip_paused=True):
    mem_cache_key = MEM_CACHE_KEY.format(security)
    if mem_cache_key in MEM_CACHE:
        dataset = MEM_CACHE[mem_cache_key]
    else:
        slice_cache_file = SLICE_CACHE_FILE.format(security)
        if os.path.isfile(slice_cache_file):
            dataset = pd.read_csv(slice_cache_file, index_col=0)
        else:
            dataset = pd.read_csv(DATABASE_FILE, index_col=0, low_memory=False)
            dataset = dataset[dataset.security==security]
            dataset.to_csv(slice_cache_file)
        MEM_CACHE[mem_cache_key] = dataset.copy()

    try:
        end_date = str(end_date)
        idx = dataset.index.get_loc(end_date)+1
        dataset = dataset[idx-count:idx]
    except:
        dataset.index = pd.to_datetime(dataset.index, format="%Y-%m-%d")
        dataset = dataset.sort_index()
        end_date = np.datetime64(end_date)
        dataset = dataset[dataset.index<=end_date]
        dataset = dataset[-count:]
        dataset.index = dataset.index.strftime("%Y-%m-%d")
    return dataset
