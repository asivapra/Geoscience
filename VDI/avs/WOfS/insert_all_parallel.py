#!/bin/env python
# Created by AV Sivaprasad on Jun 08, 2018
# Last modified by AV Sivaprasad on Jun 08,2018
# ----------------------------------------------------------
# This script reads in the NetCDF datasets in the specified directory and
# adds them to the 'wofs_confidence' database.
# Pre-requisite: Add the following definitions into the database once
# 1. Product definitions
# 2. Dataset definitions
# ----------------------------------------------------------
import sys
import os
from subprocess import Popen, PIPE
import re
import multiprocessing
import time
from multiprocessing import Pool

np = 16 # Number of workers spawned each iteration
j = 0   # Count of the sets of np processes. 
#path = '/g/data/u46/wofs/confidence_albers/MrVBF/tiles/'
#log_file = 'log_file.txt'
# Input file is the list of all datasets. It is mandatory.
try:
    path = sys.argv[1]
    match = re.match( r'(/$)', path, re.M|re.I)
    if(match): pass
    else:
        path += "/"
except:
    print("Usage: ./insert_all_parallel.py Path")
    print("Default Path: /g/data/u46/wofs/confidence_albers/MrVBF/tiles/")
#        sys.exit()
    path = '/g/data/u46/wofs/confidence_albers/MrVBF/tiles/'
try:
    limit = int(sys.argv[2])
except:
    limit = 32 # Used only for debugging.

#-------------------------------------------------------------------------------
# Function to be spawned as workers
#-------------------------------------------------------------------------------
def f(item):
    global j
    match = re.match( r'(.*\.nc$)', item, re.M|re.I)
    if(match):
        j += 1
        dataset = path + match.group()
        echo_line = "{}. Adding {}:".format(j,dataset)
        print(echo_line)
        process = Popen(["datacube", "-E", "confidence", "dataset", "add", dataset], stdout=PIPE)
        time.sleep(15) # make this wait long enough to finish the datacube processing
    else:
        dataset = item
        echo_line = "{}. ******* Not Adding {}:".format(j,dataset)
        print(echo_line)

if __name__ == '__main__':
    pool = Pool(processes=np)              # start $np worker processes. It is the optimum
    print("Dir: {}; Limit: {}".format(path,limit))
    files = os.listdir(path)
    print(len(files))
    print (pool.map(f, files)) # Send $np files each time until the full set         
#    pool.map(f, files[:limit]) # Send $np files each time until the set limit         
    print("Finished !")    
	
	    
	    
