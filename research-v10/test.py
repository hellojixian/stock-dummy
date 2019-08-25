#!/usr/bin/env python3

import datetime
import pandas as pd
import numpy as np
import math, sys, os
import progressbar
import multiprocessing as mp
from lib.jqdata import *

values=[3.97,3.67,3.51,3.57,3.7,3.74,3.84,3.71,3.78,4.08,4.31,4.17,4.14,3.9
,3.89,3.69,3.74,3.64,3.78,3.84,3.83,3.81,3.81,3.71,3.6,3.63,3.65,3.71
,3.62,3.64,3.64,3.65,3.57,3.72,3.7,3.68,3.64,3.6,3.58,3.57,3.62,3.62
,3.58,3.59,3.67,3.64,3.7,3.63,3.63,3.58,3.59,3.58,3.58,3.56,3.56,3.56
,3.54,3.52,3.5,3.55,3.51,3.54,3.53,3.51,3.56,3.55,3.9,3.98,3.84,3.7
,3.7,3.63,3.61,3.68,3.59,3.61,3.62,3.6,3.62,3.57,3.59,3.59,3.56,3.58
,3.56,3.54,3.56,3.56,3.56,3.58]

p_min, p_max = np.min(values), np.max(values)
print(p_min, p_max)

print(values.index(p_min), values.index(p_max))

for i in range(4,8):
    print(7+4-i)

for i in range(8,16,2):
    print(3+int(4-i/2))
