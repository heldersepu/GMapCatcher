#!/usr/bin/env python

## @package download
# Downloader tool without GUI

import sys
import src.mapConf as mapConf

from src.mapUtils import *
from src.mapServices import MapServ
from src.mapDownloader import MapDownloader

conf = mapConf.MapConf()
ctx_map = MapServ(conf.init_path)
downloader = None
max_zl = MAP_MAX_ZOOM_LEVEL
min_zl = MAP_MIN_ZOOM_LEVEL + 4
lng_range = 0.05
lat_range = 0.05
nr_threads = 5

def print_help():
    print ' '
    print 'Download all maps of given location with one command'
    print ' '
    print 'OPTIONS'
    print '  --location=   Location to download'
    print '  --latitude=   Latitude of the location '
    print '  --longitude=  Longitude of the location'
    print ' '
    print '  --map         Retrieve map images (default)'
    print '  --satellite   Retrieve satellite images'
    print '  --terrain     Retrieve terrain images'
    print ' '
    print '  --latrange=   Latitude Range to get    (default = %f)' % lat_range
    print '  --lngrange=   Longitude Range to get   (default = %f)' % lng_range
    print '  --max-zoom=   Maximum Zoom   (default = %d)' % max_zl
    print '  --min-zoom=   Minimum Zoom   (default = %d)' % min_zl
    print '  --threads=    Number of threads   (default = %d)' % nr_threads
    print '  --full-range  Sets Lat, Lng to (0, 0) and range to the Max,'
    print '                very useful to download maps of entire world'
    print ' '
    print 'SAMPLE USAGE'
    print '  download.py --location="Paris, France"'
    print '  download.py --min-zoom=13 --full-range'
    print '  download.py --latitude=37.979180 --longitude=23.716647'

def do_nothing(*args, **kwargs):
    pass


def download(lat, lng, lat_range, lng_range, layer):
    for zl in range(max_zl, min_zl - 1, -1):
        print "Downloading zl %d" % zl
        downloader.query_region_around_location(lat, lng, 
            lat_range*2, lng_range*2, zl, 
            layer, do_nothing, 
            mapServ=conf.map_service,
            styleID=conf.cloudMade_styleID
        )
        downloader.wait_all()

if __name__ == "__main__":
    lat = None
    lng = None
    location = None
    layer = LAYER_MAP

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                arg = arg.lower()
                if arg.startswith('--max-zoom-level='):
                    max_zl = int(arg[17:])
                elif arg.startswith('--min-zoom-level='):
                    min_zl = int(arg[17:])
                elif arg.startswith('--max-zoom='):
                    max_zl = int(arg[11:])
                elif arg.startswith('--min-zoom='):
                    min_zl = int(arg[11:])
                elif arg.startswith('--location='):
                    location = arg[11:]
                elif arg.startswith('--longitude='):
                    lng = float(arg[12:])
                elif arg.startswith('--latitude='):
                    lat = float(arg[11:])
                elif arg.startswith('--latrange='):
                    lat_range = float(arg[11:])
                elif arg.startswith('--lngrange='):
                    lng_range = float(arg[11:])
                elif arg.startswith('--threads='):
                    nr_threads = int(arg[10:])
                elif arg.startswith('--satellite'):
                    layer = LAYER_SATELLITE
                elif arg.startswith('--terrain'):
                    layer = LAYER_TERRAIN
                elif arg.startswith('--full-range'):
                    location = "Whole World"
                    lng = 0
                    lat = 0
                    lat_range = 85
                    lng_range = 179

    if (location == None) and ((lat == None) or (lng == None)):
        print_help()
        exit(0)
    print "location = %s" % location
    if ((lat == None) or (lng == None)):
        locations = ctx_map.get_locations()
        if (not location in locations.keys()):
            location = ctx_map.search_location(location)
            if (location[:6] == "error="):
                print location[6:]
                exit(0)

        coord = ctx_map.get_locations()[location]
        lat = coord[0]
        lng = coord[1]

    if (location == None):
        location = "somewhere"
    print "Download %s (%f, %f), range (%f, %f), zoom level: %d to %d" % \
            (location, lat, lng, lat_range, lng_range, max_zl, min_zl)

    downloader=MapDownloader(ctx_map, nr_threads)
    try:
        download(lat, lng, lat_range, lng_range, layer)
    finally:
        print "Waiting..."
        downloader.stop_all()

