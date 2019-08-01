import numpy as np
import pandas as pd
import sys,os,datetime
from scipy import stats

a1 = np.round(np.random.uniform(0,5, 100),1)

# a1 = [1,3,4,10]
# print(np.quantile(a1,0.4), np.quantile(a1,0.6))
settings = {'u':0.6,'m':0.5,'d':0.4}
for s in settings:
    print(s,settings[s])
securities = ['11','11','22','12','23','22']
print(len(securities))
securities = list(dict.fromkeys(securities))
print(len(securities))


# for _ in range(10):
#     a2 = np.round(np.random.uniform(0,5, 10))
#     print(a2,'\t',np.abs(a1-a2).sum())
