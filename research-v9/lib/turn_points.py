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
    return turn_points
