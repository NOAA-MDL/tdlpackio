#!/usr/bin/env python

import numpy as np
import pytdlpack
import sys

file1 = sys.argv[1]
file2 = sys.argv[2]
print " INPUT FILE 1: ",file1
print " INPUT FILE 2: ",file2

fo1 = pytdlpack.open(file1,mode="r")
fo2 = pytdlpack.open(file2,mode="r")

rec1 = fo1.read()
rec2 = fo2.read()

rec1.unpack()
rec2.unpack()

print "COMPARE IS0: ",np.array_equal(rec1.is0,rec2.is0)
print "COMPARE IS1: ",np.array_equal(rec1.is1,rec2.is1)
print "COMPARE IS2: ",np.array_equal(rec1.is2,rec2.is2)
print "COMPARE IS4: ",np.array_equal(rec1.is4,rec2.is4)
print "COMPARE DATA: ",np.array_equal(rec1.data,rec2.data)

for old,new in np.nditer([rec1.data,rec2.data],order='F'):
    print old,new

fo1.close()
fo2.close()
