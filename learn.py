"""
The Evolution Strategy can be summarized as the following term:
{mu/rho +, lambda}-ES
Here we use following term to find a maximum point.
{n_pop/n_pop + n_kid}-ES
Visit my tutorial website for more: https://morvanzhou.github.io/tutorials/
"""
import numpy as np
import matplotlib.pyplot as plt

TARGET_DNA=[6,9,3,1,8,2,3,1,3,4,2,1,2,3,10,0,10,1,2,2,3,1,3,4]

DNA_SIZE = len(TARGET_DNA)  # DNA (real number)
DNA_BOUND = [0, 10]       # solution upper and lower bounds
N_GENERATIONS = 2000
POP_SIZE = 100           # population size
N_KID = 50               # n kids per generation

np.set_printoptions(edgeitems=10)
np.core.arrayprint._line_width = 180

def F(x): return np.sin(10*x)*x + np.cos(2*x)*x     # to find the maximum of this function


# find non-zero fitness for selection
def get_fitness(pred):     
    v = (np.round(TARGET_DNA,1) == np.round(pred,1)).sum(axis=1)    
    # v = np.sqrt(np.mean(TARGET_DNA - pred, axis=1)**2)
    return v


def make_kid(pop, n_kid):
    # generate empty kid holder
    kids = {'DNA': np.empty((n_kid, DNA_SIZE))}
    kids['mut_strength'] = np.empty_like(kids['DNA'])

    for kv, ks in zip(kids['DNA'], kids['mut_strength']):
        # crossover (roughly half p1 and half p2)        
        p1, p2 = np.random.choice(np.arange(POP_SIZE), size=2, replace=False)
        
        cp = np.random.randint(0, 2, DNA_SIZE, dtype=np.bool)  # crossover points                
        kv[cp] = pop['DNA'][p1, cp]
        kv[~cp] = pop['DNA'][p2, ~cp]
        ks[cp] = pop['mut_strength'][p1, cp]
        ks[~cp] = pop['mut_strength'][p2, ~cp]

        # mutate (change DNA based on normal distribution)
        ks[:] = np.maximum(ks + (np.random.randn(*ks.shape)-0.5), 0.)    # must > 0
        kv += ks * np.random.randn(*kv.shape)
        kv[:] = np.clip(kv, *DNA_BOUND)    # clip the mutated value
    return kids


def kill_bad(pop, kids):
    # put pop and kids together
    for key in ['DNA', 'mut_strength']:
        pop[key] = np.vstack((pop[key], kids[key]))

    fitness = get_fitness(pop['DNA'])            # calculate global fitness
    idx = np.arange(pop['DNA'].shape[0])
    good_idx = idx[fitness.argsort()][-POP_SIZE:]   # selected by fitness ranking (not value)
    for key in ['DNA', 'mut_strength']:
        pop[key] = pop[key][good_idx]
    return pop


pop = dict(DNA=5 * np.random.rand(1, DNA_SIZE).repeat(POP_SIZE, axis=0),   # initialize the pop DNA values
           mut_strength=np.random.rand(POP_SIZE, DNA_SIZE))                # initialize the pop mutation strength values


print("DNA_SIZE:",DNA_SIZE)
# for _ in range(N_GENERATIONS):
i = 0 
while (np.round(pop["DNA"][0],0) == np.round(TARGET_DNA,0)).sum() != DNA_SIZE:
    # ES part    
    kids = make_kid(pop, N_KID)
    pop = kill_bad(pop, kids)   # keep some good parent for elitism
    print("\r G:",i,np.round(pop["DNA"][0],0)," "*100, end="")
    i+=1
    
print("\r\n")
