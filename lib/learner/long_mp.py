# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import multiprocessing as mp
import math
import time

from lib.learner.ga_core import GACore

class Learner(GACore):

    def __init__(self, DNA_sample, train_set, pop_size,
            n_kid, init_dna=None,validation_set=None,
            key_factor='fu_c1', min_exp=0):

        factors = train_set.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
        super().__init__(pop_size=pop_size, n_kid=n_kid, init_dna=init_dna,
                        factors=factors, key_factor=key_factor)

        self.min_exp = min_exp
        self.train_set = train_set.sort_values(by='date', ascending=True)
        self.DNA_sample = DNA_sample
        self.hr_max_exp = self.train_set[self.train_set[self.key_factor]>self.min_exp].shape[0]/self.train_set.shape[0]*0.05
        self.wr_weight = 1.8

        if validation_set is None:
            self.validation_set = self.train_set
        else:
            self.validation_set = validation_set.sort_values(by="date", ascending=True)

        # 添加评估标准 用于连乘
        self.train_set['_evaluate'] = self.train_set[self.key_factor]/100 + 1
        self.validation_set['_evaluate'] = self.validation_set[self.key_factor]/100 + 1

        # init factor
        scalers = pd.DataFrame()
        for factor in self.factors:
            scaler_max = self.train_set[factor].quantile(0.99)
            scaler_min = self.train_set[factor].quantile(0.01)
            scaler_med = (scaler_max+scaler_min)/2
            scaler = pd.Series([scaler_max,scaler_min,scaler_med],
                index=['max','min','med'])
            scaler.name = factor
            scalers = scalers.append(scaler)
        self.scalers = scalers

        return

    def translateDNA(self, dna):
        def min_max_range(x, range_values):
            return [round( ((xx - min(x)) / (1.0*(max(x) - min(x)))) * (range_values[1] - range_values[0]) + range_values[0], 2) for xx in x]

        decodedDNA = {}
        for i in range(len(self.factors)):
            factor = self.factors[i]
            dna_up_idx, dna_down_idx = i*2, i*2+1
            sample_value = self.DNA_sample[factor]
            factor_max, factor_min = self.scalers.loc[factor,['max','min']].values
            dna_up_bias    = min_max_range([self.DNA_bound[0],dna[dna_up_idx],self.DNA_bound[1]], (sample_value,factor_max) )[1]
            dna_down_bias  = min_max_range([self.DNA_bound[0],dna[dna_down_idx],self.DNA_bound[1]], (factor_min,sample_value))[1]
            decodedDNA[factor+'_u'] = dna_up_bias
            decodedDNA[factor+'_d'] = dna_down_bias
        return decodedDNA



    def evaluate_dna(self, dna, deep_eval=False,
                    dataset="train", min_exp=None):
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

        if min_exp is None:
            min_exp = self.min_exp

        # 设计数据期望
        wr_min, wr_max = 0.4, 0.75
        hr_min, hr_max = 0.0001, self.hr_max_exp
        wr_weight, hr_weight = self.wr_weight,1

        # 评估
        profit,score,win_r,max_win,mean_win,max_risk,mean_risk = 1,0,0,-1,-1,-1,-1
        normalized_wr, normalized_hr = 0,0
        hits_r = 0

        hits = rs.shape[0]
        wins = rs[self.key_factor][rs[self.key_factor]>=min_exp]

        if deep_eval==True:
            profit = np.prod(rs['_evaluate'])
            max_win = wins.quantile(0.9)
            mean_win = wins.mean()
            risks = rs[self.key_factor][rs[self.key_factor]<0]
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
            win_r>wr_min and win_r<wr_max:
            # 标准化数据表达
            normalized_hr = np.tanh(normalization(hits_r, hr_min, hr_max))*1.3
            normalized_wr = np.tanh(normalization(win_r , wr_min, wr_max))*1.3
            sum_weight = sum([wr_weight, hr_weight])
            wr_weight /= sum_weight
            hr_weight /= sum_weight

            score = normalized_wr*wr_weight + normalized_hr*hr_weight

        return {
            "score": score,
            "profit": profit,
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

    def adjust_weight(self):
        step_bound = [0.2, 0.8]
        old_weight = self.wr_weight
        best_dna = self.pop["DNA"][-1]
        res = self.evaluate_dna(best_dna)
        if res['weighted_wr'] < res['weighted_hr']:
            self.wr_weight+=random.uniform(step_bound[0],step_bound[1])
        else:
            self.wr_weight-=random.uniform(step_bound[0],step_bound[1])
        print("WR weight adjusted from {:.2f} to {:.2f}\t\traw_wr:{:.4f}\traw_hr:{:.4f}\t"
            .format(old_weight, self.wr_weight, res['weighted_wr'], res['weighted_hr']))
        return
