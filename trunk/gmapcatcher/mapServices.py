## @package gmapcatcher.mapServices
# All the interaction with the map services

import gtk
from mapConst import *
from gobject import TYPE_STRING

import os
import mapUtils
import fileUtils
import openanything
import tilesRepo.Factory as trFactory
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
        from mapServers import googleMaps
        location, coord = googleMaps.search_location(location)
        location = mapUtils.html_decode(location)
        if (location[:6] != "error="):
            self.locations[location] = coord
            self.write_locations()
        return location

    ## Get the Map Server package
    def get_map_server(self, map_service):
        map_server = None
        if map_service == MAP_SERVERS[VIRTUAL_EARTH]:
            import mapServers.virtualEarth as map_server
        elif map_service == MAP_SERVERS[OSM]:
            import mapServers.openStreetMaps as map_server
        elif map_service == MAP_SERVERS[STAMEN]:
            import mapServers.stamenMaps as map_server
        elif map_service == MAP_SERVERS[REFUGES]:
            import mapServers.refugesInfo as map_server
        elif map_service == MAP_SERVERS[CLOUDMADE]:
            import mapServers.cloudMade as map_server
        elif map_service == MAP_SERVERS[YAHOO]:
            import mapServers.yahoo as map_server
        elif map_service == MAP_SERVERS[INFO_FREEWAY]:
            import mapServers.informationFreeway as map_server
        elif map_service == MAP_SERVERS[OPENCYCLEMAP]:
            import mapServers.openCycleMap as map_server
        elif map_service == MAP_SERVERS[GOOGLE_MAKER]:
            import mapServers.googleMapMaker as map_server
        elif map_service == MAP_SERVERS[YANDEX]:
            import mapServers.yandex as map_server
        elif map_service == MAP_SERVERS[SEZNAM]:
            import mapServers.seznam as map_server
        elif map_service == MAP_SERVERS[SEZNAM_HIKING]:
            import mapServers.seznamHiking as map_server
        elif map_service == MAP_SERVERS[SEZNAM_CYCLO]:
            import mapServers.seznamCyclo as map_server
        elif map_service == MAP_SERVERS[SEZNAM_HIST]:
            import mapServers.seznamHist as map_server
        elif map_service == MAP_SERVERS[OPENSEAMAP]:
            import mapServers.openSeaMap as map_server
        elif map_service == MAP_SERVERS[ENIRO]:
            import mapServers.eniro as map_server
        elif map_service == MAP_SERVERS[NOKIA]:
            import mapServers.nokia as map_server
        elif map_service == MAP_SERVERS[SKYVECTOR_WORLD_VFR]:
            import mapServers.WorldVFR as map_server
        elif map_service == MAP_SERVERS[SKYVECTOR_WORLD_HI]:
            import mapServers.WorldHI as map_server
        elif map_service == MAP_SERVERS[SKYVECTOR_WORLD_LO]:
            import mapServers.WorldLO as map_server
        elif map_service == MAP_SERVERS[MAPS_FOR_FREE]:
            import mapServers.maps4free as map_server
        elif map_service == MAP_SERVERS[GOOGLE]:
            import mapServers.googleMaps as map_server
        return map_server

    ## Get the URL for the given coordinates
    # In this function we point to the proper map service
    def get_url_from_coord(self, coord, layer, conf):
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        map_server = self.get_map_server(conf.map_service)
        return map_server.get_url(self.mt_counter, coord, layer, conf)

    ## Get the max zoom if defined in the map server
    def get_max_zoom(self, map_service):
        try:
            map_server = self.get_map_server(map_service)
            return map_server.max_zoom
        except:
            return MAP_MAX_ZOOM_LEVEL - 1

    ## Get the min zoom if defined in the map server
    def get_min_zoom(self, map_service):
        try:
            map_server = self.get_map_server(map_service)
            return map_server.min_zoom
        except:
            return MAP_MIN_ZOOM_LEVEL

    ## Get skip zooms if defined in the map server
    def get_skip_zooms(self, map_service):
        try:
            map_server = self.get_map_server(map_service)
            return map_server.skip_zooms
        except:
            return []

    def get_hybrid_background(self, layer, map_service):
        try:
            map_server = self.get_map_server(map_service)
            return map_server.hybrid_background[layer - LAYER_HYB]
        except:
            return LAYER_SAT

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
