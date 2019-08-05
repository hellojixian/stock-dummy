#!/usr/bin/env python3

import pandas as pd
import datetime,time

import scipy.stats
import seaborn as sns
import matplotlib.pylab as plt

from lib.jqdata import *
from lib.feature_extract import *
from lib.backtest import *
from lib.visualize import *
from lib.strategy import Strategy
from lib.kb import KnowledgeBase
from lib.ml import *


# 设置显示宽度
pd.set_option('display.max_rows', 350)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


print('Loading dataset ...')
start_date=datetime.date(2006,7,30)
end_date=datetime.date(2016,12,30)
train_df = get_train_set(300, start_date, end_date)
model_saved = 'data/research_ml_model_weights.h5'

MEASURE = 'buy'
training_epoch=10

true_samples = train_df[train_df.buy==1]
false_samples = train_df.sample(len(true_samples)*2)

df = true_samples.append(false_samples)
df = df.sample(frac=1)

# df = train_df
x = transform_data_buy(df)
y = df[MEASURE].values


split_ratio = int(len(x) * 0.9)
x_train= x[0:split_ratio]
y_train= y[0:split_ratio]
x_test = x[split_ratio:]
y_test = y[split_ratio:]


# construct the autoencoder model
model = get_model(x_train.shape[1])

# compile autoencoder
optimizer = optimizers.Adam(lr=0.0025, beta_1=0.9, beta_2=0.999)
model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

autosave = ModelCheckpoint(model_saved, monitor='val_loss',
					verbose=0, save_best_only=False,
					save_weights_only=True, mode='auto', period=1)


for steps in range(training_epoch):
	print('Training model batch '+str(steps+1)+'/'+str(training_epoch)+' ...')
	# training
	model.fit(x_train, y_train,
					validation_split=0.1,
	                nb_epoch=10,
	                batch_size=32,
	                shuffle=True,
	                callbacks=[autosave])
	print('Testing ------------')
	cost = model.evaluate(x_test, y_test, batch_size=40)
	print('\ntest cost:', cost)
	cost = model.evaluate(x_train, y_train, batch_size=40)
	print('\ntrain cost:', cost)
	print("-"*100)
	print("\n")
