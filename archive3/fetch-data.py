#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys,os,datetime


# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# fetching data
securities = get_index_stocks('000300.XSHG')
start_date = datetime.date(2005,1,1)
end_date = datetime.date(2016,12,30)

knowledge_base = pd.DataFrame()
knowledge_base_filename = "knowledge_base.csv"
i=0
for security in securities:
    frequency = 'daily'
    dataset = get_price(security, start_date=start_date, end_date=end_date, frequency=frequency)

    dataset['security'] = security
    dataset = dataset.join(daily_changes([4,3,2,1,0],dataset))
    dataset = dataset.join(get_env([120,30,10,5],dataset))
    dataset = dataset.join(risk_index([60,30,20,10],dataset))
    dataset = dataset.join(future_value(dataset))
    dataset = dataset.dropna()

    knowledge_base = knowledge_base.append(dataset)
    print("\rprogress: {:.2f}%\t\tsecurity: {}\t\trecords: {} ".format(
        i/len(securities)*100, security, knowledge_base.shape[0]),end="")
    i+=1


knowledge_base = knowledge_base.drop(columns=['open', 'close', 'high', 'low', 'volume', 'money'])
knowledge_base.to_csv(knowledge_base_filename)
print("Done")
