#!/bin/bash
# This Script is used to build the tar.gz file

cd ..
MAINDIR=$(pwd)
echo $MAINDIR


# Clean up temporary files
find . -name \*.pyc | xargs rm -f
find . -name \*.py~ | xargs rm -f

if [ $1 = "lin" -a $2 = "refresh" ]
then
    rm $MAINDIR/debian/*
    rmdir $MAINDIR/debian
fi

# Get the Name 
dName="`grep -w "NAME = " src/mapConst.py`"
dName=${dName:8}
dName=${dName/%\"}
echo "Name $dName"
debname=$(echo $dName | awk '{print tolower($0)}')
debname=$(echo $debname | awk '{print gensub(/g/,"",1)}')
echo "debian name $debname"

#debian package variables
export DEBFULLNAME="Helder Sepulveda"
export DEBEMAIL="heldersepu@gmail.com"

# Get the Version
dVer="`grep -w "VERSION = " src/mapConst.py`"
dVer=${dVer:11}
dVer=${dVer/%\"}
echo "Version $dVer"

if [ $1 = "lin" ]
then
    pkgname=$debname"_"$dVer
    dirname=$debname"-"$dVer
else
    pkgname="$dName-$dVer"
    dirname="$dName-$dVer"
fi



# Copy all the files to a temp location
mkdir -p ../temp/$dirname
cp -r * ../temp/$dirname
cd ../temp

# Remove some files
rm -r -f $dirname/common
if [ $1 = "lin" ]
then
    rm -r -f $dirname/WindowsMobile
else
    rm -r -f $dirname/debian
fi

find . -name \.svn | xargs rm -r -f

# Create the tar.gz file
if [ $1 = "lin" ]
then
    filename="$pkgname.orig.tar.gz"
else
    filename="../$pkgname.tar.gz"
fi

echo "making file $filename"
tar czf $filename $dirname
 
if [ $1 = "lin" -a $2 = "refresh" ]
then
    cd $dirname
    dh_make -b -c gpl2
    cd debian
    pwd
    rm *.ex *.EX
    echo $MAINDIR
    cd $MAINDIR
    if [ -d debian ]
    then
        cp ../temp/$dirname/debian/* debian/
    else
        mkdir debian
        cp ../temp/$dirname/debian/* debian/
    fi
    cp ../temp/$pkgname.orig.tar.gz .
fi

if [ $1 = "lin" ]
then
# make ,deb
    
fi

# Delete temp directory
rm -rf ../temp/
