#!/usr/bin/env python3
#
import pandas as pd
import time, datetime, os
from jqdata import *

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

securities = get_index_stocks('000300.XSHG')
start_date = datetime.date(2006,1,1)
end_date = datetime.date(2006,1,10)

res = pd.DataFrame()
days = get_trade_days(start_date, end_date)

def rolling_wr(val):
    return (len(np.where(val>0)[0]) - len(np.where(val<0)[0])) / len(val)


h_dataset = pd.DataFrame()
h_data_filename = 'test-featured-v7.1-HS300-2006-2016.csv'
if os.path.exists(h_data_filename):
    print('Loading dataset')
    h_dataset = pd.read_csv(h_data_filename,index_col=0)
    print(h_dataset.shape)

print('Days:' ,len(days))
start_timestamp = time.time()
for trade_date in days:
    panel =  get_price(securities, end_date=trade_date, count=100, skip_paused=False)        
    panel['pre_c3'] = round((panel['close'].shift(periods=3) - panel['close'].shift(periods=4)) / panel['close'].shift(periods=4)*100,2)
    panel['pre_c2'] = round((panel['close'].shift(periods=2) - panel['close'].shift(periods=3)) / panel['close'].shift(periods=3)*100,2)
    panel['pre_c1'] = round((panel['close'].shift(periods=1) - panel['close'].shift(periods=2)) / panel['close'].shift(periods=2)*100,2)
    panel['today_c'] = round((panel['close'] - panel['close'].shift(periods=1)) / panel['close'].shift(periods=1)*100,2)

    panel['up_l'] = round((panel['close'] - panel['high']) / panel['close']*100,2)
    panel['dn_l'] = round((panel['close'] - panel['low']) / panel['close']*100,2)
    panel['open_c'] = round((panel['open'] - panel['close'].shift(periods=1)) / panel['close'].shift(periods=1)*100,2)    
    
    panel['ma5'] = round(panel['close'].rolling(window=5).mean(),2)
    panel['ma10'] = round(panel['close'].rolling(window=10).mean(),2)
    panel['ma60'] = round(panel['close'].rolling(window=60).mean(),2)
    
    panel['ma5_pos']  = round((panel['close'] - panel['ma5'])/panel['close']*100,2)
    panel['ma10_pos'] = round((panel['close'] - panel['ma10'])/panel['close']*100,2)    
    panel['ma60_pos'] = round((panel['close'] - panel['ma60'])/panel['close']*100,2)    

    
    ma5_c = (panel['ma5'] - panel['ma5'].shift(periods=5)) / panel['ma5'].shift(periods=5)
    panel['ma5_ang']  = round(np.arcsin(ma5_c/np.hypot(0.6, ma5_c/100))*180/math.pi*3,1)

    ma10_c = (panel['ma10'] - panel['ma10'].shift(periods=5)) / panel['ma10'].shift(periods=5)
    panel['ma10_ang']  = round(np.arcsin(ma10_c/np.hypot(0.6, ma10_c/100))*180/math.pi*3,1)

    ma60_c = (panel['ma60'] - panel['ma60'].shift(periods=5)) / panel['ma60'].shift(periods=5)
    panel['ma60_ang']  = round(np.arcsin(ma60_c/np.hypot(0.6, ma60_c/100))*180/math.pi*3,1)              


    panel['p5_wr'] = round(panel['today_c'].rolling(window=5).sum(),2)
    panel['p10_wr'] = round(panel['today_c'].rolling(window=10).sum(),2)    
    
    panel['prewr1'] = round(len(panel.major_xs(panel.major_axis[-2])[panel[:,panel.major_axis[-2]].today_c>=0])/\
                         len(panel.major_xs(panel.major_axis[-2]).dropna(axis=0)),2)    
    panel['win_r'] = round(len(panel.major_xs(panel.major_axis[-1])[panel[:,panel.major_axis[-1]].today_c>=0])/\
                         len(panel.major_xs(panel.major_axis[-1]).dropna(axis=0)),2)

    h100_high = panel['high'].rolling(window=100).max()
    h100_low = panel['low'].rolling(window=100).min()
    panel['h100_pos'] = round((panel['close'] - h100_low) / (h100_high - h100_low),2)    
    
    h10_high = panel['high'].rolling(window=10).max()
    h10_low = panel['low'].rolling(window=10).min()
    panel['h10_pos'] = round((panel['close'] - h10_low) / (h10_high - h10_low),2)
    
    panel = panel.drop(['open','close','high','low','ma5','ma10','ma60','volume','money'])
    
    res = panel.major_xs(panel.major_axis[-1]).dropna(axis=0)
        
    # attach future result for inspection
    idx = list(days).index(trade_date)
    future_len = 4
    if idx+future_len >= len(days): break        
    future_date = days[idx+future_len]
    future_panel = get_price(securities, end_date=future_date, count=future_len+1, skip_paused=False)        
    future_panel['fu_c1'] = round((future_panel['close'].shift(periods=-1) - future_panel['close']) / future_panel['close']*100,2)
    future_panel['fu_c2'] = round((future_panel['close'].shift(periods=-2) - future_panel['close']) / future_panel['close']*100,2)
    future_panel['fu_c3'] = round((future_panel['close'].shift(periods=-3) - future_panel['close']) / future_panel['close']*100,2)
    future_panel['fu_c4'] = round((future_panel['close'].shift(periods=-4) - future_panel['close']) / future_panel['close']*100,2)    
    
    future_res = future_panel.major_xs(future_panel.major_axis[0]).dropna(axis=0)
    future_res = future_res[['fu_c1','fu_c2','fu_c3','fu_c4']]        

    res = res.join(future_res)

    res['date'] = trade_date
    cols = res.columns.tolist()
    ncols = np.insert(cols[:-1],0, values=[cols[-1]])
    res = res.reindex(columns=ncols)

    res['security'] = res.index    
    cols = res.columns.tolist()
    ncols = np.insert(cols[:-1],0, values=[cols[-1]])
    res = res.reindex(columns=ncols)
        
    res['date'] = res['date'].astype(str)
    res['id'] = res['security']+"_"+res['date'].str.replace("-",'')
    res =res.set_index(keys='id')
    
    remain_sec=int((time.time() - start_timestamp) / ((idx+1)/len(days)) * (1-((idx+1)/len(days))))
    print('\r',trade_date, len(h_dataset),'records\tprogress: ',str(round((idx+1)/len(days)*100,2))+'%\t est: '+str(datetime.timedelta(seconds=remain_sec)),'\tsince start:',int((time.time() - start_timestamp))," "*50, end='')

    
    h_dataset = h_dataset.append(res)
    if idx % 200 == 0 and idx>9:
        h_dataset.to_csv(h_data_filename)
        print('\r\nsave progress.\n')

print("\n\n")        
h_dataset.to_csv(h_data_filename)
print('\ndone')