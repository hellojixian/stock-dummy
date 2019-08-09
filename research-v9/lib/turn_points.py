from rdp import rdp
import numpy as np
import pandas as pd

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
    epsilon = history['close'].iloc[-1]*0.07
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
    fuzzy_range_low = 0.08
    price = subset['close'].iloc[-1]
    low = subset['low'].iloc[-1]
    buy_signal_count = 0

    if points['direction'].iloc[-2]=='down':
        last_vspace = (points['price'].iloc[-2] - points['price'].iloc[-1]) / points['price'].iloc[-2]
        support_points = points[(points.direction=='up') & (points.price>low*(1-fuzzy_range_low))]
        # 下降破断
        pos = 1
        if last_vspace>0.08: #最后一次的下跌空间要够
            while(pos<support_points.shape[0]):
                point = support_points['price'].iloc[-pos]
                if (point*(1+fuzzy_range) > price and point*(1-fuzzy_range) < price) \
                    or (point*(1+fuzzy_range) > low and point*(1-fuzzy_range_low) < low):
                    buy_signal_count +=1
                    # print(last_vspace, price, point, point*(1+fuzzy_range), point*(1-fuzzy_range), pos)
                pos += 1
            if buy_signal_count>0 and buy_signal_count<3:
                if subset['low'][-5:].min() == low: decision = True

        max_drop = (dataset['high'][-240:].max() - low )/dataset['high'][-240:].max()
        if max_drop > 0.58: decision = True
        max_drop = (dataset['high'][-60:].max() - low )/dataset['high'][-60:].max()
        if max_drop > 0.48: decision = True

        print('{:.10}\t buy: {} \tsignal: {} \tlast_vspace: {:.3f}'.format(str(subset.iloc[-1].name), decision,buy_signal_count,last_vspace))
    return decision
