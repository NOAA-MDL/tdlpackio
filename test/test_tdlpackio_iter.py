#!/usr/bin/env python3

import numpy as np
import pdb
import os
import sys

import setuptools
platform = setuptools.distutils.util.get_platform()
build_path = './build/lib.'+platform+'-'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)
sys.path.insert(0,build_path)
import pytdlpack
import TdlpackIO

# ---------------------------------------------------------------------------------------- 
# Point stdout to null
# ---------------------------------------------------------------------------------------- 
fout = open(os.devnull,'w')
sys.stdout = fout

# ---------------------------------------------------------------------------------------- 
# Open vector TDLPACK file; iterate; close
# ---------------------------------------------------------------------------------------- 
f = TdlpackIO.open("sampledata/hre201701.sq")
print(f.dates)
print(f.leadtimes)
f.seek(0)
for rec in f:
    print(f.recordnumber,type(rec),rec.id)
f.close()

# ---------------------------------------------------------------------------------------- 
# Open gridded TDLPACK file; iterate; close
# ---------------------------------------------------------------------------------------- 
f = TdlpackIO.open("sampledata/gfspkd47.2017020100.sq")
print(f.dates)
print(f.leadtimes)
f.seek(0)
for rec in f:
    print(f.recordnumber,type(rec),rec.id)
f.close()

fout.close()
