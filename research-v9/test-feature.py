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

backtest = get_price(security=security, start_date=start_date, end_date=end_date)
assert(backtest.shape[0]>0)

print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(len(backtest),str(backtest.index[0]),str(backtest.index[-1])))

train_df = get_train_set(300, start_date, end_date)
kb = KnowledgeBase(train_df=train_df)
print(train_df.shape)

timestamp = time.time()
features = extract_all_features(security, backtest, get_price)
buy_samples  = features[features.buy==1]
sell_samples = features[features.sell==1]

print("Buy : {} samples".format(buy_samples.shape[0]))
print("Sell: {} samples".format(sell_samples.shape[0]))
print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))

# features=features[features.eval("f3d_pos==1")]
cols = ["nobs","minmax","mean","variance","skewness","kurtosis"]


# sys.setrecursionlimit(50000)
timestamp = time.time()

i=0
for _, sample in buy_samples.iterrows():
    i+=1
    if i<=3: continue
    if kb.need_learn(sample,'buy'):
        kb.learn(sample,'buy')

    print("\r progress: {:.2f}%  {}/{}".format(i/len(buy_samples)*100,i,len(buy_samples)), end="")
print("\r")

# i=0
# for _, sample in sell_samples.iterrows():
#     i+=1
#     if kb.need_learn(sample,'sell'):
#         kb.learn(sample,'sell')
#     print("\r progress: {:.2f}%  {}/{}".format(i/len(sell_samples)*100,i,len(sell_samples)), end="")
# print("\r")

print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))
