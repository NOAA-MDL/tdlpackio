#!/usr/bin/env python

from hashlib import sha1
import copy
import numpy as np
import pytdlpack
import sys

oldfile = sys.argv[1]
newfile = sys.argv[2]
print " INPUT FILE: ",oldfile
print "OUTPUT FILE: ",newfile

of = pytdlpack.open(oldfile,mode="r")
nf = pytdlpack.open(newfile,mode="w")

n = 1
while of.lun != -1:
    oldrec = of.read()
    if of.lun == -1: break
    oldrec.unpack()
    newrec = copy.deepcopy(oldrec)
    newrec.pack()
    nf.write(newrec)
    del oldrec
    n+=1

of.close()
nf.close()
