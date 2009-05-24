"""
This modul provides filebased tile repository functions

Usage:

- constructor requires googleMaps instance, because method
'get_tile_from_url' is provided be the googleMaps

- this modul is not used directly. It is used via GoogleMaps() methods:
    - get_file()
    - load_pixbuf()
- module is finalized from GoogleMaps.finish() method

"""

import os
import sys
import gtk

import lrucache
import fileUtils

from threading import Lock
from mapConst import *
from time import time

class TilesRepositoryFS:

    def __init__(self, googleMaps_inst):
        self.tile_cache = lrucache.LRUCache(1000)
        self.instance_google_maps = googleMaps_inst
        self.lock = Lock()
        self.configpath = self.instance_google_maps.configpath

    def finish(self):
        pass

    def load_pixbuf(self, coord, layer):
        filename = self.coord_to_path(coord, layer)
        if not os.path.isfile(filename):
            filename = None
        if filename in self.tile_cache:
            return self.tile_cache[filename]
        w = gtk.Image()
        if (filename == None):
            w.set_from_file('missing.png')
        else:
            w.set_from_file(filename)
        try:
            pb = w.get_pixbuf()
            self.tile_cache[filename] = pb
            return pb
        except ValueError:
            print "File corrupted: %s" % filename
            try:
                os.remove(filename)
            finally:
                w.set_from_file('missing.png')
                return w.get_pixbuf()

    def get_png_file(self, coord, layer, filename, online, force_update):
        # remove tile only when online
        if (os.path.isfile(filename) and force_update and online):
            # Don't remove old tile unless it is downloaded more
            # than 24 hours ago (24h * 3600s) = 86400
            if (int(time() - os.path.getmtime(filename)) > 86400):
                os.remove(filename)

        if os.path.isfile(filename):
            return True
        if not online:
            return False

        try:
            data = self.instance_google_maps.get_tile_from_url(coord, layer, online)
            file = open( filename, 'wb' )
            file.write( data )
            file.close()
            return True
        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]
        return False

    def coord_to_path(self, coord, layer):
        self.lock.acquire()
        ## at most 1024 files in one dir
        ## We only have 2 levels for one axis
        path=os.path.join(self.configpath,LAYER_DIRS[layer])
        path = fileUtils.check_dir(path)
        path = fileUtils.check_dir(path, '%d' % coord[2])
        path = fileUtils.check_dir(path, "%d" % (coord[0] / 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[0] % 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[1] / 1024))
        self.lock.release()
        return os.path.join(path, "%d.png" % (coord[1] % 1024))

    def get_file(self, coord, layer, online, force_update):
        if (MAP_MIN_ZOOM_LEVEL <= coord[2] <= MAP_MAX_ZOOM_LEVEL):
            world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - coord[2])
            if (coord[0] > world_tiles) or (coord[1] > world_tiles):
                return None
            ## Tiles dir structure
            filename = self.coord_to_path(coord, layer)
            # print "Coord to path: %s" % filename
            if (self.get_png_file(coord, layer, filename, online, force_update)):
                return filename
        return None

