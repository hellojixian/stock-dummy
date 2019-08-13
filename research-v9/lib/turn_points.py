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

def find_turn_points(history, epsilon=None):
    points = history[['num_date','close']].values
    if epsilon is None:
        short_his = history[-5:].copy()
        short_his['amp'] = short_his['high'] - short_his['low']
        ma_amp = short_his['amp'].mean()
        epsilon = ma_amp
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

    short_his = subset[-5:].copy()
    short_his['amp'] = short_his['high'] - short_his['low']
    ma_amp = short_his['amp'].mean()
    epsilon = ma_amp*1
    epsilon_2 = subset['close'].iloc[-1]*0.03
    points = find_turn_points(subset, epsilon)

    decision = False
    fuzzy_range = 0.03
    fuzzy_range_low = 0.015
    close = price = subset['close'].iloc[-1]
    low = subset['low'].iloc[-1]
    open = subset['open'].iloc[-1]
    date = subset.iloc[-1].name
    prev_open = subset['open'].iloc[-2]
    prev_close = subset['close'].iloc[-2]
    prev_change = dataset['change'].iloc[-2]

    buy_signal_count = 0
    v_pos = (price - subset['close'].min()) / (subset['close'].max() - subset['close'].min())

    change = dataset['change'].iloc[-1]

    bottom_points = points[(points.direction=='up')]
    top_points = points[(points.direction=='down')]

    # not enough data
    if points.shape[0]<4:
        if os.environ['DEBUG']=='ON':print('No enough data')
        return False

    if points['direction'].iloc[-2]=='down':
        last_down = (points['price'].iloc[-2] - points['price'].iloc[-1]) / points['price'].iloc[-2]
        last_up = (points['price'].iloc[-2] - points['price'].iloc[-3]) / points['price'].iloc[-2]
        prev_down = (points['price'].iloc[-4] - points['price'].iloc[-3]) / points['price'].iloc[-4]
        since_days = int(points['num_date'].iloc[-1] - points['num_date'].iloc[-2])

        # 下降坡段
        pos = 1
        max_down = subset['change'][-since_days:].min()
        if last_down<0.03 \
            and max_down>-0.04 \
            and since_days<9 \
            and since_days>5 :
            decision = True
            if os.environ['DEBUG']=='ON':
                print('{:.10} not droping so much for {:.0f} days at v_pos: {:.2f} max_d:{:.2f}'.format(str(date),since_days,v_pos,max_down))

        if v_pos>0 and v_pos<=0.05:
            decision = True
            if os.environ['DEBUG']=='ON':
                print('{:.10} Cheap enough vpos:{:.2f}'.format(str(date),since_days,v_pos))

        if last_down > last_up*2 and v_pos<0.1:
            decision = True
            if os.environ['DEBUG']=='ON':
                print('{:.10} try to catch the bottom days:{} vpos:{:.2f}'.format(str(date),since_days,v_pos))

        if (last_down>0.06) \
            or prev_down>0.25: #最后一次的下跌空间要够

            if last_up<0.15 and last_down>0.2 and v_pos>0.2 and v_pos<0.4:
                fuzzy_range=0.05
                decision = True
                if os.environ['DEBUG']=='ON':print('got it 2')

            if v_pos>0.45 or v_pos<0.2:
                fuzzy_range=0.025
                if last_up>0.2 and last_down>0.1:
                    fuzzy_range=0.02
                    decision = True
                    if os.environ['DEBUG']=='ON':print('got it')
            else:
                #下跌幅度不够，往下看支撑位
                if (last_down<0.1 and prev_down<0.25):
                    fuzzy_range=0.01

            support_points = points[(points.direction=='up')]
            support_points = support_points.sort_values(by=["num_date"], ascending=False)
            while(support_points.shape[0]>0):
                point = support_points['price'].iloc[0]
                num_date =  support_points['num_date'].iloc[0]
                date = mdates.num2date(num_date)
                support_since_days = int(dataset['num_date'].iloc[-1] -  num_date)
                support_points = support_points[support_points.price<point].sort_values(by=["num_date"], ascending=False)
                if os.environ['DEBUG']=='ON':
                    print("{:.10}\t p:{:.2f}\t scope: {:.2f} - {:.2f} since {} days\t last_down:{:.2f}/{:.2f} fuzzy_range:{:.2f}/{:.2f}".format(str(date), price,
                        point*(1-fuzzy_range_low), point*(1+fuzzy_range),support_since_days,last_down,prev_down,fuzzy_range, fuzzy_range_low ))
                if (point*(1+fuzzy_range) > price and point*(1-fuzzy_range_low) < price) \
                    or (point*(1+fuzzy_range) > low and point*(1-fuzzy_range_low) < low):
                    if support_since_days<60 :
                        buy_signal_count +=1
                        if os.environ['DEBUG']=='ON':
                            print ("^ signal at {} days ago".format(support_since_days))
                        break
                pos += 1
            if buy_signal_count>0:
                # if subset['close'][-5:].min()*0.99 < low:
                decision = True

        # 说明下跌无力
        if (last_down<0.01 and v_pos<0.2): decision = True
        if (last_down>0.25 and v_pos<0.1): decision = True

        # 阴线反包赶紧扔
        if dataset['change'].iloc[-3]>0.01 and \
            (prev_change>0.01 or change<-0.03 ) and \
            (change <0 and prev_change>0) and \
            (open > prev_close) and \
            (price < prev_open):
            if os.environ['DEBUG']=='ON':
                print("{:.10} 阴线反包 不能买".format(
                    str(dataset.iloc[-1].name)))
            decision = False

        if (dataset['close'][-5:].max() - price)/dataset['close'][-5:].max() <= 0.035 \
            and v_pos <0.3 and since_days>=3:
            if os.environ['DEBUG']=='ON':
                print("{:.10} not droping so much".format(
                    str(dataset.iloc[-1].name)))
            decision = True

        if since_days==1 and v_pos<0.35 and change<-0.06:
            decision = True

        if decision == True and since_days==1 and change < -0.09:
            decision = False

        if os.environ['DEBUG']=='ON':
            print('{:.10}\t buy: {} \tsignal: {} \tdown: {:.3f}/{:.3f} \tup:{:.3f}\t v_pos:{:.2f}\t d:{}\tdays:{}'\
                .format(str(subset.iloc[-1].name), decision,buy_signal_count,last_down,prev_down,last_up,v_pos,points['direction'].iloc[-2],since_days))

    if points['direction'].iloc[-2]=='up':
        last_down = (points['price'].iloc[-3] - points['price'].iloc[-2]) / points['price'].iloc[-3]
        last_up = (points['price'].iloc[-1] - points['price'].iloc[-2]) / points['price'].iloc[-2]

        if bottom_points.shape[0]>=2 \
            and (bottom_points['price'].iloc[-2] < bottom_points['price'].iloc[-1] ) \
            and v_pos < 0.4 and last_up<0.03:
            decision = True

        # 阳线反包 追着买入
        if open < price*1.005 \
            and prev_open > prev_close*1.005 \
            and open < prev_close \
            and price > prev_open \
            and close > open*1.025 \
            and change<0.07 and last_up<0.15:
            if os.environ['DEBUG']=='ON':
                print('Grow line hugging down line')
            decision = True

        # 前面是大绿柱 两根阳线收复绿柱 80%
        if dataset['change'].iloc[-3]<-0.04 \
            and prev_change < abs(dataset['change'].iloc[-3]) \
            and change+prev_change > abs(dataset['change'].iloc[-3])*0.8:
            if os.environ['DEBUG']=='ON':
                print('Recovered big green bar')
            decision = True

        if os.environ['DEBUG']=='ON':
            print('{:.10}\t buy: {} \tsignal: {} \tdown: {:.3f}/000 \tup:{:.3f}\t v_pos:{:.2f}\t d:{}'\
                .format(str(subset.iloc[-1].name), decision,buy_signal_count,last_down,last_up,v_pos,points['direction'].iloc[-2]))

    max_drop = (dataset['high'][-240:].max() - low )/dataset['high'][-240:].max()
    if max_drop > 0.58 and price>open:
        if os.environ['DEBUG']=='ON':
            print("240 max_drop:",max_drop)
        decision = True
    if max_drop > 0.65 and price<open:
        if os.environ['DEBUG']=='ON':
            print("240 65%off max_drop:",max_drop)
        decision = True
    max_drop = (dataset['high'][-60:].max() - low )/dataset['high'][-60:].max()
    if max_drop > 0.48  and price>open and last_up<0.1:
        if os.environ['DEBUG']=='ON':
            print("60 max_drop:",max_drop)
        decision = True


    # 判断是否应该忽略这次购买信号
    if decision == True:
        # 忽略 比如箱体横盘太久了
        if bottom_points.shape[0]>=2 \
            and ((bottom_points['price'].iloc[-2] > bottom_points['price'].iloc[-1] ) \
            and (top_points['price'].iloc[-2] > top_points['price'].iloc[-1]))  \
            and v_pos > 0.3:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - down trend')
            decision = False

        # 忽略 向下有跳空
        if open < price*1.005 \
            and price < prev_close \
            and prev_change < -0.05:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - jump down')
            decision = False

        if open > price*1.005 \
            and prev_close*0.99 > open  \
            and (prev_change+change) < -0.05:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - jump down v2')
            decision = False

        # 忽略下跌幅度不够
        if v_pos == 0 and since_days > 10 and last_down < 0.25:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - Not droping enough yet')
            decision = False

        # 不跟跌停
        if abs((price - open) /open) > 0.07:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - After big drop', (price - open) /open)
            decision = False

        # 跌得太多 反弹太小
        if change < 0.02 \
            and (prev_change<0 and dataset['change'].iloc[-3]<0) \
            and abs(prev_change+dataset['change'].iloc[-3]) > 0.075:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - recover to little')
            decision = False

        # 两阴夹一阳 先别买
        if change < -0.03 \
            and prev_change < 0.03 \
            and dataset['change'].iloc[-3] < -0.03:
            if os.environ['DEBUG']=='ON':
                print('Ignore Buy decision - 2 black bar hugging one red bar')
            decision = False

        # 阴线孕育阴线
        if prev_change<-0.02 and change>0 \
            and prev_close < open and prev_open > close \
            and open > close:
            if os.environ['DEBUG']=='ON':
                print("black bar contains black bar YunXian")
            decision = False

    # 判断是否阴线孕育阳线
    if prev_change<-0.02 and change>0 \
        and prev_close < open and prev_open > close \
        and close > open *1.01:
        if os.environ['DEBUG']=='ON':
            print("black bar contains red bar YunXian")
        decision = True

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

