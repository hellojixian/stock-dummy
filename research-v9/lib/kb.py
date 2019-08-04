#!/usr/bin/env python3

import pandas as pd
import numpy as np
import scipy.stats
import os

KB_FILENAME = "data/knowledge_base.csv"

class KnowledgeBase(object):
    def __init__(self, train_df):
        self.train_df = train_df
        if os.path.isfile(KB_FILENAME):
            self.kb = pd.read_csv(KB_FILENAME)
        else:
            self.kb = pd.DataFrame()
        return

    def need_learn(self, sample, k_type='buy'):
        if len(self.kb)==0: return True
        test_df = pd.DataFrame([sample])
        for i,k in self.kb[self.kb.eval("type=='{}'".format(k_type))].iterrows():
            filter = k['base_filter']
            if test_df[test_df.eval(filter)].shape[0]==1:
                return False
        return True

    def learn(self, sample, k_type='buy'):
        if k_type.lower() == "buy":
            wr_cond = "(buy==1)"
            max_deep = 6
            search_desc = False
        elif k_type.lower() == "sell":
            wr_cond = "(buy==0 | hold==0) & sell==1"
            max_deep = 9
            search_desc = False
        fixed_factor = 'f3d_pos'

        train_df = self.train_df

        wr = train_df[train_df.eval(wr_cond)].shape[0]/train_df.shape[0]*100
        print('default',wr)

        used_factors = [fixed_factor]
        remain_factors = []
        for f in train_df.columns.tolist():
            if f[:1]=='f': remain_factors.append(f)
        remain_factors.remove(fixed_factor)
        filter = " ({} in [{}]) &".format(
                    fixed_factor,sample[fixed_factor])
        dataset = train_df[train_df.eval("{}=={}".format(fixed_factor,sample[fixed_factor]))]
        while len(remain_factors)>0:
            factor_desc = {}
            for factor in remain_factors:
                var = scipy.stats.variation(dataset[factor])
                factor_desc[factor] = var
            factor_desc = sorted(factor_desc.items(), key=lambda kv: kv[1], reverse=search_desc)
            use_factor = factor_desc[0][0]
            used_factors.append(use_factor)

            filter_test = {}
            for offest in [(-2,0),(-1,0),(0,0),(0,1),(-1,1),(0,2)]:
                filter_tmp = ""
                v_range=[]
                for _ in range(sample[use_factor]+offest[0],sample[use_factor]+offest[1]+1):
                    v_range.append(_)
                filter_tmp += " ({} in {}) &".format(
                            use_factor, v_range)
                filter_tmp = filter_tmp[:-1]
                subset = dataset[dataset.eval(filter+filter_tmp)]
                wr = 0
                if subset.shape[0]>0:
                    wr = subset[subset.eval(wr_cond)].shape[0]/subset.shape[0]*100
                filter_test[filter_tmp]=wr
                print("{}:{}\t{}\tAcc: {:.2f}% of {} Samples Corrects:{}".format(
                    len(used_factors),use_factor, str(offest[0])+str(offest[1]), wr,
                        subset.shape[0], subset[subset.eval(wr_cond)].shape[0]))
            filter_test = sorted(filter_test.items(), key=lambda kv: kv[1], reverse=True)
            filter += filter_test[0][0] +" &"
            last_best_wr = filter_test[1][1]
            remain_factors.remove(use_factor)
            base_filter = filter[:-1]
            # deep search on level 5
            if len(used_factors)>=max_deep:
                factor_desc = {}
                for factor in remain_factors:
                    var = scipy.stats.variation(dataset[factor])
                    factor_desc[factor] = var
                factor_desc = sorted(factor_desc.items(), key=lambda kv: kv[1], reverse=search_desc)
                use_factor = factor_desc[0][0]
                used_factors.append(use_factor)
                filter_test = {}
                for r in range(10):
                    filter_tmp = ""
                    filter_tmp += " ({} in [{}]) &".format(
                                use_factor,r)
                    filter_tmp = filter_tmp[:-1]
                    subset = dataset[dataset.eval(filter+filter_tmp)]
                    wr = 0
                    if subset.shape[0]>0:
                        wr = subset[subset.eval(wr_cond)].shape[0]/subset.shape[0]*100

                    print("{}:{}\t{}\tAcc: {:.2f}% of {} Samples Corrects:{}".format(
                        len(used_factors),use_factor, str(offest[0])+str(offest[1]), wr,
                            subset.shape[0], subset[subset.eval(wr_cond)].shape[0]))
                    if wr>=last_best_wr: filter_test[r]=wr
                filter_test = sorted(filter_test.items(), key=lambda kv: kv[1], reverse=True)
                best_range = [x[0] for x in filter_test]


                filter_tmp = " ({} in {})".format(use_factor, best_range)
                filter += filter_tmp
                subset = dataset[dataset.eval(filter)]
                wr = 0
                if subset.shape[0]>0:
                    wr = subset[subset.eval(wr_cond)].shape[0]/subset.shape[0]*100

                print("BEST \tAcc: {:.2f}% of {} Samples Corrects:{}".format(
                    wr,subset.shape[0], subset[subset.eval(wr_cond)].shape[0]))
                k = pd.Series()
                k['type'] = k_type
                k['wr'] = np.round(wr/100,3)
                k['samples'] = subset.shape[0]
                k['filter'] = filter
                k['base_filter'] = base_filter
                self.kb = self.kb.append(k,ignore_index=True)
                print(filter)
                assert(False)
                self.save_kb()
                break

        return filter

    def save_kb(self):
        self.kb.to_csv(KB_FILENAME, index=False)
        # print(self.kb[-5:])
        print("\t\tkb size:",self.kb.shape[0])
        return
