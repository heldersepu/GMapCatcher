## @package gmapcatcher.mapServices
# All the interaction with the map services

import gtk
import StringIO
from mapConst import *
from gobject import TYPE_STRING

import os
import mapUtils
import fileUtils
import openanything
import tilesRepo.Factory as trFactory

import mapServers.googleMaps as googleMaps
import mapServers.openStreetMaps as openStreetMaps
import mapServers.cloudMade as cloudMade
import mapServers.yahoo as yahoo
import mapServers.informationFreeway as informationFreeway
import mapServers.openCycleMap as openCycleMap
import mapServers.googleMapMaker as googleMapMaker
import mapServers.virtualEarth as virtualEarth
import mapServers.yandex as yandex
import mapServers.seznam as seznam
import mapServers.seznamHiking as seznamHiking
import mapServers.seznamCyclo as seznamCyclo
import mapServers.seznamHist as seznamHist
import mapServers.stamenMaps as stamenMaps
import mapServers.refugesInfo as refugesInfo
import mapServers.openSeaMap as openSeaMap
import mapServers.eniro as eniro
import mapServers.nokia as nokia

from threading import Timer


## All the interaction with the map services.
#  Other map services can be added see def get_url_from_coord
class MapServ:
    # coord = (lat, lng, zoom_level)
    exThread = None

    def read_locations(self):
        self.locations = fileUtils.read_file('location', self.locationpath)

    def write_locations(self):
        fileUtils.write_file('location', self.locationpath, self.locations)

    def initLocations(self, conf):
        configpath = os.path.expanduser(conf.init_path or DEFAULT_PATH)
        self.mt_counter = 0
        self.configpath = fileUtils.check_dir(configpath)
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.locations = {}

        if conf.repository_type is None:
            conf.repository_type = DEFAULT_REPOS_TYPE

        if self.tile_repository is not None:
            self.tile_repository.finish()
            self.tile_repository = None

        self.tile_repository = trFactory.get_tile_repository(self, conf)

    def __init__(self, conf):
        self.tile_repository = None
        self.initLocations(conf)

        if (os.path.exists(self.locationpath)):
            self.read_locations()
        else:
            self.write_locations()

    def finish(self):
        self.tile_repository.finish()
        if self.exThread:
            self.exThread.cancel()

    def get_locations(self):
        return self.locations

    def search_location(self, location):
        location, coord = googleMaps.search_location(location)
        location = mapUtils.html_decode(location)
        if (location[:6] != "error="):
            self.locations[location] = coord
            self.write_locations()
        return location

    ## Get the URL for the given coordinates
    # In this function we point to the proper map service
    def get_url_from_coord(self, coord, layer, conf):
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        if conf.map_service == MAP_SERVERS[VIRTUAL_EARTH]:
            return virtualEarth.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[OSM]:
            return openStreetMaps.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[STAMEN]:
            return stamenMaps.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[REFUGES]:
            return refugesInfo.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[CLOUDMADE]:
            return cloudMade.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[YAHOO]:
            return yahoo.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[INFO_FREEWAY]:
            return informationFreeway.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[OPENCYCLEMAP]:
            return openCycleMap.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[GOOGLE_MAKER]:
            return googleMapMaker.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[YANDEX]:
            return yandex.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[SEZNAM]:
            return seznam.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[SEZNAM_HIKING]:
            return seznamHiking.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[SEZNAM_CYCLO]:
            return seznamCyclo.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[SEZNAM_HIST]:
            return seznamHist.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[OPENSEAMAP]:
            return openSeaMap.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[ENIRO]:
            return eniro.get_url(self.mt_counter, coord, layer, conf)
        elif conf.map_service == MAP_SERVERS[NOKIA]:
            return nokia.get_url(self.mt_counter, coord, layer, conf)
        else:
            return googleMaps.get_url(self.mt_counter, coord, layer, conf)

    def get_tile_from_coord(self, coord, layer, conf):
        href = self.get_url_from_coord(coord, layer, conf)
        if href:
            try:
                #print 'downloading:', href
                oa = openanything.fetch(href)
                if oa['status'] == 200:
                    return oa['data']
                else:
                    raise RuntimeError, ("HTTP Reponse is: " + str(oa['status']) + ' in ' + str(href),)
            except:
                raise

    ## Get the tile for the given location
    #  Validates the given tile coordinates and,
    #  returns tile coords if successfully retrieved
    def get_tile(self, tcoord, layer, online, force_update, conf):
        if (MAP_MIN_ZOOM_LEVEL <= tcoord[2] <= MAP_MAX_ZOOM_LEVEL):
            world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - tcoord[2])
            if (tcoord[0] > world_tiles) or (tcoord[1] > world_tiles):
                return None
            if self.tile_repository.get_png_file(tcoord, layer, online,
                                    force_update, conf):
                return (tcoord, layer)
        return None

    def is_tile_in_local_repos(self, coord, layer):
        return self.tile_repository.is_tile_in_local_repos(coord, layer)

    ## Combine tiles to one big map
    def do_combine(self, tPoint, zoom, layer, online, conf, size):
        try:
            from PIL import Image

            # Initialise the image
            result = Image.new("RGBA", size)
            x = 0
            for i in range(tPoint['xLow'], tPoint['xHigh']):
                y = 0
                for j in range(tPoint['yLow'], tPoint['yHigh']):
                    if self.get_tile((i, j, zoom), layer, online, False, conf):
                        pb = self.load_pixbuf((i, j, zoom), layer, False)
                        width, height = pb.get_width(), pb.get_height()

                        result.paste(
                            Image.fromstring("RGB", (width, height), pb.get_pixels()),
                            (x * TILES_WIDTH, y * TILES_HEIGHT)
                        )
                    y += 1
                x += 1
            fileName = tPoint['FileName']
            result.save(fileName)
            return fileName
        except Exception, inst:
            return str(inst)

    ## Export tiles to one big map
    def do_export(self, tPoint, zoom, layer, online, conf, size, callback):
        def exportThread():
            fileName = self.do_combine(
                tPoint, zoom, layer, online, conf, size
            )
            callback(None, fileName)
        self.exThread = Timer(0, exportThread)
        self.exThread.start()


    def load_pixbuf(self, coord, layer, force_update):
        return self.tile_repository.load_pixbuf(coord, layer, force_update)

    def completion_model(self, strAppend=''):
        store = gtk.ListStore(TYPE_STRING)
        for str in sorted(self.locations.keys()):
            iter = store.append()
            store.set(iter, 0, str + strAppend)
        if strAppend == '' and os.path.exists('poi.db'):
            import sqlite3
            dbconn = sqlite3.connect('poi.db')
            dbcursor = dbconn.cursor()
            dbcursor.execute("SELECT location FROM locations")
            for row in dbcursor:
                iter = store.append()
                store.set(iter, 0, row[0])
        return store
