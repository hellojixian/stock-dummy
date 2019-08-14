#!/usr/bin/env python3

import pandas as pd
import numpy as np
import time, datetime, os, gc, sys

DATABASE_FILE = 'data/raw_dataset_2005-01-01-2016-12-30-3740.csv'
SLICE_CACHE_FILE = 'data/cache/{:.6}-full.cache'

MEM_CACHE_KEY = '{:.6}'
MEM_CACHE = {}
DB_CACHE = None

def get_price(security, end_date, start_date=None, count=10, skip_paused=True):
    global DB_CACHE
    mem_cache_key = MEM_CACHE_KEY.format(security)
    if mem_cache_key in MEM_CACHE:
        dataset = MEM_CACHE[mem_cache_key]
    else:
        slice_cache_file = SLICE_CACHE_FILE.format(security)
        if os.path.isfile(slice_cache_file):
            dataset = pd.read_csv(slice_cache_file, index_col=0)
        else:
            if DB_CACHE is not None:
                dataset = DB_CACHE
            else:
                dataset = pd.read_csv(DATABASE_FILE, index_col=0, low_memory=False)
                DB_CACHE = dataset
            dataset = dataset[dataset.security==security]
            dataset.to_csv(slice_cache_file)
        MEM_CACHE[mem_cache_key] = dataset.copy()

    start_iloc = None
    if start_date is not None:
        try:
            start_date = str(start_date)
            start_iloc = dataset.index.get_loc(start_date)
        except:
            dataset.index = pd.to_datetime(dataset.index, format="%Y-%m-%d")
            dataset = dataset.sort_index()
            end_date = np.datetime64(end_date)
            dataset = dataset[dataset.index>=start_date]
            dataset.index = dataset.index.strftime("%Y-%m-%d")


    try:
        end_date = str(end_date)
        end_iloc = dataset.index.get_loc(end_date)+1
        if start_iloc is not None:
            dataset = dataset[start_iloc:end_iloc]
        else:
            if start_date is not None:
                dataset = dataset[:end_iloc]
            else:
                dataset = dataset[end_iloc-count:end_iloc]
    except:
        dataset.index = pd.to_datetime(dataset.index, format="%Y-%m-%d")
        dataset = dataset.sort_index()
        end_date = np.datetime64(end_date)
        dataset = dataset[dataset.index<=end_date]
        if start_date is not None:
            dataset = dataset[dataset.index>=start_date]
        if start_date is None:
            dataset = dataset[-count:]
        dataset.index = dataset.index.strftime("%Y-%m-%d")
    dataset = dataset.dropna()
    return dataset

def get_all_securites():
    cache_file = "data/cache/security_list.csv"
    if os.path.isfile(cache_file):
        securities = pd.read_csv(cache_file)
    else:
        dataset = pd.read_csv(DATABASE_FILE, index_col=0, low_memory=False)
        securities = dataset['security'].value_counts().index.tolist()
        securities = pd.DataFrame(securities, columns=["security"])
        securities.to_csv(cache_file, index=False)
    return securities
