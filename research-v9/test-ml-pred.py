#!/usr/bin/env python3

import pandas as pd
import datetime,time

from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *
from lib.visualize import *
from lib.strategy import Strategy
from lib.ml import *

from keras import optimizers
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Input, Dropout
from keras.callbacks import ModelCheckpoint

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

security='300201.XSHE'
start_date=datetime.date(2012,5,12)
end_date=datetime.date(2014,12,30)


backtest = get_price(security=security, start_date=start_date, end_date=end_date)
init_fund = 100000

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

timestamp = time.time()
features = []
action = ""

features = extract_all_features(security, backtest, get_price)
strategy = Strategy(cash=init_fund, kb={})
features['action'] = ""
for i,feature in features.iterrows():
    action = strategy.handle_data(feature)
    features.loc[i,'action'] = action

transformed = transform_data_buy(features)
model_buy = get_model(transformed.shape[1])
pred = np.round(model_buy.predict(transformed),2)
features['buy_pred'] = pred[:,0]


print(pred[:,0])
print("buy_pred: ",features[features.buy_pred>0.4].shape[0])

print("-"*50)
baseline_profits = calc_baseline_profit(backtest)
strategy_profits = strategy.get_profit(backtest['close'].iloc[-1])
print("Baseline Profit: {:.2f}%".format(baseline_profits))
print("Strategy Profit: {:.2g}%".format(strategy_profits))
print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))
visualize_report(generate_report(features),backtest,strategy)
