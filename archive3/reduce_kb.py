import numpy as np
import pandas as pd
import sys,os,datetime

# file = 'data/test_set.csv'
file = 'data/knowledge_base.csv'

df = pd.read_csv(file,index_col=0)
# for col in df.columns:
#     print(col)

df = df.reset_index()
cols = [
'index',
'security',
'risk_60',
'risk_30',
'amp_10',
'amp_120',
'prev4_down_line',
'prev4_up_line',
'prev4_open_c',
'prev4_bar',
'prev3_down_line',
'prev3_up_line',
'prev3_open_c',
'prev4_bar',
'prev2_down_line',
'prev2_up_line',
'prev2_open_c',
'prev2_bar',
'prev1_down_line',
'prev1_up_line',
]

df = df.drop(columns=cols)
int_cols = df.columns[:-2]
float_cols = ['future_profit','future_risk']
df_float = df[float_cols].copy()
df = df.astype('i')
df[float_cols] = df_float

df.to_csv(file+"_min")
print('Done')
