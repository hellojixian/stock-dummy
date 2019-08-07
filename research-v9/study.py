import numpy as np
import scipy as sp
import scipy.stats as stats
a = np.random.normal(size=1000)
loc, std = stats.norm.fit(a)
print(loc, std)

import numpy as np
#从fftpack中导入fft(快速傅里叶变化)和ifft(快速傅里叶逆变换)函数
from scipy.fftpack import fft,ifft

#创建一个随机值数组
x = np.array([1.0, 2.0, 1.0, -1.0, 1.5])

#对数组数据进行傅里叶变换
y = fft(x)
print('fft: ')
print(y)
print('\n')
