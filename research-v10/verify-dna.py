#!/usr/bin/env python3

import datetime
import pandas as pd
import math, sys, os
import progressbar

from lib.jqdata import *
from lib.func import *
from lib.dna import *

filename = 'data/dataset-labeled-min.csv'
np.random.seed(0)
dataset = pd.read_csv(filename)

cores = [DNAv1, DNAv2, DNAv3, DNAv4, DNAv5, DNAv6]
for i in range(len(dataset)):
    record = dataset.iloc[i]
    r = []
    for core in cores:
        dna = core.to_dna(record)
        query = core.to_query(dna)
        subset = pd.DataFrame([record])
        if subset[subset.eval(query)].shape[0]==1:
            r.append(dna)
        else:
            print("{:05d}\t{}\t{}\t{}".format(i,dna, core.name,'mismatched'))
        assert(subset[subset.eval(query)].shape[0]==1)

    print("{:05d}\t{}\t{}".format(i,' '.join(r), 'verified'))
