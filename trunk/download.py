#!/usr/bin/env python
import os
import googleMaps
import sys
import Queue
import threading
from mapConst import *
from threading import Thread
from Queue import Queue
from mapUtils import coord_to_tile

serviceQueue = None
threads = []
class DownloaderThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            info = serviceQueue.get()
            if (info == None):
                return
            ctx_map.get_file(info, True, False)
            serviceQueue.task_done()



ctx_map = googleMaps.GoogleMaps()
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
    print '  --longitude=  Longitud of the location'
    print ' '
    print '  --latrange=   Latitude Range to get   (default = %f)' % lat_range
    print '  --lngrange=   Longitud Range to get   (default = %f)' % lng_range
    print '  --max-zoom=   Maximum Zoom   (default = %d)' % max_zl
    print '  --min-zoom=   Minimum Zoom   (default = %d)' % min_zl
    print '  --threads=    Number of therads   (default = %d)' % nr_threads
    print '  --full-range  Sets the Latitude & Longitud ranges to the Maximum'
    print ' '
    print 'SAMPLE USAGE'
    print ' '
    print '  download.py --location="Paris, France"'
    print '  download.py --location="0, 0" --min-zoom=13 --full-range'
    print '  download.py --latitude=37.979180 --longitude=23.716647'

def download(lat, lng, lat_range, lng_range):
    lat_min = lat - lat_range
    lat_max = lat + lat_range
    lng_min = lng - lng_range
    lng_max = lng + lng_range

    for zl in range(max_zl, min_zl - 1, -1):
        print "Downloading zl %d" % zl
        tmpCenter = coord_to_tile((lat_max, lng_min, zl))
        tlx, tly = tmpCenter[0]

        tmpCenter = coord_to_tile((lat_min, lng_max, zl))
        brx, bry = tmpCenter[0]

        for x in range(tlx, brx+1):
            for y in range(tly, bry+1):
                serviceQueue.put((x, y, zl))
#                ctx_map.get_file(zl, (x, y), True)

if __name__ == "__main__":
    lat = None
    lng = None
    location = None

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
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
                elif arg.startswith('--full-range'):
                    lat_range = 85
                    lng_range = 179

    if (location == None) and ((lat == None) or (lng == None)):
        print_help()
        exit(0)
    print "location = %s" % location
    if ((lat == None) or (lng == None)):
        locations = ctx_map.get_locations()
        if (not location in locations.keys()):
            l = ctx_map.search_location(location)
            if (False == l):
                print "Can't find %s in google map" % location
                exit(0)
            location = l;
        coord = ctx_map.get_locations()[location]
        lat = coord[0]
        lng = coord[1]

    if (location == None):
        location = "somewhere"
    print "Download %s (%f, %f), range (%f, %f), zoom level: %d to %d" % \
            (location, lat, lng, lat_range, lng_range, max_zl, min_zl)

    if (nr_threads <= 0):
        threads = 1
    serviceQueue = Queue(nr_threads)
    for i in xrange(nr_threads):
        threads.append(DownloaderThread())
    for t in threads:
        t.start()

    download(lat, lng, lat_range, lng_range)

    for t in threads:
        serviceQueue.put(None)
    for t in threads:
        t.join()

