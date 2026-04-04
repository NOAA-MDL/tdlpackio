# tdlpackio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/release/python-3140/)

![Build Linux](https://github.com/NOAA-MDL/tdlpackio/actions/workflows/build_linux.yml/badge.svg)
![Build macOS](https://github.com/NOAA-MDL/tdlpackio/actions/workflows/build_macos.yml/badge.svg)

![PyPI](https://img.shields.io/pypi/v/tdlpackio?label=pypi%20package)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tdlpackio)

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/tdlpackio/badges/version.svg)](https://anaconda.org/conda-forge/tdlpackio)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/tdlpackio/badges/platforms.svg)](https://anaconda.org/conda-forge/tdlpackio)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/tdlpackio/badges/downloads.svg)](https://anaconda.org/conda-forge/tdlpackio)

## Introduction

tdlpackio provides a Python interface for reading and writing TDLPACK files. The NOAA/NWS Meteorological Development Lab ([MDL](https://www.weather.gov/mdl/)) produces [Model Output Statistics (MOS)](https://vlab.noaa.gov/web/mdl/mos) and the [National Blend of Models (NBM)](https://vlab.noaa.gov/web/mdl/nbm). These products are generated from the MDL's in-house MOS-2000 Software System (MOS2K). The MOS2K system defines a GRIB-like data format called TDLPACK.  A brief introduction to TDLPACK files and data format can be found [here](TDLPACK.md). tdlpackio provides a Cython extension module, tdlpacklib, which provides an interface to [libtdlpack](https://github.com/NOAA-MDL/libtdlpack), a Fortran-based library containing a subset of MOS2K subroutines.

## Requirements
* Python 3.10, 3.11, 3.12, 3.13, 3.14
* [libtdlpack](https://github.com/NOAA-MDL/libtdlpack) 1.0.0+
* setuptools
* cython 3.0+
* numpy 1.26+
* pyproj 1.9.6+
* C compiler: GNU, Intel, and Apple Clang have been tested.

## Required External Libraries

### libtdlpack
The [libtdlpack](https://github.com/NOAA-MDL/libtdlpack) library is required for tdlpackio.  You will have to build and install this yourself, but this is not difficult.  For macOS users, libtdlpack can be installed via [this Homebrew Tap](https://github.com/NOAA-MDL/homebrew-mdllibs).  If you use the *conda ecosystems, then you can install via `conda install -c conda-forge libtdlpack`.

## Install

Once again, this assumes that libtdlpack has been installed.  If libtdlpack has been installed into a "common" installation path, then it will be found, otherwise define environment variable `TDLPACK_DIR` with the installation path.

* From [PyPI](https://pypi.python.org/pypi/tdlpackio) via pip:

```
pip install tdlpackio
```
* From [conda-forge](https://anaconda.org/conda-forge/tdlpackio) via conda:

```
conda install -c conda-forge tdlpackio
```

* From source:
```shell
pip install .
```

## Development

The development evolution of tdlpackio will mainly focus on how best to serve that purpose and its primary user's -- mainly meteorologists, physical scientists, and software developers supporting the missions within NOAA's National Weather Service (NWS) and National Centers for Environmental Prediction (NCEP), and other NOAA organizations.

## Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.
