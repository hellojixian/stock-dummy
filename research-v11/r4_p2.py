#!/usr/bin/env python3
import datetime
import pandas as pd
import numpy as np
import math, sys, os

SECURITY = 'sz000001'
history = pd.read_csv('data/analysis/{}_feature.csv'.format(SECURITY),index_col=0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# subset = history[history.eval("future_opp>future_risk & future_risk<0.05")]
# print(subset[:100])

field = 'c9d'
for q in np.linspace(0,1,21):
    print("Quantitle: {:.0f}".format(q*100))
    limit_low = history[field].quantile(q)
    if q!=1:
        limit_high = history[field].quantile(q+0.05)
    else:
        limit_high = limit_low
    print("{}: {:.2f} to {:.2f}".format(field,limit_low, limit_high))
    subset = history[history.eval("{}>={} & {}<={}".format(field,limit_low,field,limit_high))]
    mean_risk, mean_opp = subset['future_risk'].mean(),subset['future_opp'].mean()
    print("qty: {}\t mean_risk: {:.3f}\t mean_opp: {:.3f}".format(len(subset),mean_risk, mean_opp))
    print("-"*100)

# print(subset['ideal_up'].quantile(0.05))
# print(subset.shape)
