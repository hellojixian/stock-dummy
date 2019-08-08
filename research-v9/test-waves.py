'''
触发点 按过去60日的90分位数作为触发
破了新低 追第一红
'''

import datetime
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
import talib
import pandas as pd
import math, sys

from lib.jqdata import *
from lib.vis import *


mpl.style.use('dark_background')
mpl.rcParams['toolbar'] = 'None'

lookback_size = 600
security='000786.XSHE'
security='000537.XSHE'
end_date=datetime.date(2012,6,15)

history=get_price(security, end_date=end_date, count=lookback_size)
visualize(history)
