# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import multiprocessing as mp
import math
import time

from lib.learner.ga_core import GACore

class Learner(GACore):

    def __init__(self, base_knowledge, train_set,
            pop_size=50, n_kid=50, validation_set=None,
            key_factor='fu_c1', max_exp=0):
        factors = train_set.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
        super().__init__(pop_size=pop_size, n_kid=n_kid,
                        factors=factors, key_factor=key_factor)

        self.max_exp = max_exp
        self.train_set = train_set.sort_values(by='date', ascending=True)
        self.base_knowledge = base_knowledge
        self.wr_weight = 1.8

        if validation_set is None:
            self.validation_set = self.train_set
        else:
            self.validation_set = validation_set.sort_values(by="date", ascending=True)
        return


    def translateDNA(self, dna):
        # 这部分代码是翻译反向DNA的 先暂时放在这里
        t_dna = np.zeros(len(dna))
        for i in range(int(len(dna)/2)):
            t_dna[i*2],t_dna[i*2+1]= np.sort([dna[i*2],dna[i*2+1]])
        dna = t_dna

        decodedDNA = {}
        for i in range(len(self.factors)):
            factor = self.factors[i]
            dna_down_idx, dna_up_idx = i*2, i*2+1
            factor_max, factor_min = self.base_knowledge[factor+'_u'], self.base_knowledge[factor+'_d']
            dna_up_bias    = self.value_scale(dna[dna_up_idx],(factor_min,factor_max))
            dna_down_bias  = self.value_scale(dna[dna_down_idx],(factor_min,factor_max))
            decodedDNA[factor+'_u'] = dna_up_bias
            decodedDNA[factor+'_d'] = dna_down_bias
        return decodedDNA

    def evaluate_dna(self, dna, deep_eval=False,
                    dataset="train", max_exp=None):
        """
        Args
            deep_eval: 是否进行深度评估，包括风险评估等，消耗性能多一些，只在保存之前使用
            dataset: 使用哪个样本集进行评估 ['train','validation']
        """
        dna = self.translateDNA(dna)
        if dataset == "validation":
            rs = self.validation_set
        else:
            rs = self.train_set

        # 筛选 静态编译
        rs = eval(self._data_filter)
        # print(rs.shape)
        # print('DNA',dna)
        # print('KNOWLEDGE',self.base_knowledge)
        # import sys
        # sys.exit()
        if max_exp is None:
            max_exp = self.max_exp

        # 设计数据期望
        wr_min, wr_max = 0.4, 0.95
        hr_min, hr_max = 0.0001, 0.1
        wr_weight, hr_weight = self.wr_weight,1

        # 评估
        score,win_r,max_win,mean_win,max_risk,mean_risk = 0,0,-1,-1,-1,-1
        normalized_wr, normalized_hr = 0,0
        hits_r = 0

        hits = rs.shape[0]
        wins = rs[self.key_factor][rs[self.key_factor]<=max_exp]

        if deep_eval==True:
            max_win = wins.quantile(0.9)
            mean_win = wins.mean()
            risks = rs[self.key_factor][rs[self.key_factor]>0]
            if risks.shape[0]>0:
                max_risk = risks.quantile(0.1)
                mean_risk = risks.mean()

        if hits>0:
            win_r = wins.shape[0] / hits
        hits_r = rs.shape[0] / self.train_set.shape[0]

        def normalization(x,min,max):
            return (x-min)/(max-min)

        # 扔掉极端值
        if  hits_r>hr_min and\
            wr_min<win_r and win_r<wr_max:
            # 标准化数据表达
            normalized_hr = np.tanh(normalization(hits_r, hr_min, hr_max))*1.3
            normalized_wr = np.tanh(normalization(win_r , wr_min, wr_max))*1.3
            sum_weight = sum([wr_weight, hr_weight])
            wr_weight /= sum_weight
            hr_weight /= sum_weight

            score = normalized_wr*wr_weight + normalized_hr*hr_weight

        return {
            "score": score,
            "hits":  hits,
            "hits_r": hits_r,
            "weighted_hr": normalized_hr*hr_weight,
            "weighted_wr": normalized_wr*wr_weight,
            "win_r": win_r,
            "max_win": max_win,
            "mean_win": mean_win,
            "max_risk": max_risk,
            "mean_risk": mean_risk,
        }
