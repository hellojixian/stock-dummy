#!/usr/bin/env python3

from lib.jqdata import *
from lib.feature_extract import *

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

security='000919.XSHE'
# end_date=datetime.date(2015,7,30)
end_date=datetime.date(2015,3,16)
test_days = 100
dates = get_price(security, end_date, count=test_days).index
assert(len(dates)==test_days)
assert(end_date == dates[-1])

n_steps = 7

df = pd.DataFrame()
for trade_date in dates:
    close = get_price(security, end_date=trade_date, count=1)['close'][0]
    days_scopes=[3,5,10,20,30,60,120]

    feature = pd.Series({'close':close},name=trade_date)
    for days in days_scopes:
        history = get_price(security=security, end_date=trade_date, count=days)
        history = history.iloc[:-1]
        min, max = history['low'].min(), history['high'].max()
        pos = to_categorial((close-min) / (max-min), n_steps)
        f_key = 'pos_{}'.format(days)
        feature[f_key]= pos

        sign=" "
        if df.shape[0]>0:
            if pos > df[f_key].iloc[-1]: sign="+"
            if pos < df[f_key].iloc[-1]: sign="-"
        feature["_"+f_key]= "{} {}".format(pos, sign)
    df = df.append(feature)

cols = []
for days in days_scopes:
    cols.extend(['_pos_{}'.format(days)])

cols.extend(['close'])
df=df[cols]
print(df)
