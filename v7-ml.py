#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import warnings,sys

if not sys.warnoptions:
    warnings.simplefilter("ignore")

from lib.learning_manager import LearningManager as Manager

learning_mode = 'full'
if len(sys.argv)>1 and sys.argv[1] in ['full','random','improve']:
    learning_mode = sys.argv[1]

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


train_data_filename = 'data/featured-v7.1-HS300-2006-2016.csv'
test_data_filename  = 'data/featured-v7.1-HS300-2017-2018.csv'

print('Loading dataset ...')
train_df = pd.read_csv(train_data_filename, index_col=0)
# test_df = pd.read_csv(test_data_filename, index_col=0)
# train_df = test_df.copy()

if __name__ == '__main__':
    manager = Manager(train_set=train_df, key_factor='fu_c1')
    manager.start_learning(how=learning_mode)
