#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from lib.learning_manager import LearningManager as Manager

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


train_data_filename = 'data/featured-v7.1-HS300-2006-2016.csv'
test_data_filename  = 'data/featured-v7.1-HS300-2017-2018.csv'

print('Loading dataset ...')
train_df = pd.read_csv(train_data_filename, index_col=0)
# test_df = pd.read_csv(test_data_filename, index_col=0)
# train_df = test_df.copy()

manager = Manager(train_set=train_df, key_factor='fu_c1')
manager.start_learning(how='full')
