#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd

from lib.datasource import fetch_dataset
from lib.strategies import strategies

np.random.seed(10)
# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


DEFAULT_STRATEGY = 'fantan'
parser = argparse.ArgumentParser(description='Strategy Algorithm Traininer')
parser.add_argument('--strategy', '-s',
                    help='The strategy will be evolved ',
                    default=DEFAULT_STRATEGY)
parser.add_argument('--datasource', '-d',
                    type=int,
                    help='Data source ID',
                    default=1)
args = parser.parse_args()

strategy = strategies[args.strategy]()
dataset = fetch_dataset(args.datasource)
print("Dataset loaded: {} records".format(dataset.shape[0]))

for i in range(100):
    if strategy.evolve(training_set=dataset) == False:
        print("TODO: Should pick up another dataset to continue learning")
        break
