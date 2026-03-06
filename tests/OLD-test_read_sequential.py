#!/usr/bin/env python3

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import copy
import filecmp
import numpy as np
import setuptools
import sys

platform = setuptools.distutils.util.get_platform()
build_path = './build/lib.'+platform+'-'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)
sys.path.insert(0,build_path)
import pytdlpack

file_input = "sampledata/gfspkd47.2017020100.sq"
file_output = "test.sq"

f = pytdlpack.open(file_input)
fout = pytdlpack.open(file_output,mode="w")
recs = f.read(all=True)
for r in recs:
   r.unpack()
   newrec = copy.deepcopy(r)
   newrec.pack()
   fout.write(newrec)

f.close()
fout.close()

filecompare = filecmp.cmp(file_input,file_output)
print("filecmp result:",filecompare)
