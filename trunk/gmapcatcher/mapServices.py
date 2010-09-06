## @package gmapcatcher.mapServices
# All the interaction with the map services

from mapConst import *
if IS_GTK:
    import gtk
    from gobject import TYPE_STRING
import sys
import fileUtils
import tilesRepoFactory
import openanything

import mapServers.googleMaps as googleMaps
import mapServers.openStreetMaps as openStreetMaps
import mapServers.cloudMade as cloudMade
import mapServers.yahoo as yahoo
import mapServers.informationFreeway as informationFreeway
import mapServers.openCycleMap as openCycleMap
import mapServers.googleMapMaker as googleMapMaker
import mapServers.virtualEarth as virtualEarth

from threading import Timer



class MapServException(Exception):
    pass

## All the interaction with the map services.
#  Other map services can be added see def get_url_from_coord
class MapServ:
    # coord = (lat, lng, zoom_level)
    exThread = None

    def read_locations(self):
        self.locations = fileUtils.read_file('location', self.locationpath)

    def write_locations(self):
        fileUtils.write_file('location', self.locationpath, self.locations)

    def initLocations(self, configpath, tilerepostype):
        configpath = os.path.expanduser(configpath or DEFAULT_PATH)
        self.mt_counter=0
        self.configpath = fileUtils.check_dir(configpath)
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.locations = {}

        if tilerepostype is None:
            tilerepostype = DEFAULT_REPOS_TYPE
        self.tile_repository = tilesRepoFactory.get_tile_repository(self, configpath, tilerepostype)

    def __init__(self, configpath=None, tilerepostype=None):
        self.tile_repository = None
        self.initLocations(configpath, tilerepostype)


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
        if (location[:6] != "error="):
            self.locations[location] = coord
            self.write_locations()
        return location

    ## Get the URL for the given coordinates
    # In this function we point to the proper map service
    def get_url_from_coord(self, coord, layer, conf):
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        print
        try:
            if not conf.oneDirPerMap:
                if conf.map_service == MAP_SERVERS[VIRTUAL_EARTH] and (layer != LAYER_TERRAIN):
                    return virtualEarth.get_url(self.mt_counter, coord, layer)
                elif conf.map_service == MAP_SERVERS[OSM] and (layer == LAYER_MAP):
                    return openStreetMaps.get_url(self.mt_counter, coord)
                elif conf.map_service == MAP_SERVERS[CLOUDMADE] and (layer == LAYER_MAP):
                    return cloudMade.get_url(self.mt_counter, coord, styleID)
                elif conf.map_service == MAP_SERVERS[YAHOO] and (layer != LAYER_TERRAIN):
                    return yahoo.get_url(self.mt_counter, coord, layer)
                elif conf.map_service == MAP_SERVERS[INFO_FREEWAY] and (layer == LAYER_MAP):
                    return informationFreeway.get_url(self.mt_counter, coord)
                elif conf.map_service == MAP_SERVERS[OPENCYCLEMAP] and (layer == LAYER_MAP):
                    return openCycleMap.get_url(self.mt_counter, coord)
                elif conf.map_service == MAP_SERVERS[GOOGLE_MAKER] and (layer == LAYER_MAP):
                    return googleMapMaker.get_url(self.mt_counter, coord)
                else:
                    return googleMaps.get_url(self.mt_counter, coord, layer, conf.language)

            if (MAP_SERVICES[layer]["TextID"] in ["veter", "vemap", "vesat"]):
                return virtualEarth.get_url(self.mt_counter, coord, MAP_SERVICES[layer]["ID"])
            elif (MAP_SERVICES[layer]["TextID"] == "osmmap"):
                return openStreetMaps.get_url(self.mt_counter, coord)
            elif (MAP_SERVICES[layer]["TextID"] == "cmmap"):
                return cloudMade.get_url(self.mt_counter, coord, conf.cloudMade_styleID)
            elif (MAP_SERVICES[layer]["TextID"] in ["yter", "ymap", "yhyb"]):
                return yahoo.get_url(self.mt_counter, coord, MAP_SERVICES[layer]["ID"])
            elif (MAP_SERVICES[layer]["TextID"] == "ifwmap"):
                return informationFreeway.get_url(self.mt_counter, coord)
            elif (MAP_SERVICES[layer]["TextID"] == "ocmmap"):
                return openCycleMap.get_url(self.mt_counter, coord)
            elif (MAP_SERVICES[layer]["TextID"] == "gmmmap"):
                return googleMapMaker.get_url(self.mt_counter, coord)
            else:
                return googleMaps.get_url(self.mt_counter, coord, layer, conf.language)

        except KeyError:
            raise MapServException("Invalid layer ID: " + str(layer) )


    def get_tile_from_coord(self, coord, layer, conf):
        href = self.get_url_from_coord(coord, layer, conf)
        if href:
            try:
                print 'downloading:', href
                oa = openanything.fetch(href)
                if oa['status']==200:
                    return oa['data']
                else:
                    raise RuntimeError, ("HTTP Reponse is: " + str(oa['status']),)
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
                    if self.get_tile((i,j,zoom), layer, online, False, conf):
                        pb = self.load_pixbuf((i,j,zoom), layer, False)
                        width, height = pb.get_width(), pb.get_height()

                        result.paste(
                            Image.fromstring("RGB", (width,height), pb.get_pixels()),
                            (x* TILES_WIDTH, y* TILES_HEIGHT)
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
        if IS_GTK:
            store = gtk.ListStore(TYPE_STRING)
            for str in sorted(self.locations.keys()):
                iter = store.append()
                store.set(iter, 0, str + strAppend)
        return store
