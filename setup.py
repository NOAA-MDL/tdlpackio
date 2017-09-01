# ---------------------------------------------------------------------------------------- 
# Import modules
# ---------------------------------------------------------------------------------------- 
from numpy.distutils.core import setup, Extension
import os

#GFORTRAN FFLAGS "-O3 -fautomatic -finit-integer=zero -finit-real=zero -fbacktrace"
#INTEL FFLAGS    "-O3 -auto -zero -g -traceback"

# ---------------------------------------------------------------------------------------- 
# Define Extension object
# ---------------------------------------------------------------------------------------- 
ext = Extension(name  = '_tdlpack',
                sources = ['tdlpack/_tdlpack.pyf','tdlpack/bswap.f','tdlpack/ckfilend.f','tdlpack/ckraend.f',
                           'tdlpack/cksysend.f','tdlpack/closefile.f','tdlpack/openfile.f',
                           'tdlpack/pack.f','tdlpack/packgp.f','tdlpack/pkbg.f',
                           'tdlpack/pkc4lx.f','tdlpack/pkms00.f','tdlpack/pkms97.f',
                           'tdlpack/pkms99.f','tdlpack/pks4lx.f','tdlpack/readfile.f',
                           'tdlpack/reduce.f','tdlpack/unpack.f','tdlpack/unpkbg.f',
                           'tdlpack/unpklx.f','tdlpack/unpkoo.f','tdlpack/unpkpo.f',
                           'tdlpack/unpkps.f','tdlpack/writep.f'],
                extra_compile_args = ["-O3"])

# ---------------------------------------------------------------------------------------- 
# Build pytdlpack
# ---------------------------------------------------------------------------------------- 
if __name__ == "__main__":
    setup(name = 'pytdlpack',
          author            = "Eric Engle",
          author_email      = "eric.engle@mac.com",
          url               = "https://github.com/eengl/pytdlpack",
          download_url      = "https://github.com/eengl/pytdlpack/releases",
          version           = "0.1",
          description       = "Python interface for reading and writing TDLPACK data",
          ext_modules       = [ext],
          py_modules        = ['pytdlpack'],
          )
