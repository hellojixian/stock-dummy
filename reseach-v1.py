#!/usr/bin/env python3

import json, math
import pandas as pd
import numpy as np
import os,sys

from keras.models import Model, load_model
from keras.layers import Dense, Input
from keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
from matplotlib import cm

np.random.seed(1337)  # for reproducibility

training_epoch = 0
if len(sys.argv)>=2:
	training_epoch = int(sys.argv[1])


# 设置显示宽度
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
encoding_dim = 2

print('Loading dataset ...')
source_data = pd.DataFrame().from_csv('featured_data.csv')
model_saved = 'research_v1_model_weights.h5'
encoder_saved = 'research_v1_encoder_weights.h5'

y=source_data['future_value'].values
x=source_data
del x['future_value']
x=x.values

# print(source_data['future_value'][0:100])
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


input_len = x.shape[1]
input_data=Input(shape=(input_len,))

# encoder layers
encoded = Dense(12, activation='tanh')(input_data)
encoded = Dense(8, activation='tanh')(encoded)
encoded = Dense(4, activation='tanh')(encoded)
encoder_output = Dense(encoding_dim)(encoded)

# decoder layers
decoded = Dense(4, activation='tanh')(encoder_output)
decoded = Dense(8, activation='tanh')(decoded)
decoded = Dense(12, activation='tanh')(decoded)
decoded = Dense(input_len, activation='tanh')(decoded)


# construct the encoder model for plotting
encoder = Model(input=input_data, output=encoder_output)

# construct the autoencoder model
autoencoder = Model(input=input_data, output=decoded)
if os.path.exists(model_saved):
	autoencoder.load_weights(model_saved)
	encoder = Model(input=autoencoder.input, output=autoencoder.layers[4].output)	
	visualize(encoder,x,y)
# compile autoencoder
# autoencoder.compile(optimizer='adam', loss='mse')
autoencoder.compile(optimizer='adadelta', loss='mse')

autosave = ModelCheckpoint(model_saved, monitor='val_loss', 
					verbose=0, save_best_only=False, 
					save_weights_only=True, mode='auto', period=1)


for steps in range(training_epoch):
	print('Training model batch '+str(steps+1)+'/'+str(training_epoch)+' ...')
	# training
	autoencoder.fit(x, x,
	                nb_epoch=10,
	                batch_size=24,
	                shuffle=True,
	                callbacks=[autosave])
	visualize(encoder,x,y)

plt.show()