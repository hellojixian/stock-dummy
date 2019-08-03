#!/usr/bin/env python3

import pandas as pd
import datetime,time

from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *
from lib.visualize import *
from lib.strategy import Strategy

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# security='000919.XSHE'
# start_date=datetime.date(2006,7,30)
# # start_date=datetime.date(2015,5,12)
# end_date=datetime.date(2016,12,30)

# security='600822.XSHG'
security='600001.XSHG'
start_date=datetime.date(2005,7,30)
end_date=datetime.date(2017,12,30)

backtest = get_price(security=security, start_date=start_date, end_date=end_date)
init_fund = 100000
assert(backtest.shape[0]>0)

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

timestamp = time.time()
features = extract_all_features(security, backtest, get_price)
strategy = Strategy(cash=init_fund)

print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))
df = pd.DataFrame(features)
print(df.columns.tolist())
print(df[:10].values)
