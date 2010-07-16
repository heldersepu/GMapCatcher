#!/bin/bash
# This Script is used to build the tar.gz file

if [ "$1" = "refreshdebian" ]
then
    echo "warning - replacing entire debian directory"
    echo "make sure you have made a backup for the manual stage!"
    echo "continue? yes/no"
    read aword
    if [ ! "$aword" = "yes" ]
    then
        exit
    fi
fi

cd ..
MAINDIR=$(pwd)
echo $MAINDIR


# Clean up temporary files
find . -name \*.pyc | xargs rm -f

if [ "$1" = "refreshdebian" ]
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

if [ "$1" = "lin" -o "$1" = "refreshdebian" ]
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
# clean up backup files
find . -name \*~ | xargs rm -f

# Remove some files
rm -r -f $dirname/common
if [ "$1" = "lin" -o "$1" = "refreshdebian" ]
then
    rm -r -f $dirname/WindowsMobile
fi
rm -r -f $dirname/debian

find . -name \.svn | xargs rm -r -f

# Create the tar.gz file
if [ "$1" = "lin" -o "$1" = "refreshdebian" ]
then
    filename="$pkgname.orig.tar.gz"
else
    filename="../$pkgname.tar.gz"
fi

mv $dirname/installer/setup.py $dirname/setup.py

echo "making file $filename"
tar czf $filename $dirname
 
if [ "$1" = "refreshdebian" ]
then
    cd $dirname
    dh_make -b -c gpl2
    cd debian
    pwd
    rm *.ex *.EX
    echo $MAINDIR
    cd $MAINDIR
    if [ ! -d debian ]
    then
        mkdir debian
    fi
    cp ../temp/$dirname/debian/* debian/
    mv ../temp/$pkgname.orig.tar.gz ../$pkgname.tar.gz
fi

if [ "$1" = "lin" ]
then
    cd $dirname
    mkdir debian
    cp -r $MAINDIR/debian/* debian
    debuild -us -uc
    cd ..
    cp *.deb $MAINDIR
    cp *.orig.tar.gz $MAINDIR/$pkgname.tar.gz
fi

# Delete temp directory
rm -rf ../temp/
