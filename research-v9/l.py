#!/usr/bin/env python3

import pandas as pd
import datetime,time

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


train_df = get_train_set(300, start_date, end_date)

print(train_df.shape)

report = {}
for f in train_df.columns:
    if f[:1]!='f': continue
    res = np.corrcoef(train_df[f],train_df['buy'])
    report[f]={'cor':res[0][1]}
report = pd.DataFrame(report)
report = report.T
report['cor'] = np.abs(report['cor'])
print(report.sort_values(by=["cor"],ascending=False))
