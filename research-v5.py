import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

df = pd.read_csv('f-01.csv',index_col=0)
df.drop(columns=['volume','money','security','median','hash_close','action'],inplace=True)

# adding features
df['prev_c1'] = round((df['close'] - df['close'].shift(periods=1)) / df['close'].shift(periods=1),3)
df['prev_c2'] = round((df['close'].shift(periods=1) - df['close'].shift(periods=2)) / df['close'].shift(periods=2),3)

# 策略组1 - 5日线上买绿柱 胜率 70% 持仓3天
# df = df[df.ma5_pos>0]
# df = df[df.today_c<0.009]
# df = df[df.ma60_pos>-0.05]
# df = df[df.ma60_pos<0.11]
# df = df[df.ma10_ang<0.25]
# df = df[df.prev_c1>0.006]


# 策略组2 - 5日线下买三连绿 持仓1天
# df = df[df.ma5_pos<0.00]
# df = df[df.today_c<0]
# df = df[df.prev_c1<0]
# df = df[df.prev_c2<0]
# df = df[df.ma60_pos<0.08]


# print(df.columns)

basefund = 1
error = 0
for i in range(len(df)-1):
    change = df['future_c1'].iloc[i]
    if change<-0.01: error+=1
    basefund *= (1+change)

print("-"*100)
print('basefund:',basefund)
print('total:',len(df))
print('errors:',error)
print('errors rate:', round(error/len(df)*100,2))
print("-"*100)

res = df[['future_c1','future_c2','ma5_pos','prev_c1','today_c','ma5_ma10','ma60_pos','p100_pos', 'ma10_ang','mode_pos']][:50]
res = res.sort_values(by=['future_c1'],ascending=False)
print(res[:50])
