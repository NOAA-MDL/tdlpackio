#!/usr/bin/env python3

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import numpy as np
import setuptools
import sys

platform = setuptools.distutils.util.get_platform()
build_path = './build/lib.'+platform+'-'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)
sys.path.insert(0,build_path)
import pytdlpack

f = pytdlpack.open('sampledata/blend.analysisgrconst.co.ra')
recs = f.read(all=True)
for r in recs:
   r.unpack(data=True)

f.close()
