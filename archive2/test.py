#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will visualize the win/lose data distributions
"""
import pandas as pd
import numpy as np
import warnings,sys,os
import json, pprint
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

df = pd.read_csv("train_subset.csv", index_col=0)
df = df.sort_values(by=['weight'], ascending=False)
df['weight'] = np.round(df['weight'],2)
factors = df.columns.drop(['security','date','fu_c2', 'fu_c3', 'fu_c4']).values

df = df[factors]
print(df.iloc[[0,4]])
sys.exit()



total = df.shape[0]
df_full = df
win_r = df[df.fu_c1>=0].shape[0] / df.shape[0]
print('full_wr',win_r)
df = df[:100]
win_r = df[df.fu_c1>=0].shape[0] / df.shape[0]
print(df.shape[0], total)
print(win_r)
# print(df_full)
