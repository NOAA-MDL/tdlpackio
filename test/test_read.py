#!/usr/bin/env python

import pytdlpack
import sys

if len(sys.argv) == 1:
    print "usage: ",sys.argv[0]," <TDLPACK_Input>"
    exit(1)

fin = pytdlpack.open(sys.argv[1],"r")

i=1
while fin.lun != -1:
    x=fin.read()
    if type(x) is pytdlpack.TdlpackRecord:
        print i,"TDLPACK RECORD"
        x.unpack()
        print x
    elif type(x) is pytdlpack.TdlpackStations:
        print i,"STATION CALL LETTER RECORD"
    elif type(x) is pytdlpack.TdlpackTrailer:
        print i,"TRAILER RECORD"
    i+=1

fin.close()
