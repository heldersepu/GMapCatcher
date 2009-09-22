#!/bin/bash
# This Script is used to build the tar.gz file

cd ..
# Clean up temporary files
find . -name \*.pyc | xargs rm
find . -name \*.py~ | xargs rm

# Get the Name 
dName="`grep -w "NAME = " src/mapConst.py`"
dName=${dName:8}
dName=${dName/%\"}

# Get the Version
dVer="`grep -w "VERSION = " src/mapConst.py`"
dVer=${dVer:11}
dVer=${dVer/%\"}

# Create the tar.gz file
tar czf ../$dName-$dVer.tar.gz *.py src images installer Changelog README
