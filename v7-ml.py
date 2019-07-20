#!/usr/bin/env python3

import json, math
import pandas as pd
import numpy as np
from learner_long import Learner as learnerL

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

N_GENERATIONS = 2000
TARGET_DNA = [6,9,3,1,8,2,3,1,3,4,2,1,2,3,10,0,10,1,2,2,3,1,3,4,1,2,2,3]
THRESHOLD_PRECENT = 3

print('Loading dataset ...')
# train_df = pd.read_csv('data/featured-v7.1-HS300-2006-2016', index_col=0)
test_df = pd.read_csv('data/featured-v7.1-HS300-2017-2018.csv', index_col=0)

# pre_c3_up
# pre_c3_down

days = test_df['date'].value_counts().index.sort_values()

for trade_date in days:  
    df = test_df[test_df.date==trade_date]
    long_df  = df[df.fu_c1> THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=False)
    short_df = df[df.fu_c1<-THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=True)

    for sample in long_df.iterrows():
        print(sample,"\n\n")
        ga = learnerL(sample=sample, pop_size=100, n_kid=150)
        # for _ in range(N_GENERATIONS):
        #     dna = ga.evolve()        
        #     print("\r G:",_,dna," "*10, end="")
        #     if (dna == np.round(TARGET_DNA,0)).sum() == len(dna): break
        break


    for sample in short_df.iterrows():
        print(sample)

    break