import datetime
import pandas as pd
import math, sys, os
import progressbar

from lib.jqdata import *


start_date=datetime.date(2008,4,15)
end_date=datetime.date(2019,7,15)
np.random.seed(0)

# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('start testing')

filename = 'data/dataset-labeled.csv'

dataset = pd.DataFrame()
security_list = get_all_securites()
for _,row in progressbar.progressbar(security_list.iterrows(),max_value=security_list.shape[0]):
    security = row['security']
    history = get_price(security, start_date=start_date, end_date=end_date,
                            skip_paused=True)

    for i in range(0,10):
        history['prev_{}'.format(i)] = (history['close'].shift(periods=i) - history['close'].shift(periods=i+1) )/history['close'].shift(periods=i+1)*100
        history['prev_{}'.format(i)] = np.round(history['prev_{}'.format(i)],2)

    for i in range(0,5):
        history['fu_{}'.format(i+1)] = (history['close'].shift(periods=-i-1) - history['close'].shift(periods=0) )/history['close'].shift(periods=0)*100
        history['fu_{}'.format(i+1)] = np.round(history['fu_{}'.format(i+1)],2)

    history.drop(columns=['high','low','volume','money'])
    history=history.dropna()
    dataset = dataset.append(history)

dataset.to_csv(filename)
print('done')
