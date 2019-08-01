#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys,os,datetime
import gc


# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

securities = []

# fetching data

start_date = datetime.date(2005,1,1)
end_date = datetime.date(2016,12,30)
knowledge_base_filename = "knowledge_base.csv"

# start_date = datetime.date(2017,1,1)
# end_date = datetime.date(2019,6,30)
# knowledge_base_filename = "test_set.csv"

securities.extend(get_index_stocks('000905.XSHG'))
securities.extend(get_index_stocks('000300.XSHG'))

securities = list(dict.fromkeys(securities))
print(len(securities))

slices = np.split(np.array(range(0,len(securities))),5)
for slice_i in range(len(slices)):
    sec_slice = slices[slice_i]
    knowledge_base = pd.DataFrame()
    for sec_i in sec_slice:
        security = securities[sec_i]
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
            sec_i/(len(securities)-1)*100, security, knowledge_base.shape[0]),end="")

    knowledge_base=reduce_kb(knowledge_base)
    knowledge_base.to_csv(knowledge_base_filename+"_"+str(slice_i), index=False)
    del knowledge_base
    gc.collect()
    print("\nSave progress ", slice_i)

print("merging")
knowledge_base = pd.DataFrame()
for slice_i in range(len(slices)):
    f=knowledge_base_filename+"_"+str(slice_i)
    ds = pd.read_csv(f)
    knowledge_base = knowledge_base.append(ds)
    del ds
    gc.collect()
    os.remove(f)
    print("merged slice ", slice_i)

knowledge_base.to_csv(knowledge_base_filename, index=False)
del knowledge_base
gc.collect()
print("all done") 
