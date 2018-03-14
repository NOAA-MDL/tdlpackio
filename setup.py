# ---------------------------------------------------------------------------------------- 
# Import modules
# ---------------------------------------------------------------------------------------- 
from numpy.distutils.core import setup, Extension
import os
import sys

# ---------------------------------------------------------------------------------------- 
# Build pytdlpack
# ---------------------------------------------------------------------------------------- 
if __name__ == "__main__":

    # Define Fortran compiler flags for GNU and Intel Fortran
    if "build" in sys.argv:
        if "--fcompiler=gnu95" in sys.argv:
            tdlpack_fortran_args = ["-O3",
                                    "-fd-lines-as-comments",
                                    "-ffixed-form",
                                    "-fautomatic",
                                    "-finit-integer=0",
                                    "-finit-real=zero",
                                    "-finit-logical=false"]
        elif "--fcompiler=intelem" in sys.argv:
            tdlpack_fortran_args = ["-O3",
                                    "-nofree",
                                    "-integer-size 32",
                                    "-real-size 32",
                                    "-auto",
                                    "-fpscomp logicals",
                                    "-fp-model strict",
                                    "-assume byterecl",
                                    "-axCore-AVX2",
                                    "-assume buffered_io"]
    else:
        tdlpack_fortran_args = []

    # Define Extension object. For Fortran 77 source files, use "extra_f77_compile_args".
    # For Fortran 90+ source files, use "extra_f90_compile_args".
    ext = Extension(name  = '_tdlpack',
                  sources = ["tdlpack/_tdlpack.pyf",
                             "tdlpack/bswap.f",
                             "tdlpack/ckfilend.f",
                             "tdlpack/ckraend.f",
                             "tdlpack/cksysend.f",
                             "tdlpack/closefile.f",
                             "tdlpack/openfile.f",
                             "tdlpack/pack.f",
                             "tdlpack/pack1d.f",
                             "tdlpack/pack2d.f",
                             "tdlpack/packgp.f",
                             "tdlpack/packxx.f",
                             "tdlpack/packyy.f",
                             "tdlpack/pkbg.f",
                             "tdlpack/pkc4lx.f",
                             "tdlpack/pkms00.f",
                             "tdlpack/pkms97.f",
                             "tdlpack/pkms99.f",
                             "tdlpack/pks4lx.f",
                             "tdlpack/readfile.f",
                             "tdlpack/reduce.f",
                             "tdlpack/unpack.f",
                             "tdlpack/unpkbg.f",
                             "tdlpack/unpklx.f",
                             "tdlpack/unpkoo.f",
                             "tdlpack/unpkpo.f",
                             "tdlpack/unpkps.f",
                             "tdlpack/writep.f",
                             "tdlpack/xfer1d2d.f"],
    extra_f77_compile_args = tdlpack_fortran_args)

    # Run setup
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
