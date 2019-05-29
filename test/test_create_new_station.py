#!/usr/bin/env python

import sys
sys.path.insert(0,'../build/lib.macosx-10.6-x86_64-2.7')

import pytdlpack

# Create some data
date = 2019052900
id = [4210008,10,24,0]
station_name = ('KACY','KBWI','KDCA','KIAD','KPHL')
station_data = [10.3,12.4,15.6,8.6,9999.0]

# Create station record and pack
sta = pytdlpack.TdlpackStationRecord(ccall=station_name)
sta.pack()

# Create TDLPACK data record and pack
rec = pytdlpack.TdlpackRecord(date=date,dcf=1,id=id,lead=24,plain="NO CLUE...",data=station_data,missing_value=9999.0)
rec.pack()

# Open new sequential file and write the records
f = pytdlpack.open('new.sq',mode='w',format='sequential')
f.write(sta)
f.write(rec)
f.close()
