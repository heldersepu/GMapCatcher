#!/bin/bash
# This Script is used to build the tar.gz file

cd ..

dName="`grep -w "NAME = " src/mapConst.py`"
dName=${dName:8}
dName=${dName/%\"}

dVer="`grep -w "VERSION = " src/mapConst.py`"
dVer=${dVer:11}
dVer=${dVer/%\"}

tar czf ../$dName-$dVer.tar.gz *.py src images installer Changelog README
