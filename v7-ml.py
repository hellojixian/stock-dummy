#!/usr/bin/env python3

import json, math
import pandas as pd
import numpy as np
from learner_long import Learner as learnerL

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

N_GENERATIONS = 3000
THRESHOLD_PRECENT = 2.5

print('Loading dataset ...')
train_df = pd.read_csv('data/featured-v7.1-HS300-2006-2016.csv', index_col=0)
# test_df = pd.read_csv('data/featured-v7.1-HS300-2017-2018.csv', index_col=0)
# train_df = test_df.copy()
print(train_df.shape[0],'records')

days = train_df['date'].value_counts().index.sort_values()

for trade_date in days:  
    df = train_df[train_df.date==trade_date]
    long_df  = df[df.fu_c1> THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=False)
    short_df = df[df.fu_c1<-THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=True)

    for sample_id, sample in long_df.iterrows():
        sample_id, sample = next(long_df.iterrows())
        sample_id, sample = next(long_df.iterrows())
        sample_id, sample = next(long_df.iterrows())
        
        print("SampleID: ",sample_id)
        ga = learnerL(DNA_sample=sample, pop_size=100, n_kid=200 , dataset=train_df)

        for _ in range(N_GENERATIONS):
            best_dna = ga.evolve()        
            evaluation = ga.evaluate_dna(best_dna)
            
            print("G:",_,\
                '\tscore:', round(evaluation['score'],3),\
                '\thits:',evaluation['hits'],\
                '\twin_r:',round(evaluation['win_r'],2),\
                '\tmean_win:',round(evaluation['mean_win'],2),\
                '\tmax_risk:',round(evaluation['max_risk'],2),\
                '\tmean_risk:',round(evaluation['mean_risk'],2),\
                '\tprofit:', round(evaluation['profit'],3),\
                " "*10)
        break


    for _, sample in short_df.iterrows():
        print(sample)

    break