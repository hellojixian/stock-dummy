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
df1 = pd.DataFrame({'key': ['fooxx', 'bar', 'baz', 'foo'],
                     'value': [1, 2, 3, 5]})
df2 = pd.DataFrame({'key': ['foo', 'bar', 'bacdd', 'fofso'],
                     'value': [5, 6, 7, 8]})

print(df1)
print( df2)
print(pd.merge(df1,df2,how='inner',on='key',suffixes=("","_y")))
