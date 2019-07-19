#!/usr/bin/env python3

import json, math
import pandas as pd
import numpy as np
import os,sys

import keras
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Input
from keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
from matplotlib import cm

np.random.seed(1337)  # for reproducibility

training_epoch = 0
if len(sys.argv)>=2:
	training_epoch = int(sys.argv[1])


# 设置显示宽度
pd.set_option('display.max_rows', 350)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
encoding_dim = 2

print('Loading dataset ...')
source_data = pd.DataFrame().from_csv('featured_data.csv')
model_saved = 'research_ml_model_weights.h5'

# filter bad data
source_data = source_data[source_data.future_value>-0.2]
source_data = source_data[source_data.future_value< 0.2]

records_before_filter = len(source_data)
source_data=source_data.dropna(how='any',axis='index')
records_after_filter = len(source_data)
print(str(records_before_filter-records_after_filter)+' / '+str(records_before_filter)+' records has NAN issue, been filtered out')

y=source_data['future_value'].values
x=source_data
del x['future_value']
del x['security']
del x['price_ma60_trend']
del x['price_pos_60']
del x['history_amp_100']
del x['history_amp_60']
x=x.values

y*=100

split_ratio = int(len(x) * 0.9)
x_train= x[0:split_ratio]
y_train= y[0:split_ratio]
x_test = x[split_ratio:]
y_test = y[split_ratio:]
# print(x[0:1])
# print(x.shape)
# print(max(y),min(y),y.mean())

# os._exit(0)

def visualize(encoder,x,y):
	# plotting	
	# limit = 2000
	# x=x[0:limit]
	# y=y[0:limit]
	encoded_data = encoder.predict(x)
	plt.clf()	
	plt.scatter(encoded_data[:, 0], 
				encoded_data[:, 1], 
				s=2,
				alpha=0.75,
				cmap=cm.rainbow,
				c=y, vmin=-0.15, vmax=0.15)
	# plt.xlim(-1.3, 0.8)
	# plt.ylim(0, 2.5)
	plt.colorbar()
	plt.pause(0.01)	
	return


# construct the autoencoder model
model = Sequential()
model.add(Dense(32, activation='relu',input_shape=(x_train.shape[1],)))
# model.add(Dense(6, activation='relu'))
model.add(Dense(1))
# load weight
if os.path.exists(model_saved):
	model.load_weights(model_saved)

# compile autoencoder
optimizer = keras.optimizers.Adam(lr=0.0025, beta_1=0.9, beta_2=0.999)
model.compile(optimizer=optimizer, loss='mean_squared_error')

autosave = ModelCheckpoint(model_saved, monitor='val_loss', 
					verbose=0, save_best_only=False, 
					save_weights_only=True, mode='auto', period=1)


for steps in range(training_epoch):
	print('Training model batch '+str(steps+1)+'/'+str(training_epoch)+' ...')
	# training
	model.fit(x_train, y_train,
					validation_split=0.1,
	                nb_epoch=1,
	                batch_size=32,
	                shuffle=True,
	                callbacks=[autosave])
	print('Testing ------------')
	cost = model.evaluate(x_test, y_test, batch_size=40)
	print('\ntest cost:', cost)
	print("-"*100)
	print("\n")

print("Predicting ...")
res_test = model.predict(x_test)
res = pd.DataFrame(data=res_test,columns=['test'])
res['actual'] = pd.Series(y_test, index=res.index)
res['diff'] = res['actual']-res['test'] 
# res = res[res.test>4]
# res = res[res.test<12]
res = round(res,2)
print(res)
print(len(res))

plt.show()