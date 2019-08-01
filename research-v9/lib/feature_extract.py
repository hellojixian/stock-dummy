#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

def min_max_scale(v, min, max):
    return np.clip((v-min)/(max-min),0,1)

def to_categorial(v, categories):
    if v<0: return 0
    if v>1: return categories

    val = v/(1/(categories-1))
    return int(np.round(val+1))
