#!/usr/bin/env python3

import pandas as pd
import datetime,time

from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

security='000919.XSHE'
start_date=datetime.date(2014,3,16)
end_date=datetime.date(2015,7,30)

backtest = get_price(security=security, start_date=start_date, end_date=end_date)

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

timestamp = time.time()
features = []
for trade_date in backtest.index:
    feature = extract_features(security,trade_date,get_price)
    features.append(feature)

print(generate_report(features))
print("-"*50)
baseline_profits = calc_baseline_profit(backtest)
time_durtion = time.time() - timestamp
print("Baseline Profit: {:.2f}%".format(baseline_profits))
print("Test Durtion: {:.2f} sec".format(time_durtion))
