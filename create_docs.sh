#!/bin/sh

BUILD_DIR=$(find $PWD/build -mindepth 1 -name "lib.*" -type d)
export PYTHONPATH=$BUILD_DIR:$PYTHONPATH

VER=$(python -c "import pytdlpack; print(f\"pytdlpack v{pytdlpack.__version__}\")")

pdoc --footer-text "$VER" -o 'docs' pytdlpack
pdoc --footer-text "$VER" -o 'docs' TdlpackIO

touch index.html
echo "<h1>$VER</h1>" >> index.html
echo "<li> <a href=pytdlpack.html>pytdlpack docs</a> </li>" >> index.html
echo "<li> <a href=TdlpackIO.html>TdlpackIO docs</a> </li>" >> index.html
mv -v index.html docs/.
