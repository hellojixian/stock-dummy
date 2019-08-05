#!/usr/bin/env python3

import pandas as pd
import datetime,time

import scipy.stats
from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *
from lib.visualize import *
from lib.strategy import Strategy
from lib.kb import KnowledgeBase

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# security='600822.XSHG'
security='600001.XSHG'
start_date=datetime.date(2005,7,30)
end_date=datetime.date(2017,12,30)

# train_df = get_train_set(300, start_date, end_date)
backtest = get_price(security=security, start_date=start_date, end_date=end_date)
train_df = extract_all_features(security, backtest, get_price)

print(train_df.shape)

# print(train_df['f60d_down'].quantile(0.9),train_df['f60d_down'].max())
# print(train_df['f30d_down'].quantile(0.9),train_df['f30d_down'].max())
# print(train_df['f10d_down'].quantile(0.9),train_df['f10d_down'].max())
# print(train_df['f5d_down'].quantile(0.9),train_df['f5d_down'].max())
# print(train_df['f3d_down'].quantile(0.8),train_df['f3d_down'].max())

measure = 'buy'
report = {}
for f in train_df.columns:
    if f[:1]!='f': continue
    cor = np.corrcoef(train_df[f],train_df[measure])[0][1]
    cov = np.cov(train_df[f],train_df[measure])[0][1]
    var = scipy.stats.variation(train_df[f])
    report[f]={
        'cor':cor,
        'cov':cov,
        'var':var,
    }
report = pd.DataFrame(report)
report = report.T
report['cor'] = report['cor']
report['cov'] = report['cov']
print(report.sort_values(by=["cor"],ascending=True))
