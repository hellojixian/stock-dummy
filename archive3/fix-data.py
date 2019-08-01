import numpy as np
import pandas as pd
import sys,os,datetime

# file = 'data/test_set.csv'
file = 'data/knowledge_base.csv'

df = pd.read_csv(file,index_col=0)
print(df.shape)
subset = df[df.future_risk>=0]
subset = subset.sort_values(by=["future_risk"], ascending=True)
print(subset.head(5))
