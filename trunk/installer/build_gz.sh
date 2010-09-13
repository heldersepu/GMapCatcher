#!/bin/bash
# This Script is used to build the tar.gz file
# to make the .deb you'll need ubuntu-dev-tools plus many of its suggested packages
# - build-essential, lintian, debhelper, cdbs, fakeroot, pbuilder dh-make notably
echo "$0 - script for packaging gmapcatcher"
if [ "$1" = "help" ]
then
    echo "$0 makedeb - makes .deb installer plus mapcatcher tar.gz"
    echo "$0 makedeb debupload - additionally saves *all* debian upload files"
    echo "$0 makedeb debupload ubuntu - additionally makes/saves .changes file"
    echo "together in debian_support subdirectory im project tree"
    echo "$0 refreshdebdir - makes new debian directory in project tree"
    echo " -- make sure you have backed up the original debian directory --"
    echo " -- as the automatic creation is merely the preliminary stage  --"
    exit
else
    echo "$ $0 help for more"
fi

if [ "$1" = "refreshdebdir" ]
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

if [ "$1" = "refreshdebdir" ]
then
    rm $MAINDIR/debian/*
    rmdir $MAINDIR/debian
fi

# Get the Name 
dName="`grep -w "NAME = " gmapcatcher/mapConst.py`"
dName=${dName:8}
dName=${dName/%\"}
echo "Name $dName"
debname=$(echo $dName | awk '{print tolower($0)}')
debname=$(echo $debname | awk '{sub(/g/,"",$0); print $0}')
echo "debian name $debname"

# debian package variables
# should match the key that signs the .deb we upload to debian
export DEBFULLNAME="Mark Benjamin"
export DEBEMAIL="MarkieB.lists.20090330@gmail.com"

# Get the Version
dVer="`grep -w "VERSION = " gmapcatcher/mapConst.py`"
dVer=${dVer:11}
dVer=${dVer/%\"}
echo "Version $dVer"

if [ "$1" = "makedeb" -o "$1" = "refreshdebdir" ]
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
if [ -e $dirname/debian ]
then
    rm -r -f $dirname/debian
fi

# prepare files for debian-type arrangement
if [ "$1" = "makedeb" -o "$1" = "refreshdebdir" ]
then
    rm -r -f $dirname/WindowsMobile
    mv $dirname/maps.py $dirname/mapcatcher
    mv $dirname/download.py $dirname/mapdownloader
    gzip -9 $dirname/man/mapcatcher.1
    gzip -9 $dirname/man/mapdownloader.1
    cp $dirname/images/map.png $dirname/images/mapcatcher.png
fi

# clear such cruft as there may be
rm -f $dirname/*.gz
rm -f $dirname/*.deb
rm -f $dirname/*.lzma
rm -f $dirname/*.zip
rm -f $dirname/*.dsc
rm -f $dirname/*.rpm

if [ -e $dirname/debian_support ]
then
    rm -rf $dirname/debian_support
fi

find . -name \.svn | xargs rm -r -f

# Create the tar.gz file
if [ "$1" = "makedeb" -o "$1" = "refreshdebdir" ]
then
    filename="$pkgname.orig.tar.gz"
else
    filename="../$pkgname.tar.gz"
fi

mv $dirname/installer/setup.py $dirname/setup.py

echo "making file $filename"
tar czf $filename $dirname

if [ "$1" = "refreshdebdir" ]
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

if [ "$1" = "makedeb" ]
then
    cd $dirname
    if [ "$2" = "strict" -o "$3" = "strict" ]
    then
        echo "STRICT_LEGAL = True" > gmapcatcher/changeableConst.py
    fi
    mkdir debian
    cp -r $MAINDIR/debian/* debian
    cd debian
    find . -name \.svn | xargs rm -r -f
    rm legacy.diff
    cd ..
    if [ "$3" = "ubuntu" ]
    then
        debuild -S -us -uc
#        debuild -S -kEE8E4DE8
    else
        debuild -us -uc
# -us -uc is unsigned; -us for source, -uc for debian changes;
# in an upload to a repo then signing is obligatory; for instance
# debuild -kEE8E4DE8
    fi
    cd ..
    cp *.deb $MAINDIR
    cp *.orig.tar.gz $MAINDIR/$pkgname.tar.gz
    if [ ! -d $MAINDIR/debian_support ]
    then
        mkdir $MAINDIR/debian_support
    fi
    rm $MAINDIR/debian_support/*
    mv *.orig.tar.gz $MAINDIR/debian_support
    mv *.diff.gz $MAINDIR/debian_support
    mv *.dsc $MAINDIR/debian_support
    if [ "$2" = "debupload" ]
    then
        cp * $MAINDIR/debian_support
    fi
fi

# Delete temp directory
rm -rf ../temp/

# cd $MAINDIR/debian_support

# maverick
# dput ppa:ubunt-u-markbenjamin/mapcatcher $pkgname-1ubuntu1_source.changes

# lucid
# dput ppa:ubunt-u-markbenjamin/mapcatcher $pkgname-1ubuntu0_source.changes
