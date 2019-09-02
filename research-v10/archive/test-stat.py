#!/usr/bin/env python3

import datetime
import pandas as pd
import math, sys, os
import progressbar

from lib.jqdata import *
from lib.func import *

pn = get_prime_numbers(5,250)

filename = 'data/dataset-labeled.csv'
start_date=datetime.date(2005,4,15)
end_date=datetime.date(2018,4,15)
np.random.seed(0)
dataset = pd.read_csv(filename)

security_list = get_all_securites().sample(1)
security = security_list['security'].iloc[0]

history = dataset[dataset.security==security]
print(history.shape)
