# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import multiprocessing as mp
import math
import time

np.set_printoptions(edgeitems=20)
np.core.arrayprint._line_width = 280

N_THREAD = mp.cpu_count()
if mp.cpu_count()>=4:
    N_THREAD = mp.cpu_count() -1  # 建议留一个CPU核心避免死机

class GACore(object):
    def __init__(self, pop_size, n_kid, factors, key_factor, init_dna=None):
        self.pop_size = pop_size
        self.n_kid = n_kid
        self.factors = factors
        self.key_factor = key_factor
        self.DNA_bound = [0, 10]
        self.DNA_size = len(self.factors)*2

        if init_dna is None:
            init_dna = np.mean(self.DNA_bound)* abs(np.random.randn(1, self.pop_size, self.DNA_size))[0]
        else:
            init_dna = np.array([init_dna]).repeat(self.pop_size, axis=0)
        # initialize the pop DNA values,
        # initialize the pop mutation strength values
        self.pop = dict(DNA=init_dna,
                        mut_strength=np.random.rand(self.pop_size, self.DNA_size))

        # 编译数据筛选器 用于eval执行
        self._data_filter = self._compile_filter()
        return

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
                print("\rEvaluating: {:>6.2f}% of {:d} DNAs\t\t".format(round(processed_count.value/total*100,2),len(v) ), end="")
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
    def _compile_filter(self):
        factors = self.factors
        filter = "rs["
        for _ in range(len(factors)):
            factor = factors[_]
            filter += " (rs."+factor+" < dna['"+factor+"_u']) & (rs."+factor+" > dna['"+factor+"_d']) & "
        filter += "True ]"
        return filter

    def value_scale(self, x, range_values):        
        return (x - self.DNA_bound[0])/(self.DNA_bound[1]-self.DNA_bound[0]) * (range_values[1] - range_values[0]) + range_values[0]

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
