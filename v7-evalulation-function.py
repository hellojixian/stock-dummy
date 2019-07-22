#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

samples = 101

def normalization(x,min,max):
    return (x-min)/(max-min)

wr_min, wr_max = 0.5, 1.0
hr_min, hr_max = 0.001,0.01

x = np.round(np.linspace(0,100, samples))
data_wr = np.linspace(wr_min, wr_max, samples)
data_hr = np.linspace(0.001,0.01, samples)

fig =plt.figure(figsize=(14,6))
ax1 =fig.add_subplot(121)
ax2 =fig.add_subplot(122)

# 可视化 WR 的标准化
ax1.plot(x, data_wr,label='raw_wr', alpha=0.3, color='b')
ax1.plot(x, np.tanh(normalization(data_wr, wr_min, wr_max))*1.3,label='tanh_normalized', color='g')
ax1.plot(x, normalization(data_wr, wr_min, wr_max),label='min_max_normalized', color='r')
ax1.set_ylabel('score')
ax1.set_xlabel('samples')
ax1.legend(loc='upper left')
ax1.set_xticks(np.linspace(0,100, 9))
ax1.set_yticks(np.round(np.linspace(0,1, 9),2))
ax1.set_ylim(0,1)
ax1.set_xlim(0,100)
ax1.set_title("Transform WR")
ax1.grid(color='gray', linestyle='dashed',alpha=0.3)

# 可视化 HR 的标准化
ax2.plot(x, data_hr,label='raw_wr', alpha=0.5)
ax2.plot(x, normalization(data_hr,hr_min, hr_max),label='min_max_normalized',color='b', alpha=0.3)
ax2.plot(x, np.tanh(normalization(data_hr,hr_min, hr_max))*1.3,label='tanh_mm_normalized',color='g')
ax2.plot(x, np.log(1+normalization(data_hr,hr_min, hr_max)),label='log_mm_normalized',color='r')
ax2.set_ylabel('score')
ax2.set_xlabel('samples')
ax2.legend(loc='upper left')
ax2.set_xticks(np.linspace(0,100, 9))
ax2.set_yticks(np.round(np.linspace(0,1, 9),2))
ax2.set_ylim(0,1)
ax2.set_xlim(0,100)
ax2.set_title("Transform HR")
ax2.grid(color='gray', linestyle='dashed',alpha=0.3)

plt.show()
