## @package gmapcatcher.tilesRepo.tilesRepoMGMaps
# This modul provides filebased tile repository functions
#
# Usage:
#
# - constructor requires MapServ instance, because method
#  'get_tile_from_coord' is provided in the MapServ
#


import os
import gmapcatcher.lrucache as lrucache
import gmapcatcher.mapPixbuf as mapPixbuf
import gmapcatcher.fileUtils as fileUtils

from threading import Lock
from gmapcatcher.mapConst import *
from tilesRepo import TilesRepository


class TilesRepositoryMGMaps(TilesRepository):

    def __init__(self, MapServ_inst, configpath):
        TilesRepository.__init__(self, MapServ_inst, configpath)
        self.set_repository_path(configpath)
        self.tile_cache = lrucache.LRUCache(1000)
        self.mapServ_inst = MapServ_inst
        self.lock = Lock()
        self.missingPixbuf = mapPixbuf.missing()

    def finish(self):
        # last command in finish
        TilesRepository.finish(self)

    ## Sets new repository path to be used for storing tiles
    def set_repository_path(self, newpath):
        self.configpath = newpath
        self.create_conf_file(newpath)

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
                    pixbuf = mapPixbuf.image_data_fs(filename)
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
        remove_tile = False
        if (force_update and online):
            remove_tile = fileUtils.is_old(filename, conf.force_update_days)

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
                fileUtils.delete_old(filename, conf.force_update_days)
            file = open(filename, 'wb')
            file.write(data)
            file.close()

            return True
        except KeyboardInterrupt:
            raise
        except Exception, excInst:
            print excInst
        return False

    # retrieve tile directly from repository
    def get_plain_tile(self, coord, layer):
        if not self.is_tile_in_local_repos(coord, layer):
            raise tileNotInRepository(str((coord, layer)))

        filename = self.coord_to_path(coord, layer)
        thefile = open(filename, 'rb')
        ret = thefile.read()
        thefile.close()
        return ret

    def store_plain_tile(self, coord, layer, tiledata):
        filename = self.coord_to_path_checkdirs(coord, layer)
        file = open(filename, 'wb')
        file.write(tiledata)
        file.close()

    ## Calculate the hash
    def calc_v2_hash(self, x, y, hash_size=97):
        return str((x * 256 + y) % hash_size)

    ## Return the absolute path to a tile
    #  only check path
    #  tile_coord = (tile_X, tile_Y, zoom_level)
    #  smaple of the Naming convention:
    #  \MGMapsCache\YahooMap_1\63\1_1.mgm
    def coord_to_path(self, tile_coord, layer):
        return os.path.join(
            self.configpath,
            "Yahoo" + MAP_SERVICES[layer]["layerName"][:3] +
            "_" + str(MAP_MAX_ZOOM_LEVEL - tile_coord[2]),
            self.calc_v2_hash(tile_coord[0], tile_coord[1]),
            str(tile_coord[0]) + "_" + str(tile_coord[1]) + ".mgm"
        )

    ## create path if doesn't exists
    def coord_to_path_checkdirs(self, tile_coord, layer):
        self.lock.acquire()
        path = fileUtils.check_dir(self.configpath)
        path = fileUtils.check_dir(
            path,
            "Yahoo" + MAP_SERVICES[layer]["layerName"][:3] +
            "_" + str(MAP_MAX_ZOOM_LEVEL - tile_coord[2])
        )
        path = fileUtils.check_dir(
            path, self.calc_v2_hash(tile_coord[0], tile_coord[1])
        )
        self.lock.release()
        return os.path.join(path, "%d_%d.mgm" % (tile_coord[0], tile_coord[1]))

    ## Create the MGMaps conf fie
    def create_conf_file(self, dir):
        fileName = os.path.join(dir, 'cache.conf')
        if not os.path.isfile(fileName):
            file = open(fileName, 'w')
            file.write('version=3\n')
            file.write('tiles_per_file=1\n')
            file.write('hash_size=97\n')
            file.write('center=0,0,1,YahooMap')
            file.close()
