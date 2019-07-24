#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import warnings,sys

from lib.config import config

if not sys.warnoptions:
    warnings.simplefilter("ignore")

from lib.learning_manager import LearningManager as Manager

learning_mode = 'full'
if len(sys.argv)>1 and sys.argv[1] in ['full','random','improve']:
    learning_mode = sys.argv[1]

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print('Loading dataset ...')
train_df = pd.read_csv(config.get('TRAIN_DATA_FILE'), index_col=0)
validation_df = pd.read_csv(config.get('VALIDATION_DATA_FILE'), index_col=0)

if __name__ == '__main__':
    manager = Manager(train_set=train_df,
                      validation_set=validation_df,
                      key_factor='fu_c1')
    manager.start_learning(how=learning_mode)
