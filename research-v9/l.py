import numpy as np
import scipy.stats
t1=np.random.normal(0,7,1000)
t2=np.random.normal(0,3,1000)
t1=np.round(t1,2)
t2=np.round(t2,2)


# print(t1)
t1 = [0,1,2,3,4,5,6,7]

print(scipy.stats.variation(t1))

t2 = [0,1,7,3,7,5,7,7]
print(scipy.stats.variation(t2))

t3 = [7,1,7,7,7,7,7,7]
print(scipy.stats.variation(t3))

print("{:.3e}".format(100000000000))
