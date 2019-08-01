#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_report(dataset):
    cols = ['short','median','long','close']
    cols.extend(['date'])
    df = pd.DataFrame(dataset, columns=cols)
    df = df.set_index(keys=['date'])
    return df

def calc_baseline_profit(baseline):
    return np.round((baseline['close'].iloc[0] - baseline['close'].iloc[-1])
                    / baseline['close'].iloc[0] * 100,2)
