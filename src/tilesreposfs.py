## This modul provides filebased tile repository functions
#
# Usage:
#
# - constructor requires MapServ instance, because method
#  'get_tile_from_coord' is provided in the MapServ
#
# - this module is not used directly. It is used via MapServ() methods:
#     - get_file()
#     - load_pixbuf()
# - module is finalized from MapServ.finish() method


import os
import sys
import gtk

import lrucache
import mapPixbuf
import fileUtils

from threading import Lock
from mapConst import *


class TilesRepositoryFS:

    def __init__(self, MapServ_inst):
        self.tile_cache = lrucache.LRUCache(1000)
        self.mapServ_inst = MapServ_inst
        self.lock = Lock()
        self.configpath = self.mapServ_inst.configpath
        
        self.missingPixbuf = mapPixbuf.missing()

    def finish(self):
        pass

    ## Returns the PixBuf of the tile
    # Uses a cache to optimise HDD read access
    def load_pixbuf(self, coord, layer, force_update):
        filename = self.coord_to_path(coord, layer)
        if not force_update and (filename in self.tile_cache):
            pixbuf = self.tile_cache[filename]
        else:
            if os.path.isfile(filename):
                try:
                    pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                    self.tile_cache[filename] = pixbuf
                except Exception:
                    pixbuf = self.missingPixbuf
                    print "File corrupted: %s" % filename
                    fileUtils.del_file(filename)
            else:
                pixbuf = self.missingPixbuf
        return pixbuf

    ## Get the png file for the given location
    # Returns true if the file is successfully retrieved
    def get_png_file(self, coord, layer, filename,
                        online, force_update, mapServ, styleID):
        # remove tile only when online
        if (force_update and online):
            fileUtils.delete_old(filename)

        if os.path.isfile(filename):
            return True
        if not online:
            return False

        try:
            data = self.mapServ_inst.get_tile_from_coord(
                        coord, layer, online, mapServ, styleID
                    )
            file = open( filename, 'wb' )
            file.write( data )
            file.close()
            return True
        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]
        return False

    ## Return the absolute path to a tile
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention: 
    #  \.googlemaps\tiles\15\0\1\0\1.png 
    #  We only have 2 levels for one axis
    #  at most 1024 files in one dir
    def coord_to_path(self, tile_coord, layer):
        self.lock.acquire()
        path = os.path.join(self.configpath, LAYER_DIRS[layer])
        path = fileUtils.check_dir(path)
        path = fileUtils.check_dir(path, '%d' % tile_coord[2])
        path = fileUtils.check_dir(path, "%d" % (tile_coord[0] / 1024))
        path = fileUtils.check_dir(path, "%d" % (tile_coord[0] % 1024))
        path = fileUtils.check_dir(path, "%d" % (tile_coord[1] / 1024))
        self.lock.release()
        return os.path.join(path, "%d.png" % (tile_coord[1] % 1024))

    ## Get the image file for the given location
    # Validates the given coordinates and,
    # returns the local filename if successfully retrieved
    def get_file(self, coord, layer, online, force_update, mapServ, styleID):
        if (MAP_MIN_ZOOM_LEVEL <= coord[2] <= MAP_MAX_ZOOM_LEVEL):
            world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - coord[2])
            if (coord[0] > world_tiles) or (coord[1] > world_tiles):
                return None
            ## Tiles dir structure
            filename = self.coord_to_path(coord, layer)
            # print "Coord to path: %s" % filename
            if self.get_png_file(coord, layer, filename, online,
                                    force_update, mapServ, styleID):
                return filename
        return None


