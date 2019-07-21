import numpy as np
import pandas as pd
# import modin.pandas as pd
import math

np.set_printoptions(edgeitems=20)
np.core.arrayprint._line_width = 280

EVALUATION_FACTOR = 'fu_c1'

def min_max_range(x, range_values):
    return [round( ((xx - min(x)) / (1.0*(max(x) - min(x)))) * (range_values[1] - range_values[0]) + range_values[0], 2) for xx in x]

class Learner(object):

    def __init__(self, DNA_sample, dataset, pop_size, n_kid, init_dna=None):
        
        self.dataset = dataset.sort_values(by='date', ascending=True)
        self.factors = dataset.columns.drop(['security','date','fu_c1','fu_c2', 'fu_c3', 'fu_c4']).values
        self.DNA_sample = DNA_sample
        self.DNA_size = len(self.factors)*2       
        self.DNA_bound = [0, 10]
        self.pop_size = pop_size
        self.n_kid = n_kid

        if init_dna==None:
            init_dna = 5* abs(np.random.randn(1, self.pop_size, self.DNA_size))[0]

        self.pop = dict(DNA=init_dna,         # initialize the pop DNA values,   
                        mut_strength=np.random.rand(self.pop_size, self.DNA_size))               # initialize the pop mutation strength values

        # 添加评估标准 用于连乘
        self.dataset['_evaluate'] = self.dataset[EVALUATION_FACTOR]/100 + 1

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

    # find non-zero fitness for selection
    def get_fitness(self, dna_series):         
        v=np.array([])
        for i in range(len(dna_series)):            
            score = self.evaluate_dna(dna_series[i])['score']
            v=np.append(v,score)            
            print('\rEvaluating: '+str(round(i/(len(dna_series)-1)*100,2))+"%"+" of "+str(len(dna_series))+" DNA samples" + (" "*6),end='')
        return v

    def evaluate_dna(self, dna):
        dna = self.translateDNA(dna)
        rs = self.dataset
        # 筛选
        for _ in range(len(self.factors)):
            factor = self.factors[_]
            rs = rs[ (rs[factor] < dna[factor+'_u']) & (rs[factor] > dna[factor+'_d'])]                
        
        # 评估
        profit = np.prod(rs['_evaluate'])
        score,win_r,max_risk,mean_risk,mean_win = 0,0,0,0,0
        hits = len(rs)
        wins = rs[EVALUATION_FACTOR][rs[EVALUATION_FACTOR]>=0]
        risks = rs[EVALUATION_FACTOR][rs[EVALUATION_FACTOR]<0]
        mean_win = wins.mean()
        if len(risks)>0:
            max_risk = risks.quantile(0.1)
            mean_risk = risks.quantile(0.5)

        if hits>=3:
            win_r = len(rs[rs._evaluate>=1]) / hits
            score = math.log(hits) * math.tanh(win_r-0.35) 
        return {
            "score": score,
            "profit": profit,
            "hits":  hits,
            "win_r": win_r,
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



