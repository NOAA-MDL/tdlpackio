from distutils.cmd import Command
from numpy.distutils.core import setup, Extension
import glob
import os
import sys

# ---------------------------------------------------------------------------------------- 
# Definitions
# ---------------------------------------------------------------------------------------- 
VERSION = '1.0.7'

# ---------------------------------------------------------------------------------------- 
# Define Fortran compiler options for supported compilers
# ---------------------------------------------------------------------------------------- 
gnu_f77_flags = ["-O3",
                 "-g",
                 "-fbacktrace",
                 "-fd-lines-as-comments",
                 "-ffixed-form",
                 "-fautomatic",
                 "-finit-integer=0",
                 "-finit-real=zero",
                 "-finit-logical=false"]
gnu_f90_flags = ["-O3",
                 "-g",
                 "-fbacktrace",
                 "-fautomatic",
                 "-finit-integer=0",
                 "-finit-real=zero",
                 "-finit-logical=false"]
intel_f77_flags = ["-O3",
                   "-g",
                   "-traceback",
                   "-nofree",
                   "-integer-size","32",
                   "-real-size","32",
                   "-auto",
                   "-fpscomp","logicals",
                   "-fp-model=strict",
                   "-assume","byterecl",
                   "-xHost",
                   "-align","array64byte",
                   "-assume","buffered_io"]
intel_f90_flags = ["-O3",
                   "-g",
                   "-traceback",
                   "-integer-size","32",
                   "-real-size","32",
                   "-auto",
                   "-fpscomp","logicals",
                   "-fp-model=strict",
                   "-assume","byterecl",
                   "-xHost",
                   "-align","array64byte",
                   "-assume","buffered_io"]

# ---------------------------------------------------------------------------------------- 
# Write version info
# ---------------------------------------------------------------------------------------- 
def write_version_file(filename='pytdlpack/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM PYTDLPACK SETUP.PY
version = '%(version)s'
"""
    a = open(filename,'w')
    try:
        a.write(cnt % {'version': VERSION})
    finally:
        a.close()

# ---------------------------------------------------------------------------------------- 
# Define Fortran compiler flags for GNU and Intel Fortran
# ---------------------------------------------------------------------------------------- 
f77_flags = gnu_f77_flags
f90_flags = gnu_f90_flags
try:
    if 'gfortran' in os.environ['FC']:
        f77_flags = gnu_f77_flags
        f90_flags = gnu_f90_flags
    elif 'ifort' in os.environ['FC']:
        f77_flags = intel_f77_flags
        f90_flags = intel_f90_flags
except(KeyError):
    pass # Default to GNU Fortran
if "build" in sys.argv:
    if "--fcompiler=gnu95" in sys.argv:
        f77_flags = gnu_f77_flags
        f90_flags = gnu_f90_flags
    elif "--fcompiler=intelem" in sys.argv:
        f77_flags = intel_f77_flags
        f90_flags = intel_f90_flags

# ---------------------------------------------------------------------------------------- 
# Define Extension object. For Fortran 77 source files, use "extra_f77_compile_args".
# For Fortran 90+ source files, use "extra_f90_compile_args".
# ---------------------------------------------------------------------------------------- 
f77_sources = glob.glob("tdlpack/*.f")
f90_sources = glob.glob("tdlpack/*.f90")
all_sources = ["tdlpack/tdlpack.pyf"]+f77_sources+f90_sources
ext = Extension(name  = 'tdlpack',
                sources = all_sources,
                extra_f77_compile_args = f77_flags,
                extra_f90_compile_args = f90_flags
                )

# ---------------------------------------------------------------------------------------- 
# Define testing class
# ---------------------------------------------------------------------------------------- 
class TestCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        for f in os.listdir('./test/'):
            raise SystemExit(subprocess.call([sys.executable,'./test/'+f]))

# ---------------------------------------------------------------------------------------- 
# Rewrite the version file everytime
# ---------------------------------------------------------------------------------------- 
write_version_file()

# ---------------------------------------------------------------------------------------- 
# Import README.md as PyPi long_description
# ---------------------------------------------------------------------------------------- 
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# ---------------------------------------------------------------------------------------- 
# Run setup
# ---------------------------------------------------------------------------------------- 
setup(name             = 'pytdlpack',
      author           = "Eric Engle",
      author_email     = "eric.engle@mac.com",
      url              = "https://github.com/eengl/pytdlpack",
      download_url     = "https://github.com/eengl/pytdlpack/releases",
      version          = VERSION,
      description      = "Python interface for reading and writing TDLPACK data",
      license          = 'GPL-3.0',
      ext_modules      = [ext],
      py_modules       = ['TdlpackIO'],
      packages         = ['pytdlpack'],
      cmdclass         = {'test':TestCommand},
      classifiers      = ['Development Status :: 5 - Production/Stable',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.6',
                          'Programming Language :: Python :: 3.7',
                          'Programming Language :: Python :: 3.8',
                          'Programming Language :: Python :: 3.9',
                          'Programming Language :: Python :: 3.10',
                          'Environment :: Console',
                          'Topic :: Scientific/Engineering',
                          'Topic :: Scientific/Engineering :: Atmospheric Science',
                          'Intended Audience :: Science/Research',
                          'Operating System :: OS Independent',
                          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
      install_requires  = ['numpy>=1.12'],
      python_requires   = '>=3.6',
      long_description  = long_description,
      long_description_content_type = 'text/markdown'
)
