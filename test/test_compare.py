#!/usr/bin/env python

# ---------------------------------------------------------------------------------------- 
# Import modules
# ---------------------------------------------------------------------------------------- 
import numpy as np
import pytdlpack
import sys

# ---------------------------------------------------------------------------------------- 
# Get file names
# ---------------------------------------------------------------------------------------- 
file1 = sys.argv[1]
file2 = sys.argv[2]
print "INPUT FILE 1: ",file1
print "INPUT FILE 2: ",file2

# ---------------------------------------------------------------------------------------- 
# Open both input files.
# ---------------------------------------------------------------------------------------- 
fo1 = pytdlpack.open(file1,mode="r")
fo2 = pytdlpack.open(file2,mode="r")

# ---------------------------------------------------------------------------------------- 
# Read records and compare.  NOTE:  Assumes that these files are a copy of eachother.
# ---------------------------------------------------------------------------------------- 
while 1:

    rec1 = fo1.read()
    rec2 = fo2.read()
    n = fo1.current_record

    if fo1.lun == -1 and fo2.lun == -1: break

    rec1.unpack()
    rec2.unpack()

    print "RECORD NUMBER = ",n

    if type(rec1) is pytdlpack.TdlpackStations and \
       type(rec2) is pytdlpack.TdlpackStations:

        # Compare Station Call Letter Records.
        print "\tCOMPARE NSTA: ",(rec1.nsta==rec2.nsta)
        print "\tCOMPARE STATIONS: ",np.array_equal(rec1.ccall,rec2.ccall)

    elif type(rec1) is pytdlpack.TdlpackRecord and \
         type(rec2) is pytdlpack.TdlpackRecord:

        # Compare TDLPACK Sections and data.
        print "\tCOMPARE IS0: ",np.array_equal(rec1.is0,rec2.is0)
        print "\tCOMPARE IS1: ",np.array_equal(rec1.is1,rec2.is1)
        print "\tCOMPARE IS2: ",np.array_equal(rec1.is2,rec2.is2)
        print "\tCOMPARE IS4: ",np.array_equal(rec1.is4,rec2.is4)
        print "\tCOMPARE DATA: ",np.array_equal(rec1.data,rec2.data)

    elif type(rec1) is pytdlpack.TdlpackTrailer and \
         type(rec2) is pytdlpack.TdlpackTrailer:

       pass

# ---------------------------------------------------------------------------------------- 
# Close files.
# ---------------------------------------------------------------------------------------- 
fo1.close()
fo2.close()
