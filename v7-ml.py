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

TEST_DNA = [ 1.11099269, 0.68786225, 0.62677514, 3.83376281, 0.25326181, 3.05217483, 1.5169902,  4.59634091, 4.262085, 2.77760774, 2.98038042, 3.12156695, 4.30891929, 2.19669944, 0.57088382, 1.10168299, 1.82048785, 1.00985613, 4.58264332, 2.87930487, 1.38069562, 2.03598805, 3.28330109, 1.793364,  0.78612466, 4.98729083, 2.37608641, 4.69844104, 3.6076005,  4.39978959, 0.88665574, 2.34796301, 3.70966675, 2.55899253]

print('Loading dataset ...')
# train_df = pd.read_csv('data/featured-v7.1-HS300-2006-2016.csv', index_col=0)

test_df = pd.read_csv('data/featured-v7.1-HS300-2017-2018.csv', index_col=0)
train_df = test_df.copy()
print(train_df.shape[0],'records')

days = train_df['date'].value_counts().index.sort_values()

for trade_date in days:  
    df = train_df[train_df.date==trade_date]
    long_df  = df[df.fu_c1> THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=False)
    short_df = df[df.fu_c1<-THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=True)

    for i, sample in long_df.iterrows():
        i, sample = next(long_df.iterrows())
        i, sample = next(long_df.iterrows())
        i, sample = next(long_df.iterrows())
    
        ga = learnerL(DNA_sample=sample, pop_size=50, n_kid=150 , dataset=train_df)

        for _ in range(N_GENERATIONS):
            best_dna = ga.evolve()        
            evaluation = ga.evaluate_dna(best_dna)
            
            print("G:",_,\
                '\tscore:', round(evaluation['score'],3),\
                '\tprofit:', round(evaluation['profit'],3),\
                '\thits:',evaluation['hits'],\
                '\twin_r:',round(evaluation['win_r'],2),\
                '\tmean_win:',round(evaluation['mean_win'],2),\
                '\tmax_risk:',round(evaluation['max_risk'],2),\
                '\tmean_risk:',round(evaluation['mean_risk'],2),\
                " "*10)
        break


    for _, sample in short_df.iterrows():
        print(sample)

    break