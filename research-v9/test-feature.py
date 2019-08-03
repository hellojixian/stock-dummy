#!/usr/bin/env python3

import pandas as pd
import datetime,time
import scipy.stats

from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *
from lib.visualize import *
from lib.strategy import Strategy

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# security='600822.XSHG'
security='600001.XSHG'
start_date=datetime.date(2005,7,30)
end_date=datetime.date(2017,12,30)

backtest = get_price(security=security, start_date=start_date, end_date=end_date)
assert(backtest.shape[0]>0)

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

timestamp = time.time()
features = extract_all_features(security, backtest, get_price)
buy_samples  = features[features.buy==1]
sell_samples = features[features.sell==1]

securities = get_all_securites()

print("Buy : {} samples".format(buy_samples.shape[0]))
print("Sell: {} samples".format(sell_samples.shape[0]))
print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))

# features=features[features.eval("f3d_pos==1")]
cols = ["nobs","minmax","mean","variance","skewness","kurtosis"]

report = pd.DataFrame()
for col in features:
    if col[:1]=='f':
        e = scipy.stats.describe(features[col])
        r = pd.Series(e,name=col)
        report = report.append(r)
report.columns = cols
print(report.sort_values(by=['variance']))
