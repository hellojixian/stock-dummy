import pandas as pd
import numpy as np
import warnings,sys,os
import json, pprint
import time
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation

fullset=False

if fullset==True:
    X_file = "test/train_full_X.csv"
    Y_file = "test/train_full_Y.csv"
    s_rate = 1
else:
    X_file = "test/train_X.csv"
    Y_file = "test/train_Y.csv"
    s_rate = 1

print("Reading X data")
X = pd.read_csv(X_file, index_col=0)
X = X.values

print("Reading Y data")
Y = pd.read_csv(Y_file, index_col=0)
Y = Y.values

print(X.shape,Y.shape)
print(Y[0])

split_ratio = int(X.shape[0] * s_rate)
X= X[0:split_ratio]
Y= Y[0:split_ratio]

import keras
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Input, Dropout
from keras.callbacks import ModelCheckpoint

model_saved = "test/t1_weights.h5"
split_ratio = int(X.shape[0] * 0.8)
x_train= X[0:split_ratio]
y_train= Y[0:split_ratio]
x_test = X[split_ratio:]
y_test = Y[split_ratio:]

x_test = x_test[np.where(y_test==[0,1,0])[0]]
y_test = y_test[np.where(y_test==[0,1,0])[0]]

training_epoch = 10
if len(sys.argv)>=2:
    training_epoch = int(sys.argv[1])

# construct the autoencoder model
model = Sequential()
model.add(Dense(500, activation='relu',input_shape=(x_train.shape[1],)))
model.add(Dropout(0.4))
model.add(Dense(10, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(y_train.shape[1], activation='softmax'))
# load weight
if os.path.exists(model_saved):
    model.load_weights(model_saved)

# compile autoencoder
optimizer = keras.optimizers.Adam(lr=0.0025, beta_1=0.9, beta_2=0.999)
model.compile(optimizer=optimizer, loss="binary_crossentropy", metrics=['accuracy'])

autosave = ModelCheckpoint(model_saved, monitor='val_loss',
verbose=0, save_best_only=False,
save_weights_only=True, mode='auto', period=1)


for steps in range(training_epoch):
    print('Training model batch '+str(steps+1)+'/'+str(training_epoch)+' ...')
    # training
    model.fit(x_train, y_train,
    validation_split=0.,
    nb_epoch=10,
    batch_size=32,
    shuffle=False,
    callbacks=[autosave])

    print('Testing ------------')
    cost = model.evaluate(x_test, y_test, batch_size=32)
    t_cost = model.evaluate(x_train, y_train, batch_size=32)
    print('\n\ntrain cost:', t_cost)
    print('\ntest cost:', cost)
    print("-"*100)
