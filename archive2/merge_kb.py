#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This command line tool to will merge all knowledge base files into ./data/knowledge_base.h5
"""
import pandas as pd
import numpy as np
import warnings,sys,os

KB_FILENAME = 'data/knowledge_base.h5'
KB_KEY = 'KnowledgeBase'


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


if not sys.warnoptions:
    warnings.simplefilter("ignore")
from lib.learning_manager import LearningManager as Manager

if len(sys.argv) < 2:
    print("Need to specify the folder to scan.")
    print("   {} [path]\n".format(sys.argv[0]))
    sys.exit(1)
scan_folder = sys.argv[1]

if not os.path.isdir(scan_folder):
    print(scan_folder,"is not a folder.")
    sys.exit(1)

if not os.path.isfile(KB_FILENAME):
    print("Local knowledge file not found.", KB_FILENAME)
    sys.exit(1)

print("Loading local knowledge base...\t\t", end="")
knowledge_base = pd.read_hdf(KB_FILENAME, key=KB_KEY)
print("contains:",knowledge_base.shape[0],'records')

for directory, dirnames, filenames in os.walk(scan_folder,followlinks=False):
    for filename in filenames:
        if filename[-3:]!='.h5': continue
        filepath = os.path.join(directory, filename)
        print("Found knowledge file: {}\t".format(filename), end="")
        new_kb = pd.read_hdf(filepath, key=KB_KEY)
        print("contains: {:d} records".format(new_kb.shape[0]), end="")
        imported_count = 0
        for idx in new_kb.index:
            # check if the new record is better than we had
            if idx in knowledge_base.index and \
                knowledge_base.loc[idx,'win_r']>=new_kb.loc[idx,'win_r']:
                continue # ignore worse records
            knowledge_base.loc[idx]=new_kb.loc[idx]
            imported_count+=1
        print("\t{:d} records is better".format(imported_count))

print("Merged knowledge base size: {:d} records".format(knowledge_base.shape[0]))
knowledge_base.to_hdf(KB_FILENAME, KB_KEY)
print("File saved")
