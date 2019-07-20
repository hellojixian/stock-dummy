"""
The Evolution Strategy can be summarized as the following term:
{mu/rho +, lambda}-ES
Here we use following term to find a maximum point.
{n_pop/n_pop + n_kid}-ES
Visit my tutorial website for more: https://morvanzhou.github.io/tutorials/
"""
import numpy as np
import matplotlib.pyplot as plt


np.set_printoptions(edgeitems=20)
np.core.arrayprint._line_width = 280

N_GENERATIONS = 2000
TARGET_DNA = [6,9,3,1,8,2,3,1,3,4,2,1,2,3,10,0,10,1,2,2,3,1,3,4,1,2,2,3]

class Learner(object):

    def __init__(self, pop_size, n_kid):
        self.TARGET_DNA = TARGET_DNA
        self.DNA_size = len(self.TARGET_DNA)        
        self.DNA_bound = [0, 10]
        self.pop_size = pop_size
        self.n_kid = n_kid
        

        self.pop = dict(DNA=5 * np.random.rand(1, self.DNA_size).repeat(self.pop_size, axis=0),   # initialize the pop DNA values
                        mut_strength=np.random.rand(self.pop_size, self.DNA_size))                # initialize the pop mutation strength values

    # find non-zero fitness for selection
    def get_fitness(self, pred):     
        v = (np.round(self.TARGET_DNA,1) == np.round(pred,1)).sum(axis=1)    
        return v


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
        return self.pop


    def evolve(self):
        kids = self.make_kid()
        self.kill_bad(kids)   # keep some good parent for elitism            
        return np.round(self.pop["DNA"][0],0)


if __name__ == '__main__':
    ga = Learner(pop_size=400, n_kid=150)
    i = 0 
    for _ in range(N_GENERATIONS):
        dna = ga.evolve()        
        print("\r G:",i,dna," "*10, end="")
        if (dna == np.round(TARGET_DNA,0)).sum() == len(dna): break
        i+=1        
print("\r\n")
