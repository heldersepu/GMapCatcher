#!/usr/bin/env python

## @package download
# Downloader tool without GUI

import sys
import src.mapConf as mapConf

from src.mapUtils import *
from src.mapArgs import MapArgs
from src.mapServices import MapServ
from src.mapDownloader import MapDownloader

conf = mapConf.MapConf()
ctx_map = MapServ(conf.init_path)
downloader = None

def do_nothing(*args, **kwargs):
    pass


def download(lat, lng, lat_range, lng_range, max_zl, min_zl, layer):
    for zl in range(max_zl, min_zl - 1, -1):
        print "Downloading zl %d" % zl
        downloader.query_region_around_location(
            lat, lng,
            lat_range*2, lng_range*2, zl,
            layer, do_nothing,
            mapServ=conf.map_service,
            styleID=conf.cloudMade_styleID
        )
        downloader.wait_all()

if __name__ == "__main__":

    args = MapArgs(sys.argv)

    if (args.location is None) and ((args.lat is None) or (args.lng is None)):
        args.print_help()
        exit(0)

    print "location = %s" % args.location
    if ((args.lat is None) or (args.lng is None)):
        locations = ctx_map.get_locations()
        if (not args.location in locations.keys()):
            args.location = ctx_map.search_location(args.location)
            if (args.location[:6] == "error="):
                print args.location[6:]
                exit(0)

        coord = ctx_map.get_locations()[args.location]
        args.lat = coord[0]
        args.lng = coord[1]

    if args.width > 0:
        args.lng_range = mapUtils.km_to_lat(args.width, args.lat)
    if args.height > 0:
        args.lat_range = mapUtils.km_to_lon(args.height)

    if (args.location is None):
        args.location = "somewhere"
    print "Download %s (%f, %f), range (%f, %f), zoom level: %d to %d" % \
            (args.location, args.lat, args.lng,
             args.lat_range, args.lng_range,
             args.max_zl, args.min_zl)

    downloader = MapDownloader(ctx_map, args.nr_threads)
    try:
        download(args.lat, args.lng, args.lat_range, args.lng_range,
                 args.max_zl, args.min_zl, args.layer)
    finally:
        print "Waiting..."
        downloader.stop_all()

