import numpy as np
import scipy.stats
import talib as ta
import math

# a=[0.2,0.1,0.3,-0.3,0.1]
# b=[0.1,0.3,-0.3,0.1,0.1]

a = np.array([0.7,0.1,0.2,0.3,0.2,0.6,0.5,0.6])
w = [2,1,1]


def HMA(data):
    periods   = 4
    wmaA = ta.WMA(data,timeperiod = periods / 2) * 2
    wmaB = ta.WMA(data,timeperiod = periods)
    wmaDiffs = wmaA - wmaB
    hma = ta.WMA(wmaA - wmaB, math.sqrt(periods))
    return hma

print(HMA(a))
