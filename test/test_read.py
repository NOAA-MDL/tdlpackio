#!/usr/bin/env python

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import numpy as np
import sys
sys.path.insert(0,'../build/lib.macosx-10.6-x86_64-2.7')

import pytdlpack

# ---------------------------------------------------------------------------------------- 
# Process command line arguments
# ---------------------------------------------------------------------------------------- 
if len(sys.argv) != 2:
    print "usage: ",sys.argv[0]," <TDLPACK_Input>"
    exit(1)

# ---------------------------------------------------------------------------------------- 
# Iterate over records in the file.
# ---------------------------------------------------------------------------------------- 
fin = pytdlpack.open(sys.argv[1],mode="r")
while True:
    frec = fin.read()
    if fin.eof: break
    n = fin.position
    if type(frec) is pytdlpack.TdlpackStationRecord:
        frec.unpack(data=False)
        print "%d:%s:%d" % (n,"STATION CALL LETTER RECORD",frec.number_of_stations)
    elif type(frec) is pytdlpack.TdlpackRecord:
        frec.unpack(data=True)
        print "%d:d=%10d:%.9d %.9d %.9d %.10d:%3d-HR FCST:%32s:%d" % (n,frec.reference_date,
        frec.id[0],frec.id[1],frec.id[2],frec.id[3],frec.lead,frec.plain,frec.ioctet)
        print "%s%.6f:%s%.6f" % ("MIN=",np.amin(frec.data),"MAX=",np.amax(frec.data))
    elif type(frec) is pytdlpack.TdlpackTrailer:
        print "%d:%s" % (n,"TRAILER RECORD")