# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import h5py, os
import time, datetime #用于性能监控 查看耗时

from lib.learner.long_mp import Learner as LearnerL

SAMPLE_CHANGE_PRECENT = 2.5
MIN_CHANGE_EXPECTATION = 0.5

EARLY_STOPPING = 10
GA_POPSIZE = 100
GA_N_KID = 350
N_GENERATIONS = 200
MIN_GENERATIONS = 50

KB_FILENAME = 'data/knowledge_base.h5'
KB_KEY = 'KnowledgeBase'

class LearningManager(object):

    def __init__(self, train_set, validation_set, key_factor):
        self.key_factor = key_factor
        self.train_set = train_set
        self.validation_set = validation_set
        self.knowledge_base = pd.DataFrame()
        self.long_set  = train_set[train_set.fu_c1> SAMPLE_CHANGE_PRECENT].sort_values(by=[self.key_factor],ascending=False)
        self.short_set = train_set[train_set.fu_c1<-SAMPLE_CHANGE_PRECENT].sort_values(by=[self.key_factor],ascending=True)

        if os.path.isfile(KB_FILENAME):
            self.knowledge_base = pd.read_hdf(KB_FILENAME, key=KB_KEY)

        print("KnowledgeBase:\t{:d} records".format(self.knowledge_base.shape[0]))
        print("Train Set:\t{:d} records".format(self.train_set.shape[0]))
        print("Validation Set:\t{:d} records".format(self.validation_set.shape[0]))
        return

    def learn(self, sample_id, sample):
        print("SampleID:\t",sample_id)
        improving_stuck_count,last_score = 0,0

        # 尝试调取上次的学习记录 继续进化
        init_dna, init_generation = self.get_init_dna(sample_id)

        ga = LearnerL(DNA_sample=sample, pop_size=GA_POPSIZE, n_kid=GA_N_KID,
                      train_set=self.train_set, validation_set=self.validation_set,
                      key_factor=self.key_factor, init_dna=init_dna, min_exp=0.75)

        for generation_id in range(N_GENERATIONS):
            timestamp = time.time()
            real_generation_id = int(init_generation + generation_id + 1)
            if real_generation_id>=N_GENERATIONS:
                break

            print("")
            best_dna = ga.evolve()
            evaluation_train = ga.evaluate_dna(best_dna, deep_eval=True, dataset="train")
            evaluation_val   = ga.evaluate_dna(best_dna, deep_eval=True, dataset="validation", min_exp=0)
            durtion = int((time.time() - timestamp))

            print("Gen:",real_generation_id,"\tDuration:",str(durtion)+"s")
            self._print_report(evaluation_train, name="Training Set")
            self._print_report(evaluation_val, name="Validation Set")

            if evaluation_val['score'] <= last_score:
                improving_stuck_count+=1
            else:
                improving_stuck_count=0
                # 有进步就去记录存盘
                knowledge = {
                    'dna': best_dna,
                    'sample': sample,
                    'knowledge': ga.translateDNA(best_dna),
                    'evaluation': evaluation_train,
                    'generation': real_generation_id,
                    'key_factor': self.key_factor
                }
                self.save_result(sample_id, knowledge)
                print("[ saved ]")
                last_score = evaluation_val['score']

            if improving_stuck_count>=EARLY_STOPPING:
                print("EARLY_STOPPING")
                improving_stuck_count=0
                break
        return

    def save_result(self, sample_id, knowledge):
        for k in knowledge['evaluation']:
            knowledge[k]=knowledge['evaluation'][k]
        del knowledge['evaluation']
        knowledge['timestamp'] = time.time()
        knowledge = pd.Series(knowledge)
        knowledge.name = sample_id
        if sample_id in self.knowledge_base.index:
            self.knowledge_base.loc[sample_id] = knowledge
        else:
            self.knowledge_base = self.knowledge_base.append(knowledge)

        self.knowledge_base.to_hdf(KB_FILENAME, KB_KEY)
        return

    def get_init_dna(self, sample_id):
        if sample_id in self.knowledge_base.index:
            res= self.knowledge_base.loc[sample_id,['dna','generation']].values
            print("DNA SampleID [",sample_id,"] needs continue learning from Gen:", int(res[1]))
            return res[0],res[1]
        return None,0

    def need_learn(self, sample_id, sample):
        # 如果在已有的知识库里匹配了这个规则 那么返回False
        if sample_id in self.knowledge_base.index:
            k = self.knowledge_base.loc[sample_id]
            if k['generation'] <= MIN_GENERATIONS:
                return True  #如果知识库中虽然有 但是进化代数不够也要继续学习
            else:
                return False
        return True

    def start_learning(self, how='full'):
        if how=='full':
            self._full_sample()
        elif how=='random':
            self._random_pick_sample()
        elif how=='improve':
            self._improve_knowledge()
        else:
            print("Unknown learning mode")
        return

    def _print_report(self, evaluation, name=""):
        print(
            'name:', name, \
            '\tscore:', round(evaluation['score'],4),\
            '\thits:',round(evaluation['hits']),'/',round(evaluation['hits_r'],4),\
            '\twin_r:',round(evaluation['win_r'],3),\
            '\twin:',round(evaluation['mean_win'],2),'/',round(evaluation['max_win'],2),\
            '\trisk:',round(evaluation['mean_risk'],2),'/',round(evaluation['max_risk'],2),\
            '\tprofit:', round(evaluation['profit'],3),\
            " "*5,)
        return

    # 从已有知识库中提取并增强
    def _improve_knowledge(self):
        print("Learning Mode:\t","Improve")
        while True:
            rec = self.knowledge_base.sample(1)
            sample_id = rec.index[0]
            sample = rec['sample'][0]
            self.learn(sample_id, sample)
        return

    # 随机挑选样本
    def _random_pick_sample(self):
        print("Learning Mode:\t","Random Sample")
        while True:
            rec = self.train_set.sample(1)
            sample_id = rec.index[0]
            sample = rec.iloc[0]
            # 判断是否需要学习
            if self.need_learn(sample_id, sample):
                self.learn(sample_id, sample)
        return

    # 按时间顺序学习
    def _full_sample(self):
        print("Learning Mode:\t","Full Sample")
        days = self.train_set['date'].value_counts().index.sort_values()
        for trade_date in days:
            df = self.long_set[self.long_set.date==trade_date]
            # 取样逻辑
            for sample_id, sample in df.iterrows():
                # 判断是否需要学习
                if self.need_learn(sample_id, sample):
                    # 从样本中学习
                    self.learn(sample_id, sample)
        return
