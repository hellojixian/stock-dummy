#!/usr/bin/env python3
import argparse

from lib.datasource import fetch_dataset
from lib.strategies import strategies

DEFAULT_STRATEGY = 'zhuizhang'
parser = argparse.ArgumentParser(description='Strategy Algorithm Traininer')
parser.add_argument('--strategy', '-s',
                    help='The strategy will be evolved ',
                    default=DEFAULT_STRATEGY)
args = parser.parse_args()

strategy = strategies[args.strategy]()
dataset = fetch_dataset(quantity=1)

for i in range(100):
    if strategy.evolve(training_set=dataset) == False:
        print("TODO: Should pick up another dataset to continue learning")
        break
