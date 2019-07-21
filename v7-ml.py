#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, math, time, datetime
import pandas as pd
import numpy as np
# from lib.learner.long import Learner as learnerL
from lib.learner.long_threading import Learner as learnerL

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

N_GENERATIONS = 200
THRESHOLD_PRECENT = 2.5
EARLY_STOPPING = 10

GA_POPSIZE = 100
GA_N_KID = 200

train_data_filename = 'data/featured-v7.1-HS300-2006-2016.csv'
test_data_filename  = 'data/featured-v7.1-HS300-2017-2018.csv'
kb_filename = 'data/knowledge_base.pickle'

print('Loading dataset ...')
train_df = pd.read_csv(train_data_filename, index_col=0)
# test_df = pd.read_csv(test_data_filename, index_col=0)
# train_df = test_df.copy()
print(train_df.shape[0],'records')




days = train_df['date'].value_counts().index.sort_values()

for trade_date in days:  
    df = train_df[train_df.date==trade_date]
    long_df  = df[df.fu_c1> THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=False)
    short_df = df[df.fu_c1<-THRESHOLD_PRECENT].sort_values(by=['fu_c1'],ascending=True)

    # 取样逻辑
    for sample_id, sample in long_df.iterrows():
        # 判断是否需要学习
        # 学习逻辑
        improving_stuck_count,last_score = 0,0
        print("SampleID: ",sample_id)
        ga = learnerL(DNA_sample=sample, pop_size=GA_POPSIZE, n_kid=GA_N_KID, dataset=train_df)
        
        for generation_id in range(N_GENERATIONS):
            timestamp = time.time()
            
            best_dna = ga.evolve()        
            evaluation = ga.evaluate_dna(best_dna, deep_eval=True)            
            durtion = int((time.time() - timestamp))
            print("G:",generation_id,\
                '\tscore:', round(evaluation['score'],4),\
                '\thits:',evaluation['hits'],\
                '\twin_r:',round(evaluation['win_r'],3),\
                '\twin:',round(evaluation['mean_win'],2),'/',round(evaluation['max_win'],2),\
                '\trisk:',round(evaluation['mean_risk'],2),'/',round(evaluation['max_risk'],2),\
                '\tprofit:', round(evaluation['profit'],3),\
                '\tdurtion:', datetime.timedelta(seconds=durtion),\
                " "*10)
                        

            if evaluation['score'] <= last_score:
                improving_stuck_count+=1
            else:
                # 有进步就去记录存盘
                # sample_id sample dna generation_id
                print('DNA:', sample_id, 'saved')

            if improving_stuck_count>=EARLY_STOPPING:
                print("EARLY_STOPPING")
                break
            last_score = evaluation['score']
        break

    break

