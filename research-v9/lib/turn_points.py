from rdp import rdp
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import math, sys, os

def _find_turn_points(points, epsilon):
    simplified = rdp(points, epsilon=epsilon)
    directions = np.diff(simplified[:,1])
    idx_keep = [points[0]]
    for i in range(directions.shape[0]-1):
        if (directions[i]>=0 and directions[i+1]<0)\
            or (directions[i]<=0 and directions[i+1]>0):
            idx_keep.append(simplified[i+1])
    idx_keep.append(points[-1])
    idx_keep = np.array(idx_keep)
    return idx_keep

def find_turn_points(history):
    points = history[['num_date','close']].values
    short_his = history[-5:].copy()
    short_his['amp'] = short_his['high'] - short_his['low']
    ma_amp = short_his['amp'].mean()
    epsilon = ma_amp*1.5

    turn_points = _find_turn_points(points, epsilon=epsilon)
    turn_points = pd.DataFrame(turn_points,columns=['num_date','price'])
    turn_points['direction'] = 'unknown'
    for i in range(0,turn_points.shape[0]-1):
        if turn_points['price'].iloc[i] < turn_points['price'].iloc[i+1]:
            turn_points.loc[i,'direction'] = 'up'
        else:
            turn_points.loc[i,'direction'] = 'down'
    return turn_points

def should_buy(dataset):
    len = 120
    subset = dataset[-len:]
    points = find_turn_points(subset)

    decision = False
    fuzzy_range = 0.03
    fuzzy_range_low = 0.015
    price = subset['close'].iloc[-1]
    low = subset['low'].iloc[-1]
    open = subset['open'].iloc[-1]
    buy_signal_count = 0
    v_pos = (price - subset['close'].min()) / (subset['close'].max() - subset['close'].min())

    bottom_points = points[(points.direction=='up')]
    top_points = points[(points.direction=='down')]

    # not enough data
    if points.shape[0]<10: return False

    if points['direction'].iloc[-2]=='down':
        last_down = (points['price'].iloc[-2] - points['price'].iloc[-1]) / points['price'].iloc[-2]
        last_up = (points['price'].iloc[-2] - points['price'].iloc[-3]) / points['price'].iloc[-2]
        prev_down = (points['price'].iloc[-4] - points['price'].iloc[-3]) / points['price'].iloc[-4]

        # 下降破断
        pos = 1
        if (last_down>0.06) \
            or prev_down>0.25: #最后一次的下跌空间要够

            if last_up<0.15 and last_down>0.2 and v_pos>0.2 and v_pos<0.4:
                fuzzy_range=0.05
                decision = True
                if os.environ['DEBUG']=='ON':print('got it 2')

            if v_pos>0.45 or v_pos<0.2:
                fuzzy_range=0.05
                if last_up>0.2 and last_down>0.1:
                    fuzzy_range=0.05
                    decision = True
                    if os.environ['DEBUG']=='ON':print('got it')
            else:
                #下跌幅度不够，往下看支撑位
                if (last_down<0.1 and prev_down<0.25):
                    fuzzy_range=0.01

            support_points = points[(points.direction=='up') & (points.price>price*(1-fuzzy_range))]
            while(pos<support_points.shape[0]):
                point = support_points['price'].iloc[-pos]
                num_date =  support_points['num_date'].iloc[-pos]
                date = mdates.num2date(num_date)
                if os.environ['DEBUG']=='ON':
                    print("{:.10}\t p:{:.2f}\t scope: {:.2f} - {:.2f}\t last_down:{:.2f}/{:.2f}".format(str(date), price,
                        point*(1-fuzzy_range_low), point*(1+fuzzy_range),last_down,prev_down ))
                if (point*(1+fuzzy_range) > price and point*(1-fuzzy_range_low) < price) \
                    or (point*(1+fuzzy_range) > low and point*(1-fuzzy_range_low) < low):
                    buy_signal_count +=1
                    break
                pos += 1
            if buy_signal_count>0:
                if subset['low'][-5:].min() == low: decision = True

        # 说明下爹无力
        if (last_down<0.01 and v_pos<0.2): decision = True
        if (last_down>0.25 and v_pos<0.1): decision = True



        if os.environ['DEBUG']=='ON':
            print('{:.10}\t buy: {} \tsignal: {} \tdown: {:.3f}/{:.3f} \tup:{:.3f}\t v_pos:{:.2f}\t d:{}'\
                .format(str(subset.iloc[-1].name), decision,buy_signal_count,last_down,prev_down,last_up,v_pos,points['direction'].iloc[-2]))

    if points['direction'].iloc[-2]=='up':
        last_down = (points['price'].iloc[-3] - points['price'].iloc[-2]) / points['price'].iloc[-3]
        last_up = (points['price'].iloc[-1] - points['price'].iloc[-2]) / points['price'].iloc[-2]
        # prev_down = (points['price'].iloc[-5] - points['price'].iloc[-4]) / points['price'].iloc[-5]


        if (bottom_points['price'].iloc[-2] < bottom_points['price'].iloc[-1] ) \
            and v_pos < 0.4 and last_up<0.03:
            decision = True
        if os.environ['DEBUG']=='ON':
            print('{:.10}\t buy: {} \tsignal: {} \tdown: {:.3f}/(n/a) \tup:{:.3f}\t v_pos:{:.2f}\t d:{}'\
                .format(str(subset.iloc[-1].name), decision,buy_signal_count,last_down,last_up,v_pos,points['direction'].iloc[-2]))

    max_drop = (dataset['high'][-240:].max() - low )/dataset['high'][-240:].max()
    if max_drop > 0.58 and price>open:
        if os.environ['DEBUG']=='ON':
            print("240 max_drop:",max_drop)
        decision = True
    max_drop = (dataset['high'][-60:].max() - low )/dataset['high'][-60:].max()
    if max_drop > 0.48  and price>open:
        if os.environ['DEBUG']=='ON':
            print("60 max_drop:",max_drop)
        decision = True

    # 判断是否应该忽略这次购买信号
    # 比如箱体横盘太久了
    if decision == True:
        if ((bottom_points['price'].iloc[-2] > bottom_points['price'].iloc[-1] ) \
            and (top_points['price'].iloc[-2] > top_points['price'].iloc[-1]))  \
            and v_pos > 0.3:
            if os.environ['DEBUG']=='ON':
                print('ignore down trend')
            decision = False


    # 按振幅判断， 如果后3日振幅相比前7日振幅扩大 并且当日是3日最低
    short_his = dataset[-7:].copy()
    short_his['amp'] = short_his['high'] - short_his['low']

    last_amp = short_his['amp'][-3:].mean()
    prev_amp = short_his['amp'][:-3].mean()
    if last_amp > prev_amp*2 \
        and price == short_his['close'].min() \
        and v_pos > 0.4:
        if os.environ['DEBUG']=='ON':
            print('double amp in down trend')
        decision = True

    return decision
