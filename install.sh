#!/bin/sh

if [ $# -ne 2 ]; then
   echo "usage: $(basename $0) FCOMPILER PREFIX"
   echo "    FCOMPILER - See f2py documentation"
   echo "       PREFIX - Path to install."
   exit 1
fi

FCOMPILER=$1
PREFIX=$2

python3 setup.py build_ext --fcompiler=$FCOMPILER build
python3 setup.py install --prefix=$PREFIX
