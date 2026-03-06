#!/usr/bin/env python3

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import sys

import setuptools
platform = setuptools.distutils.util.get_platform()
build_path = './build/lib.'+platform+'-'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)
sys.path.insert(0,build_path)
import pytdlpack

# ---------------------------------------------------------------------------------------- 
# Create some data
# ---------------------------------------------------------------------------------------- 
date = 2019052900
id = [4210008,10,24,0]
station_name = ('KACY','KBWI','KDCA','KIAD','KPHL')
station_data = [10.3,12.4,15.6,8.6,9999.0]

# ---------------------------------------------------------------------------------------- 
# Create station record and pack
# ---------------------------------------------------------------------------------------- 
sta = pytdlpack.TdlpackStationRecord(station_name)
sta.pack()

# ---------------------------------------------------------------------------------------- 
# Create TDLPACK data record and pack
# ---------------------------------------------------------------------------------------- 
rec = pytdlpack.TdlpackRecord(date=date,id=id,lead=24,plain="GFS WIND SPEED",
                              data=station_data,missing_value=9999.0)
rec.pack(dec_scale=1)

# ---------------------------------------------------------------------------------------- 
# Open new sequential file and write the records
# ---------------------------------------------------------------------------------------- 
f = pytdlpack.open('new_station.sq',mode='w',format='sequential')
f.write(sta)
f.write(rec)
f.write(pytdlpack.TdlpackTrailerRecord())
f.close()
