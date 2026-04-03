#!/bin/sh
# ----------------------------------------------------------------------------------------
# Uses real pdoc (https://github.com/mitmproxy/pdoc), not pdoc3
#
# pip install pdoc
# ----------------------------------------------------------------------------------------
export PYTHONPATH=src
export VERSION=$(cat ./VERSION)
python -m pdoc -d numpy --footer-text "tdlpackio v${VERSION}" -o docs tdlpackio
