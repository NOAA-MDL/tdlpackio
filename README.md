# tdlpackio

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![PyPI version](https://badge.fury.io/py/tdlpackio.svg)](https://badge.fury.io/py/tdlpackio)

## Introduction

tdlpackio provides a Python interface for reading and writing TDLPACK files. NOAA/NWS Meteorological Development Lab ([MDL](https://www.weather.gov/mdl/)) produces [Model Output Statistics (MOS)](https://vlab.noaa.gov/web/mdl/mos) and the [National Blend of Models (NBM)](https://vlab.noaa.gov/web/mdl/nbm). These products are generated from the MDL's in-house MOS-2000 Software System (MOS2K). The MOS2K system defines a GRIB-like data format called TDLPACK.  A brief introduction to TDLPACK files and data format can be found [here](TDLPACK.md). tdlpackio contains a NumPy/F2PY extension module, tdlpacklib, which is contains Fortran subroutines for TDLPACK I/O and unpacking/packing subroutines.  These are a subset of of the MOS2K system.

## Requirements
* Python 3.8+
* setuptools
* NumPy
* Fortran compiler: GNU (gfortran) and Intel (ifort) have been tested.

## Installation

```shell
pip install tdlpackio
```

### Build and Install from Source

```shell
python setup.py build --fcompiler=[gnu95|intelem]
python setup.py install [--user |--prefix=PREFIX]
```