def should_sell(dataset):
    len = 120
    decision = False
    subset = dataset[-len:]
    short_his = subset[-5:].copy()
    short_his['amp'] = short_his['high'] - short_his['low']
    ma_amp = short_his['amp'].mean()
    epsilon = ma_amp
    points = find_turn_points(subset, epsilon)
    if points.shape[0]<4: return False
    if dataset.shape[0]<=0: return False

    last_turn_pt = points['num_date'].iloc[-2]
    days_since_last_turnpoint = dataset[dataset.num_date>last_turn_pt].shape[0]

    price = subset['close'].iloc[-1]
    low = subset['low'].iloc[-1]
    open = subset['open'].iloc[-1]
    v_pos = (price - subset['close'].min()) / (subset['close'].max() - subset['close'].min())

    if points['direction'].iloc[-2]=='down':
        last_down = (points['price'].iloc[-2] - points['price'].iloc[-1]) / points['price'].iloc[-2]
        last_up = (points['price'].iloc[-2] - points['price'].iloc[-3]) / points['price'].iloc[-2]
        prev_down = (points['price'].iloc[-4] - points['price'].iloc[-3]) / points['price'].iloc[-4]

        if days_since_last_turnpoint<=2 \
            and last_down>0.04 \
            and v_pos>0.2:
            if os.environ['DEBUG']=='ON':
                print('sell it',days_since_last_turnpoint)
            decision = True

    # 提前下车逻辑
    if points['direction'].iloc[-2]=='up':
        last_down = (points['price'].iloc[-3] - points['price'].iloc[-2]) / points['price'].iloc[-3]
        last_up = (points['price'].iloc[-1] - points['price'].iloc[-2]) / points['price'].iloc[-1]
        prev_down = 0

        fuzzy_range = 0.03
        fuzzy_range_low = 0.03
        sell_signal_count = 0
        pos = 1
        pressure_points = points[(points.direction=='down') & (points.price<price*(1+fuzzy_range))]
        while(pos<=pressure_points.shape[0]):
            point = pressure_points['price'].iloc[-pos]
            num_date =  pressure_points['num_date'].iloc[-pos]
            date = mdates.num2date(num_date)
            if os.environ['DEBUG']=='ON':
                print("{:.10}\t p:{:.2f}\t scope: {:.2f} - {:.2f}\t last_down:{:.2f}\t up:{:.2f}".format(str(date), price,
                    point*(1-fuzzy_range_low), point*(1+fuzzy_range),last_down, last_up ))
            if (point*(1+fuzzy_range) > price and point*(1-fuzzy_range_low) < price) \
                and price > open:
                sell_signal_count +=1
                break
            pos += 1
        if sell_signal_count>0:
            if v_pos > 0.35 and v_pos <0.5:
                if subset['close'][-5:].max() == price: decision = True

    if os.environ['DEBUG']=='ON':
        print('{:.10}\t sell: {} \tdown: {:.3f}/000 \tup:{:.3f}\t v_pos:{:.2f}\t d:{}'\
            .format(str(subset.iloc[-1].name), decision,last_down,last_up,v_pos,points['direction'].iloc[-2]))


    last_amp = short_his['amp'][-3:].mean()
    prev_amp = short_his['amp'][:-3].mean()
    if last_amp > prev_amp*2 \
        and open > price\
        and v_pos > 0.2 and v_pos<0.8:
        if os.environ['DEBUG']=='ON':
            print('double amp in down trend')
        decision = True
    return decision

