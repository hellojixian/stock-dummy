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
end_date=datetime.date(2016,12,30)

backtest = get_price(security=security, start_date=start_date, end_date=end_date)
init_fund = 100000

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

timestamp = time.time()
features = []
action = ""
strategy = Strategy(cash=init_fund)
for trade_date in backtest.index:
    feature = extract_features(security,trade_date,get_price)
    # action = strategy.handle_data(feature)
    feature['action'] = action
    features.append(feature)


print("-"*50)
baseline_profits = calc_baseline_profit(backtest)
strategy_profits = strategy.get_profit(backtest['close'].iloc[-1])
print("Baseline Profit: {:.2f}%".format(baseline_profits))
print("Strategy Profit: {:.2f}%".format(strategy_profits))
print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))
visualize_report(generate_report(features),backtest,strategy)
