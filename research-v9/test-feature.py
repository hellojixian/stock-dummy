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
start_date=datetime.date(2008,7,30)
end_date=datetime.date(2009,12,30)

backtest = get_price(security=security, start_date=start_date, end_date=end_date)
init_fund = 100000
assert(backtest.shape[0]>0)

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

timestamp = time.time()
features = []
strategy = Strategy(cash=init_fund)
for trade_date in backtest.index:
    feature = extract_features(security,trade_date,get_price)
    # action = strategy.handle_data(feature)
    features.append(feature)

print(pd.DataFrame(features))