def should_stoploss(dataset):
    decision = False
    hold_days = 0
    for i in range(1,len(dataset)-1):
        if dataset['action'].iloc[-i] == 'buy':
            bought_price = dataset['close'].iloc[-i]
            hold_days = i-1
            stop_line = bought_price * (1-0.02)
            highest = dataset['close'][-i:].max()
            lowest = dataset['low'][-i:].min()
            ideal_profit =  (highest - lowest) / lowest
            max_loss = (dataset['close'][-i:].min() - bought_price)/bought_price
            break
    if hold_days == 0: return False

    close = dataset['close'].iloc[-1]
    profit = (close - bought_price)/bought_price

    # 不管如何赔太多了也要扔
    if profit < -0.035:
        if os.environ['DEBUG']=='ON':
            print('stop loss profit:{:.2f}'.format(profit))
        decision = True

    # print(hold_days, profit, ideal_profit)
    if hold_days>3 and profit<0:
        if os.environ['DEBUG']=='ON':
            print('stop loss profit:{:.2f} hold_days:{}'.format(profit, hold_days))
        decision = True

    # 买了以后 没挣钱 连赔4天必须扔
    return decision

def should_hold(dataset):
    decision = True

    hold_days = 0
    for i in range(1,len(dataset)-1):
        if dataset['action'].iloc[-i] == 'buy':
            bought_price = dataset['close'].iloc[-i]
            hold_days = i-1
            stop_line = bought_price * (1-0.02)
            highest = dataset['close'][-i:].max()
            lowest = dataset['low'][-i:].min()
            ideal_profit =  (highest - lowest) / lowest
            max_loss = (dataset['close'][-i:].min() - bought_price)/bought_price
            break
    if hold_days == 0: return False

    close = dataset['close'].iloc[-1]
    open = dataset['open'].iloc[-1]
    profit = (close - bought_price)/bought_price
    change =  dataset['change'].iloc[-1]
    date = dataset.iloc[-1].name
    v_pos = (close - dataset['close'].min()) / (dataset['close'].max() - dataset['close'].min())
    drop_from_highest = (highest - bought_price)/highest
    prev_open = dataset['open'].iloc[-2]
    prev_close = dataset['close'].iloc[-2]
    prev_change = dataset['change'].iloc[-2]

    if hold_days==2:
        stop_line = bought_price

    if hold_days>2 and profit>0:
        stop_line = lowest * (1+ideal_profit/2)

    if hold_days>=2 and change<-0.01 \
        and drop_from_highest > 0.05:
        if os.environ['DEBUG']=='ON':
            print("{:.10} continue drop more than {:.2f}".format(str(date),hold_days,profit))
        decision = False

    if hold_days>=5 and profit<0.03 and max_loss>-0.035:
        if os.environ['DEBUG']=='ON':
            print("{:.10} so many days not growing, days:{} profit:{:.2f}".format(str(date),hold_days,profit))
        decision = False

    if close < stop_line:
        if os.environ['DEBUG']=='ON':
            print("{:.10} lower than stop_line bought: {} => {:.2f} (< {:.2f}) hold days:{}".format(
                str(dataset.iloc[-1].name),bought_price,close,stop_line,hold_days))
        decision = False


    if hold_days==1:
        if ideal_profit>0.1:
            if os.environ['DEBUG']=='ON':
                print("{:.10} stop wining ideal_profit:{:.2f}".format(str(date),ideal_profit))
            decision = False

        grow_rate = 1
        if abs(dataset['change'].iloc[-2])!=0:
            grow_rate = change / abs(dataset['change'].iloc[-2])

        if (dataset['change'].iloc[-2] < 0 and dataset['change'].iloc[-1]>0)\
            and ( grow_rate< 0.5) and change >0.0 and v_pos>0.15:
            if os.environ['DEBUG']=='ON':
                print("{:.10} 1 Growing to slow, grow_rate:{:.2f}".format(str(date),grow_rate))
            decision = False

        # if dataset['change'].iloc[-1]>0 and open>close:
        #     if os.environ['DEBUG']=='ON':
        #         print("{:.10} Grow with green bar, drop it".format(str(date),grow_rate))
        #     decision = False
    if hold_days>=4:
        if (close - bought_price / bought_price)<0.035:
            if os.environ['DEBUG']=='ON':
                print("{:.10} 4 Growing to slow, should not hold".format(str(date)))
            decision = False

    if change <0.09 and (hold_days<=2 and profit > 0.07) \
        or (hold_days<=3 and profit > 0.15):
        if os.environ['DEBUG']=='ON':
            print("{:.10} stop win bought: {} => {:.2f} (< {:.2f}%) hold days:{}".format(
                str(date),bought_price,close,profit*100,hold_days))
        decision = False

    # 阴线反包赶紧扔
    if (dataset['change'].iloc[-2]>0.01 or dataset['change'].iloc[-1]<-0.01 ) and \
        (dataset['change'].iloc[-1] <0 and dataset['change'].iloc[-2]>0) and \
        (dataset['open'].iloc[-1] > dataset['close'].iloc[-2]) and \
        (dataset['close'].iloc[-1] < dataset['open'].iloc[-2]):
        if os.environ['DEBUG']=='ON':
            print("{:.10} downline covered upline".format(
                str(dataset.iloc[-1].name)))
        decision = False

    # 大阴线压顶
    if dataset['change'].iloc[-1] >-0.01 and \
        dataset['high'].iloc[-1] > dataset['close'].iloc[-1]*1.04:
        if os.environ['DEBUG']=='ON':
            print("{:.10} big black bar drop it".format(
                str(dataset.iloc[-1].name)))
        decision = False

    # 向下跳空
    if dataset['change'].iloc[-2] <-0.01 \
        and dataset['open'].iloc[-1] > dataset['close'].iloc[-1]*1.005 \
        and dataset['close'].iloc[-2]*0.99 > dataset['open'].iloc[-1]:
        if os.environ['DEBUG']=='ON':
            print("{:.10} jump dump drop it".format(
                str(dataset.iloc[-1].name)))
        decision = False

    # 判断是否阳线孕育阴线
    if hold_days==1 and change<-0.01 and prev_change>0.02 \
        and prev_close > open and prev_open < close \
        and close < open:
        if os.environ['DEBUG']=='ON':
            print("Red bar contains block bar YunXian")
        decision = False

    if dataset['change'].iloc[-1] <-0.045 :
        decision = False

    return decision
