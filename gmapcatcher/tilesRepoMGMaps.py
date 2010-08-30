## @package gmapcatcher.tilesRepoMGMaps
# This modul provides filebased tile repository functions
#
# Usage:
#
# - constructor requires MapServ instance, because method
#  'get_tile_from_coord' is provided in the MapServ
#
# - this module is not used directly. It is used via MapServ() methods:
#    def finish(self):
#    def load_pixbuf(self, coord, layer, force_update):
#    def do_export(self, tcoord, layer, online, mapServ, styleID, size):
#    def is_tile_in_local_repos(self, coord, layer):
#    def set_repository_path(self, newpath):
# - module is finalized from MapServ.finish() method


import os
import gtk

import lrucache
import mapPixbuf
import fileUtils

from threading import Lock
from mapConst import *

from tilesRepo import TilesRepository


class TilesRepositoryMGMaps(TilesRepository):

    def __init__(self, MapServ_inst):
        self.configpath = self.mapServ_inst.configpath
        self.tile_cache = lrucache.LRUCache(1000)
        self.mapServ_inst = MapServ_inst
        self.lock = Lock()
        self.missingPixbuf = mapPixbuf.missing()

    def finish(self):
        pass

    ## Sets new repository path to be used for storing tiles
    def set_repository_path(self, newpath):
        self.configpath = newpath

    ## check if we have locally downloaded tile
    def is_tile_in_local_repos(self, coord, layer):
        path = self.coord_to_path(coord, layer)
        return  os.path.isfile(path)

    ## Returns the PixBuf of the tile
    #  Uses a cache to optimise HDD read access
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
    #  Returns true if the file is successfully retrieved
    def get_png_file(self, coord, layer,
                        online, force_update, conf):
        filename = self.coord_to_path(coord, layer)
        # remove tile only when online
        remove_tile = (force_update and online)

        if os.path.isfile(filename) and not remove_tile:
            return True
        if not online:
            return False

        try:
            data = self.mapServ_inst.get_tile_from_coord(
                        coord, layer, conf
                    )
            self.coord_to_path_checkdirs(coord, layer)
            # Remove the old tile only after getting the new data
            if remove_tile:
                fileUtils.delete_old(filename)
            file = open( filename, 'wb' )
            file.write( data )
            file.close()

            return True
        except KeyboardInterrupt:
            raise
        except Exception, excInst:
            print excInst
        return False

    ## Return the absolute path to a tile
    #  only check path
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention:
    #  \.googlemaps\tiles\15\1_1.mgm
    #  We only have 2 levels for one axis
    #  at most 1024 files in one dir
    # private
    def coord_to_path(self, tile_coord, layer):
        return os.path.join(
            self.configpath,
            MAP_SERVICES[layer]["layerDir"] + "_" + str(tile_coord[2]),
            str(tile_coord[0]) + "_" + str(tile_coord[1]) + ".mgm"
        )

    ## create path if doesn't exists
    def coord_to_path_checkdirs(self, tile_coord, layer):
        self.lock.acquire()
        path = fileUtils.check_dir(self.configpath)
        path = fileUtils.check_dir(
            path, MAP_SERVICES[layer]["layerDir"] + "_" + str(tile_coord[2])
        )
        self.lock.release()
        return os.path.join(path, "%d_%d.mgm" % (tile_coord[0], tile_coord[1]))
