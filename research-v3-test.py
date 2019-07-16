#!/usr/bin/env python3

import json, math
import pandas as pd
import numpy as np
import os,sys

import keras
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Dropout, Activation
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm

np.random.seed(1337)  # for reproducibility

# filename = 'featured_v3-HS300-2006-2012.csv'
filename = 'featured_v3-HS300-2012-2013.csv'
ml_filename = 'ml_balanced_data.csv'
model_saved = 'research_v3_model_weights.h5'

training_epoch = 0
if len(sys.argv)>=2:
	training_epoch = int(sys.argv[1])


# 设置显示宽度
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
encoding_dim = 2

print('Loading dataset ...')
# if not os.path.isfile(ml_filename):
if True:
	source_data = pd.DataFrame().from_csv(filename)
	source_data = source_data.drop(['date','security','latest_price'],axis=1)

	# step = 3
	source_data.loc[:,'future_change'] = round(source_data['future_change'] * 10,0)
	# source_data.loc[:,'future_change'] = source_data.drop(source_data[source_data.future_change>10].index)
	# source_data.loc[:,'future_change'] = source_data.drop(source_data[source_data.future_change<-10].index)
	# source_data['future_change'] = round(source_data['future_change'] /step ,0)
	source_data.loc[:,'class'] = 1
	# print( source_data['future_change'].value_counts()  )
	# print(source_data.head(50))

	class0 = source_data[source_data.future_change<0]
	class1 = source_data[source_data.future_change==1]	
	class2 = source_data[source_data.future_change>0]
	class2 = class2[class2.future_change<=3]
	class3 = source_data[source_data.future_change>3]
	
	class0.loc[:,'class'] = 0 # 下跌
	class1.loc[:,'class'] = 1 # 横盘
	class2.loc[:,'class'] = 2 # 上涨
	class3.loc[:,'class'] = 3 # 上涨

	# print([len(class0),len(class1),len(class2),len(class2)])
	# samples = min([len(class0),len(class1),len(class2),len(class3)])
	# class0 = class0.sample(samples)
	# class1 = class1.sample(samples)
	# class2 = class2.sample(samples)
	# class3 = class3.sample(samples)

	data = class0.append(class1)
	data = data.append(class2)
	data = data.append(class3)

else:
	data = pd.DataFrame().from_csv(ml_filename)

print( data['class'].value_counts()  )
data = data.drop(['future_change'],axis=1)

X = data.values
Y = np_utils.to_categorical(data['class'])

splitter = 0
X_train = X[:splitter]
X_test = X[splitter:]
Y_train = Y[:splitter]
Y_test = Y[splitter:]



model = Sequential()
model.add(Dense(200, activation='tanh', input_shape=(X_train.shape[1],)))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(4, activation='softmax'))

model.load_weights(model_saved)

# For a multi-class classification problem
model.compile(optimizer='rmsprop',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

score = model.evaluate(X_test, Y_test, batch_size=128)
print('\n\ntest_score:',score)

res_test = model.predict(X_test)
res_test = np.argmax(res_test, axis=1)
actual_test = np.argmax(Y_test, axis=1)
res = pd.DataFrame(data=res_test,columns=['test'])
res['actual'] = pd.Series(actual_test, index=res.index)
print(res)
