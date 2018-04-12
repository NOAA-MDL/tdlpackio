#!/usr/bin/env python

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import numpy as np
import pytdlpack
import sys

# ---------------------------------------------------------------------------------------- 
# Process command line arguments
# ---------------------------------------------------------------------------------------- 
if len(sys.argv) != 2:
    print "usage: ",sys.argv[0]," <TDLPACK_Input>"
    exit(1)

# ---------------------------------------------------------------------------------------- 
# Open file
# ---------------------------------------------------------------------------------------- 
fin = pytdlpack.open(sys.argv[1],"r")

# ---------------------------------------------------------------------------------------- 
# Iterate over records in the file.
# ---------------------------------------------------------------------------------------- 
while 1:
    frec = fin.read()
    if fin.lun == -1: break
    n = fin.current_record
    if type(frec) is pytdlpack.TdlpackStations:
        frec.unpack()
        print "%d:%s:%d" % (n,"STATION CALL LETTER RECORD",frec.nsta)
    elif type(frec) is pytdlpack.TdlpackRecord:
        frec.unpack(unpack_data=False)
        print "%d:d=%10d:%.9d %.9d %.9d %.10d:%3d-HR FCST:%32s:%d" % (n,frec.reference_date,
        frec.id[0],frec.id[1],frec.id[2],frec.id[3],frec.leadTime,frec.plain,frec.ioctet)
    elif type(frec) is pytdlpack.TdlpackTrailer:
        print "%d:%s" % (n,"TRAILER RECORD")

# ---------------------------------------------------------------------------------------- 
# Close file
# ---------------------------------------------------------------------------------------- 
fin.close()
