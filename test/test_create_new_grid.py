#!/usr/bin/env python

import numpy as np
import sys
sys.path.insert(0,'../build/lib.macosx-10.6-x86_64-2.7')

import pytdlpack

# Create some data
date = 2019052900
id = [4210008,10,24,0]
grid_data = np.zeros((2345,1597),dtype=np.float32,order='F')+10.0

# Grid Specs: CONUS Lambert-Conformal 2.5km 2345x1597 
griddef = pytdlpack.create_grid_definition(proj=3,nx=2345,ny=1597,latll=19.2290,
          lonll=233.7234,orient_lon=265.,std_lat=25.,mesh_length=2.539703)

# Create TDLPACK data record and pack
rec = pytdlpack.TdlpackRecord(date=date,dcf=1,id=id,lead=24,plain="NO CLUE...",data=grid_data,missing_value=9999.0,grid=griddef)
rec.pack()

# Open new sequential file and write the records
f = pytdlpack.open('new_grid.sq',mode='w',format='sequential')
f.write(rec)
f.close()
