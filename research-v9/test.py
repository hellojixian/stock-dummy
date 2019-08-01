#!/usr/bin/env python3

from lib.jqdata import *
from lib.feature_extract import *

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

security='000919.XSHE'
# end_date=datetime.date(2015,7,30)
end_date=datetime.date(2015,3,14)
test_days = 100
dates = get_price(security, end_date, count=test_days).index
assert(len(dates)==test_days)
print("Back test: {} Days\nSince: {}\nUntil: {}"
    .format(test_days,str(dates[0]),str(dates[-1])))


cols = ['short','median','long','close']
features = []

for trade_date in dates:
    feature = extract_features(security,trade_date,get_price)
    features.append(feature)

cols.extend(['date'])
df = pd.DataFrame(features, columns=cols)
df = df.set_index(keys=['date'])
print(df)
