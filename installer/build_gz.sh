#!/bin/bash
# This Script is used to build the tar.gz file

cd ..

dVer=''
dName=''
dFile='cat src\mapConst.py'

for dLine in $dFile
do
    if [$dLine = 'NAME =']
    then
        dName=''
    else
        if [$dLine = 'VERSION =']
        then
            dVer=''
        fi
    fi

    # if [dName!='' && dVer='']
    # then
        # # Exit For
    # fi
done

tar czf ../GMapCatcher-0.1.1.0.tar.gz *.py src images installer Changelog README
