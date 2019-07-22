# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import multiprocessing as mp
import math
import time

np.set_printoptions(edgeitems=20)
np.core.arrayprint._line_width = 280

if mp.cpu_count()>=4:
    N_THREAD = mp.cpu_count() -1  # 建议留一个CPU核心避免死机
N_THREAD = mp.cpu_count()


class Learner(object):

    def __init__(self, DNA_sample, dataset, pop_size, n_kid, init_dna=None, key_factor='fu_c1'):
        self.key_factor = key_factor
        self.dataset = dataset.sort_values(by='date', ascending=True)
        self.factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
        self.DNA_sample = DNA_sample
        self.DNA_size = len(self.factors)*2
        self.DNA_bound = [0, 10]
        self.pop_size = pop_size
        self.n_kid = n_kid

        if init_dna is None:
            init_dna = 5* abs(np.random.randn(1, self.pop_size, self.DNA_size))[0]
        else:
            init_dna = np.array([init_dna]).repeat(self.pop_size, axis=0)

        self.pop = dict(DNA=init_dna,         # initialize the pop DNA values,
                        mut_strength=np.random.rand(self.pop_size, self.DNA_size))               # initialize the pop mutation strength values

        # 添加评估标准 用于连乘
        self.dataset['_evaluate'] = self.dataset[self.key_factor]/100 + 1

        # init factor
        scalers = pd.DataFrame()
        for factor in self.factors:
            scaler_max = self.dataset[factor].quantile(0.99)
            scaler_min = self.dataset[factor].quantile(0.01)
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
                print('\rEvaluating: '+str(round(processed_count.value/total*100,2))+"%"+" of "+str(len(v))+" samples" + (" "*6),end='')

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

    # 只有在修改了特征的时候才需要手动运行一次
    # 这是为了静态编译提升性能虽然不好看 但是性能提升了60倍
    def _compile_filter(dataset):
        factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
        print("copy paste below code to evaluate_dna() ")
        for _ in range(len(factors)):
            factor = factors[_]
            # 参考代码
            # rs = rs[ (rs[factor] < dna[factor+'_u']) & (rs[factor] > dna[factor+'_d'])]
            print(" (rs."+factor+" < dna['"+factor+"_u']) & (rs."+factor+" > dna['"+factor+"_d']) & \\",)
        print("\n")
        return

    def evaluate_dna(self, dna, deep_eval=False):
        dna = self.translateDNA(dna)
        rs = self.dataset

        # 筛选 静态编译
        rs = rs[(rs.pre_c3 < dna['pre_c3_u']) & (rs.pre_c3 > dna['pre_c3_d']) & \
                 (rs.pre_c2 < dna['pre_c2_u']) & (rs.pre_c2 > dna['pre_c2_d']) & \
                 (rs.pre_c1 < dna['pre_c1_u']) & (rs.pre_c1 > dna['pre_c1_d']) & \
                 (rs.today_c < dna['today_c_u']) & (rs.today_c > dna['today_c_d']) & \
                 (rs.up_l < dna['up_l_u']) & (rs.up_l > dna['up_l_d']) & \
                 (rs.dn_l < dna['dn_l_u']) & (rs.dn_l > dna['dn_l_d']) & \
                 (rs.open_c < dna['open_c_u']) & (rs.open_c > dna['open_c_d']) & \
                 (rs.ma5_pos < dna['ma5_pos_u']) & (rs.ma5_pos > dna['ma5_pos_d']) & \
                 (rs.ma10_pos < dna['ma10_pos_u']) & (rs.ma10_pos > dna['ma10_pos_d']) & \
                 (rs.ma60_pos < dna['ma60_pos_u']) & (rs.ma60_pos > dna['ma60_pos_d']) & \
                 (rs.ma5_ang < dna['ma5_ang_u']) & (rs.ma5_ang > dna['ma5_ang_d']) & \
                 (rs.ma10_ang < dna['ma10_ang_u']) & (rs.ma10_ang > dna['ma10_ang_d']) & \
                 (rs.ma60_ang < dna['ma60_ang_u']) & (rs.ma60_ang > dna['ma60_ang_d']) & \
                 (rs.p5_wr < dna['p5_wr_u']) & (rs.p5_wr > dna['p5_wr_d']) & \
                 (rs.p10_wr < dna['p10_wr_u']) & (rs.p10_wr > dna['p10_wr_d']) & \
                 (rs.prewr1 < dna['prewr1_u']) & (rs.prewr1 > dna['prewr1_d']) & \
                 (rs.win_r < dna['win_r_u']) & (rs.win_r > dna['win_r_d']) & \
                 (rs.h100_pos < dna['h100_pos_u']) & (rs.h100_pos > dna['h100_pos_d']) & \
                 (rs.h10_pos < dna['h10_pos_u']) & (rs.h10_pos > dna['h10_pos_d']) ]
        # 评估
        profit,score,win_r,max_win,mean_win,max_risk,mean_risk = 1,0,0,-1,-1,-1,-1
        hits_r = 0

        hits = rs.shape[0]
        wins = rs[self.key_factor][rs[self.key_factor]>=0]

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
        hits_r = rs.shape[0] / self.dataset.shape[0]

        def normalization(x,min,max):
            return (x-min)/(max-min)

        # 设计数据期望
        wr_min, wr_max = 0.5, 1.0
        hr_min, hr_max = 0.001,0.015
        wr_weight, hr_weight = 1.8,  1

        # 标准化数据表达
        normalized_hr = np.tanh(normalization(hits_r,hr_min, hr_max))*1.3
        normalized_wr = np.tanh(normalization(win_r, wr_min, wr_max))*1.3
        sum_weight = sum([wr_weight, hr_weight])
        wr_weight /= sum_weight
        hr_weight /= sum_weight

        score = normalized_wr*wr_weight + normalized_hr*hr_weight
        # 修正标准差过大
        score -= abs(normalized_wr*wr_weight-normalized_hr*hr_weight)
        score *=2

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


    def make_kid(self):
        # generate empty kid holder
        kids = {'DNA': np.empty((self.n_kid, self.DNA_size))}
        kids['mut_strength'] = np.empty_like(kids['DNA'])

        for kv, ks in zip(kids['DNA'], kids['mut_strength']):
            # crossover (roughly half p1 and half p2)
            p1, p2 = np.random.choice(np.arange(self.pop_size), size=2, replace=False)

            cp = np.random.randint(0, 2, self.DNA_size, dtype=np.bool)  # crossover points
            kv[cp] = self.pop['DNA'][p1, cp]
            kv[~cp] = self.pop['DNA'][p2, ~cp]
            ks[cp] = self.pop['mut_strength'][p1, cp]
            ks[~cp] = self.pop['mut_strength'][p2, ~cp]

            # mutate (change DNA based on normal distribution)
            ks[:] = np.maximum(ks + (np.random.randn(*ks.shape)-0.5), 0.)    # must > 0
            kv += ks * np.random.randn(*kv.shape)
            kv[:] = np.clip(kv, *self.DNA_bound)    # clip the mutated value
        return kids


    def kill_bad(self, kids):
        # put pop and kids together
        for key in ['DNA', 'mut_strength']:
            self.pop[key] = np.vstack((self.pop[key], kids[key]))

        fitness = self.get_fitness(self.pop['DNA'])            # calculate global fitness
        idx = np.arange(self.pop['DNA'].shape[0])
        good_idx = idx[fitness.argsort()][-self.pop_size:]   # selected by fitness ranking (not value)

        for key in ['DNA', 'mut_strength']:
            self.pop[key] = self.pop[key][good_idx]
        return


    def evolve(self):
        kids = self.make_kid()
        self.kill_bad(kids)   # keep some good parent for elitism

        return self.pop["DNA"][-1]
