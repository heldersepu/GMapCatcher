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

from tilesRepo import TilesRepository


class TilesRepositoryFS(TilesRepository):

    def __init__(self, MapServ_inst):
        self.tile_cache = lrucache.LRUCache(1000)
        self.mapServ_inst = MapServ_inst
        self.lock = Lock()

        self.missingPixbuf = mapPixbuf.missing()

    def finish(self):
        pass


    # check if we have locally downloaded tile
    def is_tile_in_local_repos(self, coord, layer):
        path = self.coord_to_path(coord, layer)
        return  os.path.isfile(path)

    
    def remove_old_tile(self, coord, layer, intSeconds=86400):
        return fileUtils.delete_old( self.coord_to_path(coord, layer), intSeconds )

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
                        coord, layer, mapServ, styleID
                    )
            self.coord_to_path_checkdirs(coord, layer)
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
    #  only check path
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention:
    #  \.googlemaps\tiles\15\0\1\0\1.png
    #  We only have 2 levels for one axis
    #  at most 1024 files in one dir
    # private
    def coord_to_path(self, tile_coord, layer):
        path = os.path.join(self.mapServ_inst.configpath, 
                            LAYER_DIRS[layer],
                            str(tile_coord[2]),
                            str(tile_coord[0] / 1024),
                            str(tile_coord[0] % 1024),
                            str(tile_coord[1] / 1024),
                            str(tile_coord[1] % 1024) + ".png"
                            )
        return path

    # create path if doesn't exists
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention:
    #  \.googlemaps\tiles\15\0\1\0\1.png
    #  We only have 2 levels for one axis
    #  at most 1024 files in one dir
    # private
    def coord_to_path_checkdirs(self, tile_coord, layer):
        self.lock.acquire()
        path = os.path.join(self.mapServ_inst.configpath, LAYER_DIRS[layer])
        path = fileUtils.check_dir(path)
        path = fileUtils.check_dir(path, '%d' % tile_coord[2])
        path = fileUtils.check_dir(path, "%d" % (tile_coord[0] / 1024))
        path = fileUtils.check_dir(path, "%d" % (tile_coord[0] % 1024))
        path = fileUtils.check_dir(path, "%d" % (tile_coord[1] / 1024))
        self.lock.release()
        return os.path.join(path, "%d.png" % (tile_coord[1] % 1024))


    ## Get the tile for the given location
    # Validates the given tile coordinates and,
    # returns tile coords if successfully retrieved
    def get_tile(self, tcoord, layer, online, force_update, mapServ, styleID):
        if (MAP_MIN_ZOOM_LEVEL <= tcoord[2] <= MAP_MAX_ZOOM_LEVEL):
            world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - tcoord[2])
            if (tcoord[0] > world_tiles) or (tcoord[1] > world_tiles):
                return None
            ## Tiles dir structure
            filename = self.coord_to_path(tcoord, layer)
            # print "tCoord to path: %s" % filename
            if self.get_png_file(tcoord, layer, filename, online,
                                    force_update, mapServ, styleID):
                return (tcoord, layer)
        return None


    ## Export tiles to one big map
    #  tcoord are the tile coordinates of the upper left tile
    def do_export(self, tcoord, layer, online, mapServ, styleID, size):
        from PIL import Image
        # Convert given size to a tile size factor
        xFact = int(size[0]/TILES_WIDTH)
        yFact = int(size[1]/TILES_HEIGHT)
        # Initialise the image
        result = Image.new("RGBA", (xFact* TILES_WIDTH, yFact* TILES_HEIGHT))
        x = 0
        for i in range(tcoord[0], tcoord[0] + xFact):
            y = 0
            for j in range(tcoord[1], tcoord[1] + yFact):
                filename = self.get_file(
                    (i,j,tcoord[2]), layer, online, False, mapServ, styleID
                )
                if filename:
                    im = Image.open(filename)
                    result.paste(im, (x* TILES_WIDTH, y* TILES_HEIGHT))
                y += 1
            x += 1
        result.save("map.png")
