# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import h5py, os
import time, datetime #用于性能监控 查看耗时

from lib.learner.long_mp import Learner as LearnerL
from lib.learner.long_l2short_mp import Learner as LearnerL2S

MAX_CHANGE_EXPECTATION = 0

EARLY_STOPPING = 6
GA_POPSIZE = 50
GA_N_KID = 800
N_GENERATIONS = 200
MIN_GENERATIONS = 50

KB_FILENAME = 'data/knowledge_base.h5'
KB_KEY = 'KnowledgeBase'

class L2LearningManager(object):

    def __init__(self, base_knowledge, train_set, validation_set, key_factor, filter_set=[]):
        self.key_factor = key_factor
        self.train_set = train_set
        self.validation_set = validation_set
        self.base_knowledge = base_knowledge
        self.filter_set = filter_set
        return

    def save_result(self, sample_id, knowledge):
        print('TODO it later')
        return

    def filter_data(self,knowledge,dataset):
        rs = dataset
        filter = "dataset["
        for factor in knowledge.keys():
            if factor[-2:]=="_d" :operator = ">"
            if factor[-2:]=="_u": operator = "<"
            filter += " (dataset."+factor[:-2]+" "+operator+" knowledge['"+factor+"']) & "
        filter += "True ]"
        return eval(filter)

    def learning(self, train_subset, validation_subset=None):
        adjust_count,improving_stuck_count,last_score = 0,0,0
        ga = LearnerL2S(base_knowledge=self.base_knowledge,
                        train_set=train_subset,
                        validation_set=validation_subset,
                        pop_size=GA_POPSIZE, n_kid=GA_N_KID,
                        key_factor=self.key_factor, max_exp=MAX_CHANGE_EXPECTATION)

        init_generation = 0
        for generation_id in range(N_GENERATIONS):
            timestamp = time.time()
            real_generation_id = int(init_generation + generation_id + 1)
            if real_generation_id>=N_GENERATIONS:
                break

            print("")
            best_dna = ga.evolve()
            evaluation_train = ga.evaluate_dna(best_dna, deep_eval=True, dataset="train")
            evaluation_val   = ga.evaluate_dna(best_dna, deep_eval=True, dataset="validation", max_exp=MAX_CHANGE_EXPECTATION)
            durtion = int((time.time() - timestamp))

            print("Gen:",real_generation_id,"\tDuration:",str(durtion)+"s")
            self._print_report(evaluation_train, name="Training Set")
            self._print_report(evaluation_val, name="Validation Set")

        return

    def start_learning(self):
        # cut data slice by base knowledge
        train_subset = self.filter_data(knowledge=self.base_knowledge,dataset=self.train_set)
        validation_subset = self.filter_data(knowledge=self.base_knowledge,dataset=self.validation_set)

        print(train_subset.shape,validation_subset.shape)
        if self.need_learn():
            self.learning(train_subset, validation_subset)
        return

    def evalute_filterset(self):
        return

    def need_learn(self):
        # 观察切分之后的子集和原始集的正确率对比 如果错误率过高就需要继续学习
        return True

    def _print_report(self, evaluation, name=""):
        print(
            'name:', name, \
            '\tscore:', round(evaluation['score'],4),\
            '\thits:',round(evaluation['hits']),'/',round(evaluation['hits_r'],4),\
            '\twin_r:',round(evaluation['win_r'],3),\
            '\twin:',round(evaluation['mean_win'],2),'/',round(evaluation['max_win'],2),\
            '\trisk:',round(evaluation['mean_risk'],2),'/',round(evaluation['max_risk'],2),\
            " "*5,)
        return
