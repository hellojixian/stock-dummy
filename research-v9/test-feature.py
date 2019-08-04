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

TRAIN_SAMPLE_SET=300
securities = get_all_securites()['security']
securities = securities.sample(TRAIN_SAMPLE_SET)

train_cache = 'data/cache/train_set.cache'
if os.path.isfile(train_cache):
    train_df = pd.read_csv(train_cache)
else:
    train_df = pd.DataFrame()
    for i in range(len(securities.values)):
        security = securities.values[i]
        print("Generating val set {}/{}: {}".format(i+1,TRAIN_SAMPLE_SET,security))
        backtest = get_price(security=security, start_date=start_date, end_date=end_date)
        df = extract_all_features(security, backtest, get_price)
        train_cache_tmp = train_cache+"_"+security
        output_header=False
        if i==0: output_header=True
        df.to_csv(train_cache_tmp, index=False, header=output_header)

        os.system("cat {} >> {}".format(train_cache_tmp,train_cache))
        os.remove(train_cache_tmp)
print(val_df.shape)

timestamp = time.time()
features = extract_all_features(security, backtest, get_price)
buy_samples  = features[features.buy==1]
sell_samples = features[features.sell==1]

print("Buy : {} samples".format(buy_samples.shape[0]))
print("Sell: {} samples".format(sell_samples.shape[0]))
print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))

# features=features[features.eval("f3d_pos==1")]
cols = ["nobs","minmax","mean","variance","skewness","kurtosis"]

dataset = val_df
timestamp = time.time()
wr_cond = "(buy==1|hold==0)& sell==0"
for _, sample in buy_samples.iterrows():
    if _ <=2: continue
    print(sample)
    report = pd.DataFrame()
    fixed_params = ['f3d_pos']
    filter=""
    for f in fixed_params:
        if f[:1]=='f':
            filter += "({}=={})&".format(f,sample[f])
    filter=filter[:-1]
    fixed_filter = filter
    subset = dataset[dataset.eval(filter)]
    for col in features.columns:
        if col[:1]=='f':
            e = scipy.stats.describe(dataset[col])
            r = pd.Series(e,name=col)
            report = report.append(r)
    report.columns = cols
    report = report.sort_values(by=['variance'])
    wr = 0
    if subset.shape[0]>0:
        wr = subset[subset.eval(wr_cond)].shape[0]/subset.shape[0]*100
    print("Acc: {:.2f}% of {} Samples".format(wr, subset.shape[0]))


    for i in range(report.shape[0]-1):
        filter = fixed_filter+" &"
        for f in report.index[:i]:
            if f[:1]=='f':
                filter += " ({}>={}) & ({}<={}) &".format(f,sample[f]-1,f, sample[f]+1)
        filter=filter[:-1]
        if len(filter)==0: continue
        subset = dataset[dataset.eval(filter)]
        wr = 0
        if subset.shape[0]>0:
            wr = subset[subset.eval(wr_cond)].shape[0]/subset.shape[0]*100
        print("{} Acc: {:.2f}% of {} Samples".format(i,wr, subset.shape[0]))

    break

print("Test Durtion: {:.2f} sec".format(time.time() - timestamp))
