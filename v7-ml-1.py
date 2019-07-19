#!/usr/bin/env python3

import json, math
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('Loading dataset ...')
test_df = pd.read_csv('featured-v7-HS300-2017-2018.csv', index_col=0)

# pre_c3_up
# pre_c3_down

days = test_df['date'].value_counts().index.sort_values()

for trade_date in days:  
  df = test_df[test_df.date==trade_date]
  df = df[df.fu_c1>3].sort_values(by=['fu_c1'],ascending=False)
  print(df)
  break