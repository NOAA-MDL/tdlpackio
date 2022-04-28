# pytdlpack

[![Build Status](https://app.travis-ci.com/eengl/pytdlpack.svg?branch=master)](https://app.travis-ci.com/eengl/pytdlpack)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![PyPI version](https://badge.fury.io/py/pytdlpack.svg)](https://badge.fury.io/py/pytdlpack)

## Introduction

NOAA/NWS Meteorological Development Lab ([MDL](https://www.weather.gov/mdl/)) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  MOS2K uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.  A brief introduction to TDLPACK files and data format can be found [here](TDLPACK.md).

## Motivation

Provide a Python interface for reading and writing TDLPACK files.

## Requirements
* Python 3.6+
* setuptools 34.0+
* NumPy 1.12+
* GNU or Intel Fortran compiler

## Installation

```shell
pip3 install pytdlpack
```

### Build and Install from Source

```shell
python3 setup.py build_ext --fcompiler=[gnu95|intelem] build
python3 setup.py install [--user |--prefix=PREFIX]
```
## Modules

The pytdlpack package contains 2 modules.  See the docstrings for usage of each module

### pytdlpack

```python
import pytdlpack
```

### TdlpackIO

```python
import TdlpackIO
```
**IMPORTANT:** ```TdlpackIO``` is **experimental** and it usage and functionality could change with future releases.  TdlpackIO is a pure python implementation for reading TDLPACK "sequential" files (i.e. Fortran variable-length record binary files).  Currently, it does not read TDLPACK random-access files and it may never have that capability.  It requires ```pytdlpack``` for unpacking records.
