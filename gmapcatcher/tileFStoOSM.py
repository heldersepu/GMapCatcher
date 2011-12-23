# -*- coding: utf-8 -*-
## @package gmapcatcher.tileFStoOSM.py
# A tool to convert GMapCatcher format to OSM

import re
import os
from mapConst import *

## Convert from GMapCatcher filename to coord
#  file = C:\Users\Dog\.googlemaps\tiles\-1\74\541\96\982.png
# coord = 74*1024 + 541,  96*1024 + 982,  -1
def get_coord_from_name(filename):
    m = re.match('.*\D(-\d+)\D(\d+)\D(\d+)\D(\d+)\D(\d+)\.png',filename)
    if not m:
        m = re.match('.*\D(\d+)\D(\d+)\D(\d+)\D(\d+)\D(\d+)\.png',filename)
    if m:
        g = m.groups()
        if len(g) == 5:
            return int(g[1])*1024 + int(g[2]), \
                   int(g[3])*1024 + int(g[4]), \
                   int(g[0])

## Rename a file in GMapCatcher format to OSM format
def convert_file(file, dirDestination):
    coord = get_coord_from_name(file)
    if coord:
        zoom = MAP_MAX_ZOOM_LEVEL - coord[2]
        d = os.path.join(dirDestination, str(zoom))
        if not os.path.exists(d):
			os.mkdir(d)
        d = os.path.join(d, str(coord[0]))
        if not os.path.exists(d):
			os.mkdir(d)
        destFile = os.path.join(d, str(coord[1]) + '.png')
        os.rename(file, destFile)

## Do the conversion from the given source to the destination
def do_conversion(dirSource):
    if not os.path.exists(dirSource):
        print "Directory not found: \n" + dirSource
        return

    #recursively loop inside the dirSource
    for root, dirs, files in os.walk(dirSource):
        for name in files:
            convert_file(os.path.join(root, name), dirSource)


do_conversion('C:\\xampp\\htdocs\\tiles')
