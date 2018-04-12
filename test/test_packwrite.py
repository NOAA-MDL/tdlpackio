#!/usr/bin/env python

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import copy
import numpy as np
import pytdlpack
import sys

# ---------------------------------------------------------------------------------------- 
# Get filenames.
# ---------------------------------------------------------------------------------------- 
oldfile = sys.argv[1]
newfile = sys.argv[2]
print " INPUT FILE: ",oldfile
print "OUTPUT FILE: ",newfile

# ---------------------------------------------------------------------------------------- 
# Open files.
# ---------------------------------------------------------------------------------------- 
of = pytdlpack.open(oldfile,mode="r")
nf = pytdlpack.open(newfile,mode="w")

# ---------------------------------------------------------------------------------------- 
# Iterate over the records and handle accordingly.
# ---------------------------------------------------------------------------------------- 
n = 1
while of.lun != -1:
    oldrec = of.read()
    if of.lun == -1: break

    print type(oldrec)
    if type(oldrec) is pytdlpack.TdlpackStations:
        oldrec.unpack()
        newrec = copy.deepcopy(oldrec)
        newrec.pack()
    elif type(oldrec) is pytdlpack.TdlpackRecord:
        oldrec.unpack()
        newrec = copy.deepcopy(oldrec)
        newrec.pack()
    elif type(oldrec) is pytdlpack.TdlpackTrailer:
        newrec = copy.deepcopy(oldrec)

    nf.write(newrec)
    del oldrec

    n+=1

# ---------------------------------------------------------------------------------------- 
# Close files.
# ---------------------------------------------------------------------------------------- 
of.close()
nf.close()
