import numpy as np
import pandas as pd
import sys,os,datetime,gc

print("merging")
knowledge_base_filename = "knowledge_base.csv"
knowledge_base = pd.DataFrame()
scan_folder = "data/"

for directory, dirnames, filenames in os.walk(scan_folder,followlinks=False):
    for filename in filenames:
        if filename[:len(knowledge_base_filename)]!=knowledge_base_filename: continue
        ds = pd.read_csv(scan_folder+filename,index_col=0)
        knowledge_base = knowledge_base.append(ds)
        del ds
        gc.collect()
        print("merged slice ", filename)

knowledge_base.to_csv(scan_folder+knowledge_base_filename)
print("all saved")
del knowledge_base
gc.collect()
print("clean up")
for directory, dirnames, filenames in os.walk(scan_folder,followlinks=False):
    for filename in filenames:
        if filename[len(knowledge_base_filename)-1:]!=knowledge_base_filename: continue
        os.remove(scan_folder+filename)
print("all done")
