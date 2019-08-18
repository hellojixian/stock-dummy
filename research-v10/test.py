import numpy as np
import scipy.stats

# a=[0.2,0.1,0.3,-0.3,0.1]
# b=[0.1,0.3,-0.3,0.1,0.1]

a=[1,0,0,1,1,1,1,1,1]
b=[0,0,1,1,1,1,1,1,0]

print(np.corrcoef(a,b))
print(scipy.stats.pearsonr(a,b))
