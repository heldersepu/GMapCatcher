import os
import sys
import gtk
import gtk.gdk
import traceback

import googleMaps
import tilesrepos
import fileUtils

from mapConst import *

LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles"]

class TilesReposFS(tilesrepos.TilesRepos):
    
    def __init__(self, gm, params = None):
        self.google_maps_instance = gm
        self.tilespath = params[0]

        if not os.path.isdir(self.tilespath):
            os.mkdir(self.tilespath)

    def coord_to_path(self, coord):
        self.google_maps_instance.lock.acquire()
        ## at most 1024 files in one dir
        ## We only have 2 levels for one axis
        self.tilespath=os.path.join(self.google_maps_instance.configpath,LAYER_DIRS[coord[3]])
        path = fileUtils.check_dir(self.tilespath)
        path = fileUtils.check_dir(self.tilespath, '%d' % coord[2])
        path = fileUtils.check_dir(path, "%d" % (coord[0] / 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[0] % 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[1] / 1024))
        self.google_maps_instance.lock.release()
        return os.path.join(path, "%d.png" % (coord[1] % 1024))
        

    def get_png_file(self, coord, filename, online, force_update):
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
        #if not self.switch_layer(self.layer,online):
        #        return False

        try:
            oa = self.google_maps_instance.get_tile_from_url(coord)

            file = open( filename, 'wb' )
            file.write( oa['data'] )
            file.close()
            return True
        except KeyboardInterrupt:
            raise
        except:
            print traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print '\tdownload failed -', sys.exc_info()[0]
        return False

    
    
    def get_file(self, coord, online, force_update):
        if (MAP_MIN_ZOOM_LEVEL <= coord[2] <= MAP_MAX_ZOOM_LEVEL):
            world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - coord[2])
            if (coord[0] > world_tiles) or (coord[1] > world_tiles):
                return None
            ## Tiles dir structure
            filename = self.coord_to_path(coord)
            # print "Coord to path: %s" % filename
            if (self.get_png_file(coord, filename, online, force_update)):
                return filename
                    


    def get_tile_pixbuf(self, coord, online, force_update ):
        w = gtk.Image()
        # print ("get_tile_pixbuf: zl: %d, coord: %d, %d") % (coord)
        filename = self.get_file(coord, online, force_update)
        if (filename == None):
            filename = 'missing.png'
            w.set_from_file('missing.png')
        else:
            w.set_from_file(filename)

        try:
            return w.get_pixbuf()
        except ValueError:
            print "File corrupted: %s" % filename
            os.remove(filename)
            w.set_from_file('missing.png')
            return w.get_pixbuf()
