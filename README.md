# pytdlpack

## Introduction

NOAA/NWS Meteorological Development Lab ([MDL](https://www.weather.gov/mdl/)) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  MOS2K uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.

A brief introduction to TDLPACK files and data format can be found [here](TDLPACK.md).

## Motivation

Provide a Python interface for reading and writing TDLPACK files.

## Requirements
* Fortran compiler supported by f2py (GNU Fortran or Intel Fortran preferred)
* Python 2.6+
* NumPy 1.8+

## Build and Installation

Note that building on macOS requires setting ``CC=clang``. Python setuptools and f2py seems to have trouble using the GNU C compiler on macOS.

### Build
* macOS: ``CC=clang python setup.py build_ext --fcompiler=gnu95 build``
* Linux: ``python setup.py build_ext --fcompiler=[gnu95|intelem] build``

### Install

System area:
* ``sudo python setup.py install``

Local area:
* ``python setup.py install --prefix=<INSTALL_DIR>``

You can also build and install using the provided ``install.sh`` script (see its usage print).
