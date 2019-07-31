#!/usr/bin/env python

import TdlpackIO
import numpy as np
import pdb
import os
import sys

import setuptools
platform = setuptools.distutils.util.get_platform()
build_path = './build/lib.'+platform+'-'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)
sys.path.insert(0,build_path)
import pytdlpack

# ---------------------------------------------------------------------------------------- 
# Point stdout to null
# ---------------------------------------------------------------------------------------- 
fout = open(os.devnull,'w')
sys.stdout = fout

# ---------------------------------------------------------------------------------------- 
# Open TDLPACK file
# ---------------------------------------------------------------------------------------- 
f = TdlpackIO.open("../../sampledata/hre201701")
f.seek(0)

# ---------------------------------------------------------------------------------------- 
# Iterate over the file.  This is testing TdlpackIO.open.__iter__ and __next__ methods.
# ---------------------------------------------------------------------------------------- 
for rec in f:
    print(f.recordnumber,type(rec),rec.id)

# ---------------------------------------------------------------------------------------- 
# Close files.
# ---------------------------------------------------------------------------------------- 
f.close()
fout.close()
