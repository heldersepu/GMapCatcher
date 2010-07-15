#!/bin/bash
# This Script is used to build the tar.gz file

cd ..
# Clean up temporary files
find . -name \*.pyc | xargs rm -f
find . -name \*.py~ | xargs rm -f

# Get the Name 
dName="`grep -w "NAME = " src/mapConst.py`"
dName=${dName:8}
dName=${dName/%\"}
echo "Name $dName"
debname=$(echo $dName | awk '{print tolower($0)}')
echo "debian name $debname"

# Get the Version
dVer="`grep -w "VERSION = " src/mapConst.py`"
dVer=${dVer:11}
dVer=${dVer/%\"}
echo "Version $dVer"

if [ $1 = "lin" ]
then
    pkgname=$debname"_"$dVer
else
    pkgname="$dName-$dVer"
fi

# Copy all the files to a temp location
mkdir -p ../temp/$pkgname
cp -r * ../temp/$pkgname
cd ../temp

# Remove some files
rm -r -f $pkgname/common
if [ $1 = "lin" ]
then
    rm -r -f $pkgname/WindowsMobile
else
    rm -r -f $pkgname/debian
fi

find . -name \.svn | xargs rm -r -f

# Create the tar.gz file
filename="../$pkgname.tar.gz"
echo "making file $filename"
tar czf $filename $pkgname

# Delete temp directory
cd ..
rm -r -f temp/
