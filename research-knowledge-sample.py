#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This command line to will merge all knowledge base files into ./data/knowledge_base.h5
"""
import pandas as pd
import numpy as np
import warnings,sys,os
import json, pprint

KB_FILENAME = 'data/knowledge_base.h5'
KB_KEY = 'KnowledgeBase'


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

print("Loading local knowledge base...\t\t")
kb = pd.read_hdf(KB_FILENAME, key=KB_KEY)
kb = kb.sort_values(by=['win_r'],ascending=False)


try:
    dataset = sys.argv[1]
    slice = int(sys.argv[2])
except:
    slice=10
    dataset= 'validation'

def _compile_filter(factors):
    filter = "rs["
    for _ in range(len(factors)):
        factor = factors[_]
        filter += " (rs."+factor+" < dna['"+factor+"_u']) & (rs."+factor+" > dna['"+factor+"_d']) & "
    filter += "True ]"
    return filter

data_source = {
    'train':'data/featured-v7.1-HS300-2006-2016.csv',
    'validation':'data/featured-v7.1-HS300-2017-2018.csv'}

print('Loading dataset ...')
df = pd.read_csv(data_source[dataset], index_col=0)
factors = df.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
k = kb.iloc[3]
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(k['knowledge'])
dna = k['knowledge']
rs = df
rs = eval(_compile_filter(factors))

rs_wr = rs[rs.fu_c1>0].shape[0]/rs.shape[0]

scopes = np.linspace(0,rs.shape[0],slice+1,dtype='int')
report = pd.DataFrame()
for factor in factors:
    for asc in [True, False]:
        rs = rs.sort_values(by=[factor],ascending=asc)
        record = pd.Series()
        for i in range(slice):
            df = rs.iloc[scopes[i]:scopes[i+1]]
            wr = df[df.fu_c1>0].shape[0]/df.shape[0]
            record['slice_{:.0f}'.format((i)/slice*100)] = round(wr*100,2)
        cond = 'asc'
        if asc == False: cond = 'desc'
        record.name="{}_{}".format(factor, cond)
        report = report.append(record)
report = report.sort_values(by=['slice_0'],ascending=False)
print(report)
print("-"*13+"-"*slice*10)
print("full set wr: {:.2f}% of {:d} records".format(rs_wr*100, rs.shape[0]))
print("-"*13+"-"*slice*10)
