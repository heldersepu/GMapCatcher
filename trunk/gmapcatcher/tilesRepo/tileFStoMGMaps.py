# -*- coding: utf-8 -*-
## @package gmapcatcher.tilesRepo.tileFStoMGMaps.py
# A tool to convert GMapCatcher format to MGMaps

import re
import os
import shutil
import tilesRepoFS
from mapConst import *

## Create the MGMaps conf fie
def create_conf_file(dir):
    file = open( os.path.join(dir, 'cache.conf'), 'w')
    file.write('version=3\n')
    file.write('tiles_per_file=1\n')
    file.write('hash_size=97\n')
    file.write('center=0,0,1,YahooMap')
    file.close()

## Calculate the hash
def calc_v2_hash(x, y, hash_size=97):
	return str((x * 256 + y) % hash_size)

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

## Copy a file in GMapCatcher format to MGMaps format
def convert_file(file, dirDestination):
    coord = get_coord_from_name(file)
    if coord:
        zoom = MAP_MAX_ZOOM_LEVEL - coord[2]
        d = os.path.join(
            dirDestination,
            'YahooMap_' + str(zoom)
        )
        if not os.path.exists(d):
			os.mkdir(d)
        d = os.path.join(
            d, calc_v2_hash(coord[0], coord[1])
        )
        if not os.path.exists(d):
			os.mkdir(d)
        destFile = os.path.join(d, str(coord[0]) +'_'+ str(coord[1]) + '.mgm')
        shutil.copyfile(file, destFile)
        print destFile

## Do the conversion from the given source to the destination
def do_conversion(dirSource, dirDestination):
    if not os.path.exists(dirSource):
        print "Directory not found: \n" + dirSource
        return
    if not os.path.exists(dirDestination):
        os.mkdir(dirDestination)
    create_conf_file(dirDestination)
    #recursively loop inside the dirSource
    for root, dirs, files in os.walk(dirSource):
        for name in files:
            convert_file(os.path.join(root, name), dirDestination)


do_conversion('C:\\Users\Dog\\.googlemaps\\yahoomap', 'C:\\MGMapsCache')
