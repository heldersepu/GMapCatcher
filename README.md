## Overview ##

GMapCatcher is an offline maps viewer. It can display maps from many providers such as:

[CloudMade](http://maps.cloudmade.com/), [OpenStreetMap](http://www.openstreetmap.org/), [Yahoo Maps](http://maps.yahoo.com/), [Bing Maps](http://www.bing.com/maps/), [Nokia Maps](http://maps.nokia.com), ~~SkyVector~~, ~~Google Map~~.

It displays them using a custom GUI. User can view the maps while offline. GMapCatcher doesn't depend on the map's JavaScript.

GMapCatcher is written in Python 2.7 & PyGTK, can run on Linux, Windows and Mac OSX.

![https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/snapshot.gif](https://raw.githubusercontent.com/heldersepu/gmapcatcher/wiki/snapshot.gif)

You can find a list of improvements and latest features in the [Changelog](http://code.google.com/p/gmapcatcher/source/browse/trunk/changelog)

## Download ##

https://github.com/heldersepu/GMapCatcher/releases/tag/0.8.0.6

or

```
$ git clone https://github.com/heldersepu/gmapcatcher
```


## Usage ##

**maps.py** is a gui program used to browse google map. With the **offline** toggle button unchecked,  it can download google map tiles automatically. Once the file downloaded, it will reside on user's hard disk and needn't to be downloaded again any more. At release 0.02, it use multi-threaded downloader and can be faster.

After version 0.04, user can force GMapCatcher to re-download old map tiles by checking "Force update". If a tile is older than 24 hours, it will be re-downloaded.

**download.py** is a downloader tools that can be used to download map tiles without gui. **maps** can use files it downloaded without configuration.

Below is an example using **download.py**:
```
$ download.py --location="Paris, France" --max-zoom=16 --min-zoom=0 --latrange=2.0 --lngrange=2.0
```

## Files ##
Linux:
```
$HOME/.GMapCatcher/*
```

Windows:
```
%UserProfile%/.GMapCatcher/*
```

## Dependencies ##

Windows users are highly recommended to download the [latest Windows installer](https://github.com/heldersepu/GMapCatcher/releases).
This installer contains all required packages, works well on XP, Vista and Win 7.
For a complete list of tested OS, see wiki [Tested Operating Systems](https://github.com/heldersepu/GMapCatcher/blob/wiki/TestedOperatingSystems.md).


If you choose the tarball (because you have a legacy Windows like Windows 98), you must install [Python 2.7](http://www.python.org/download/), [GTK+ for windows](http://www.gtk.org/download.html), [pygtk, pygobject and pycairo](http://www.pygtk.org/downloads.html) yourself.

Currently GMapCatcher also depends on [Python Imaging Library (PIL)](http://www.pythonware.com/products/pil/). For gentoo users, emerge dev-python/imaging.

## Authors ##

pi3orama@gmail.com, HelderSepu@gmail.com
