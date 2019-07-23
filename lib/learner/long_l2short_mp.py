# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import multiprocessing as mp
import math
import time

from lib.learner.ga_core import GACore

class Learner(GACore):

    def __init__(self, train_set, pop_size, base_knowledge,
            n_kid, validation_set=None,
            key_factor='fu_c1', max_exp=0):
        self.max_exp = max_exp
        self.key_factor = key_factor
        self.train_set = train_set.sort_values(by='date', ascending=True)
        self.factors = train_set.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
        self.DNA_size = len(self.factors)*2
        self.DNA_bound = [0, 10]
        self.pop_size = pop_size
        self.n_kid = n_kid
        self.base_knowledge = base_knowledge
        self.hr_max_exp = self.train_set[self.train_set[self.key_factor]<self.max_exp].shape[0]/self.train_set.shape[0]*0.01

        if validation_set is None:
            self.validation_set = self.train_set
        else:
            self.validation_set = validation_set.sort_values(by="date", ascending=True)

        # 编译数据筛选器 用于eval执行
        self._data_filter = self._compile_filter()

        # initialize the pop DNA values,
        # initialize the pop mutation strength values
        self.pop = dict(DNA=np.mean(self.DNA_bound)* abs(np.random.randn(1, self.pop_size, self.DNA_size))[0],
                        mut_strength=np.random.rand(self.pop_size, self.DNA_size))

        # 添加评估标准 用于连乘
        self.train_set['_evaluate'] = self.train_set[self.key_factor]/100 + 1
        self.validation_set['_evaluate'] = self.validation_set[self.key_factor]/100 + 1
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

    # 增加多线程内核
    def get_fitness(self, dna_series):
        # v=np.zeros(len(dna_series))
        v = mp.Array('f',len(dna_series))
        v[:] = np.zeros(len(dna_series))

        # 切分任务到多个线程
        splited = np.array_split(v, N_THREAD)
        threads = []
        start = 0
        processed_count = mp.Value('i',0)
        def runner(v, start, end, processed_count):
            total = len(v[:])
            for i in range(start,end):
                score = self.evaluate_dna(dna_series[i])['score']

                v[i]=score
                processed_count.value+=1
                print('\rEvaluating: '+str(round(processed_count.value/total*100,2))+"%"+" of "+str(len(v))+" DNAs" + (" "*6),end='')

            return

        for i in range(len(splited)):
            end = start + len(splited[i])
            t = mp.Process(target=runner, args=(v, start, end, processed_count))
            start = end

            t.start()
            threads.append(t)

        # time.sleep(10)
        # join all threads
        for t in threads:
            t.join()

        v = np.array(v[:])
        return v

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
        wr_weight, hr_weight = 2.5,1

        # 评估
        profit,score,win_r,max_win,mean_win,max_risk,mean_risk = 1,0,0,-1,-1,-1,-1
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
            normalized_hr = np.tanh(normalization(hits_r,hr_min, hr_max))*1.3
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
            "win_r": win_r,
            "max_win": max_win,
            "mean_win": mean_win,
            "max_risk": max_risk,
            "mean_risk": mean_risk,
        }
