# pytdlpack

## Introduction

NOAA/NWS Meteorological Development Lab ([MDL](https://www.weather.gov/mdl/)) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  MOS2K uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.

A brief introduction to TDLPACK files and data format can be found [here](TDLPACK.md).

## Motivation

Provide a Python interface for reading and writing TDLPACK files.

## Requirements
* Python 2.7+ (Python 3 support coming soon!)
* NumPy 1.8+
* Fortran compiler ***Only GNU (gfortran) and Intel (ifort) are supported at this time.***

## Installation

### Build

``python setup.py build_ext --fcompiler=[gnu95|intelem] build``

**NOTE for macOS users:** If GNU C compilers are not installed on your system, build via the follwing:

``CC=clang python setup.py build_ext --fcompiler=gnu95 build``

### Install

System area:
``sudo python setup.py install``

Local area:
``python setup.py install --prefix=<INSTALL_DIR>``

You can also build and install using the provided ``install.sh`` script (see its usage print).
