import numpy as np
import pandas as pd
import os

from keras import optimizers
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Input, Dropout
from keras.callbacks import ModelCheckpoint

def transform_data_buy(df):
    bias = 9
    measure = 'buy'

    # dropout features
    report = {}
    for f in df.columns:
        if f[:1]!='f': continue
        cor = np.corrcoef(bias - df[f],df[measure])[0][1]
        report[f]={'cor':abs(cor)}
    report = pd.DataFrame(report)
    report = report.T
    report = report.sort_values(by=["cor"],ascending=False)
    ncols=[]
    i = 0
    for col,rec in report.iterrows():
        # if rec['cor']>0.02:
        ncols.append(col)
        i+=1
        if i>22: break

    print(report)
    df = df[ncols].copy()

    print(ncols)
    return df.values

def get_model(input_dim):
    model_saved = 'data/research_ml_model_weights.h5'
    # construct the autoencoder model
    model = Sequential()
    model.add(Dense(50, activation='relu',input_shape=(input_dim,)))
    model.add(Dropout(0.3))
    # model.add(Dense(10, activation='relu'))
    model.add(Dense(1, activation='sigmoid' ))
    # load weight
    if os.path.exists(model_saved):
    	model.load_weights(model_saved)
    return model
