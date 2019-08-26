#!/usr/bin/env python3

import datetime
import math, sys, os
import progressbar
import multiprocessing as mp
import numpy as np
import pandas as pd
import argparse


from lib.jqdata import *
from lib.dna import *

# parser = argparse.ArgumentParser(description='extract qtable regarding the DNA.')
# parser.add_argument('-v','--ver', dest='dna_version', nargs=1, type=str,
#                     default='v1',help='specify the DNA version number, (default: v1)')
#
# args = parser.parse_args()
# print(vars(args)['dna_version'])
#
# # set output
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)
#
# dna = '0001111101111010'
# call = "DNA{}.to_query('{}')".format('v1',dna)
# q = eval(call)
# print(q)

class DNAv1(object):
    quantile_up = 1.52      # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    quantile_down = -1.59
    def test():
        self = __class__
        print(self.quantile_up)

p60_q25=10323
# for i,p in zip((10,12),(60,10)):
for i,p in zip((13,14),(2,3)):
    print(i,p)

# print(eval("p{}_q25".format(60)))

# DNAv1.test()
