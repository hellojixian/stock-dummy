import time
import progressbar

for i in progressbar.progressbar(range(100), redirect_stdout=True):
    # print('Some text', i)
    time.sleep(0.1)
