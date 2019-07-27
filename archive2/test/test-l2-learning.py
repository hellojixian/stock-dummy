#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,sys,inspect
import numpy as np
import pandas as pd

parentdir = os.path.dirname(os.getcwd())
sys.path.insert(0,parentdir)

from lib.config import config
from lib.l2_learning_manager import L2LearningManager as L2LM

KB_FILENAME = os.path.join(parentdir,'data/knowledge_base.h5')
KB_KEY = 'KnowledgeBase'

train_df = pd.read_csv(os.path.join(parentdir,config.get('TRAIN_DATA_FILE')), index_col=0)
validation_df = pd.read_csv(os.path.join(parentdir,config.get('VALIDATION_DATA_FILE')), index_col=0)

knowledge_base = pd.read_hdf(KB_FILENAME, key=KB_KEY)
knowledge_base = knowledge_base.sort_values(by=['win_r'],ascending=False)
# k = knowledge_base.iloc[5]
k = knowledge_base.sample(1).iloc[0]
print(k)
base_knowledge = k['knowledge']

print("Base knowledge ID: {}".format(k.name))
l2m = L2LM( base_knowledge=base_knowledge,
            train_set=train_df,
            validation_set=validation_df, key_factor="fu_c1" )
l2m.start_learning()
