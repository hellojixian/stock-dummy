#!/usr/bin/env python3

import pandas as pd
import datetime,time

import scipy.stats
import seaborn as sns
import matplotlib.pylab as plt

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

security='600822.XSHG'
# security='600001.XSHG'
start_date=datetime.date(2004,7,30)
end_date=datetime.date(2010,12,30)

train_df = get_train_set(300, start_date, end_date)
backtest = get_price(security=security, start_date=start_date, end_date=end_date)
train_df = extract_all_features(security, backtest, get_price)

print(train_df.shape)

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
report = report.sort_values(by=["cor"],ascending=True)
print(report)
print('-'*100)
cols = report.index.tolist()
cols.append(measure)
train_df = train_df[cols]

# ax = sns.heatmap(train_df.corr(),cmap="RdYlGn_r", linewidth=0.5, vmin=-0.5,vmax=1)
# plt.show()
