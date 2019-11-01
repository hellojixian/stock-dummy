#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd

from lib.datasource import fetch_dataset
from lib.backtest import backtest

np.random.seed(10)
# set output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

parser = argparse.ArgumentParser(description='Strategy back test')
parser.add_argument('--datasource', '-d',
                    type=int,
                    help='Data source ID',
                    default=1)
args = parser.parse_args()

dataset = fetch_dataset(args.datasource)
print("Dataset loaded: {} records".format(dataset.shape[0]))

backtest(dataset).run()
