#!/usr/bin/env python3

# ---------------------------------------------------------------------------------------- 
# Import Modules
# ---------------------------------------------------------------------------------------- 
import numpy as np
import setuptools
import sys

platform = setuptools.distutils.util.get_platform()
build_path = './build/lib.'+platform+'-'+str(sys.version_info.major)+'.'+str(sys.version_info.minor)
sys.path.insert(0,build_path)
import pytdlpack

# ---------------------------------------------------------------------------------------- 
# Create some data
# ---------------------------------------------------------------------------------------- 
nx = 2345
ny = 1597
date = 2019052900
id = [4210008,10,24,0]
grid_data = np.random.rand(nx,ny)*75.0
grid_data.fill(np.nan)

# ---------------------------------------------------------------------------------------- 
# Grid Specs: CONUS Lambert-Conformal 2.5km 2345x1597 
# ---------------------------------------------------------------------------------------- 
griddef = pytdlpack.create_grid_definition(proj=3,nx=nx,ny=ny,latll=19.2290,
          lonll=233.7234,orientlon=265.,stdlat=25.,meshlength=2.539703)

# ---------------------------------------------------------------------------------------- 
# Create TDLPACK data record and pack
# ---------------------------------------------------------------------------------------- 
rec = pytdlpack.TdlpackRecord(date=date,id=id,lead=24,plain="GFS WIND SPEED",
                              data=grid_data,missing_value=9999.0,grid=griddef)
rec.pack(dec_scale=3)

# ---------------------------------------------------------------------------------------- 
# Open new sequential file and write the records
# ---------------------------------------------------------------------------------------- 
f = pytdlpack.open('new_grid.sq',mode='w',format='sequential')
f.write(rec)
f.close()

# ---------------------------------------------------------------------------------------- 
# Open new random-access file and write the records
# ---------------------------------------------------------------------------------------- 
fra = pytdlpack.open('new_grid.ra',mode='w',format='random-access',ra_template='large')
fra.write(rec)
fra.close()
