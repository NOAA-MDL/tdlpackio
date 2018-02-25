#!/usr/bin/env python

import pytdlpack
import sys

fin = pytdlpack.open(sys.argv[1],"r")
fout = pytdlpack.open(sys.argv[2],"w")
print "INPUT FILE UNIT NUMBER = ",fin.lun
print "OUTPUT FILE UNIT NUMBER = ",fout.lun

while fin.lun != -1:
    x=fin.read()
    if type(x) is pytdlpack.TdlpackRecord: print x.reference_date,x.id
    if type(x) is pytdlpack.TdlpackStations: print x.nsta
    fout.write(x)

fin.close()
fout.close()
