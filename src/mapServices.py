## @package src.mapServices
# All the interaction with the map services

import os
import gtk
import sys
import fileUtils
import tilesreposfs
import openanything
import googleMaps
import openStreetMaps
import cloudMade

from mapConst import *
from gobject import TYPE_STRING

## All the interaction with the map services.
#  Other map services can be added see def get_url_from_coord
class MapServ:

    # coord = (lat, lng, zoom_level)

    def read_locations(self):
        self.locations = fileUtils.read_file('location', self.locationpath)

    def write_locations(self):
        fileUtils.write_file('location', self.locationpath, self.locations)

    def __init__(self, configpath=None):
        configpath = os.path.expanduser(configpath or DEFAULT_PATH)
        self.mt_counter=0
        self.configpath = fileUtils.check_dir(configpath)
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.locations = {}

        #implementation of the method is set in maps.py:__init__()
        self.tile_repository = tilesreposfs.TilesRepositoryFS(self)

        if (os.path.exists(self.locationpath)):
            self.read_locations()
        else:
            self.write_locations()

    def finish(self):
        self.tile_repository.finish()

    def get_locations(self):
        return self.locations

    def search_location(self, location):
        print location
        location, coord = googleMaps.search_location(location)
        print location
        if (location[:6] != "error="):
            self.locations[location] = coord
            self.write_locations()
        return location
        
    ## Get the URL for the given coordinates
    # In this function we point to the proper map service
    def get_url_from_coord(self, coord, layer, online, mapServ='Google'):
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        if mapServ == MAP_SERVERS[OSM] and (layer == LAYER_MAP):
            return openStreetMaps.get_url(self.mt_counter, coord)
        elif mapServ == MAP_SERVERS[CLOUDMADE] and (layer == LAYER_MAP):
            return cloudMade.get_url(self.mt_counter, coord)
        else:
            return googleMaps.get_url(self.mt_counter, coord, layer, online)

    def get_tile_from_coord(self, coord, layer, online, mapServ='Google'):
        href = self.get_url_from_coord(coord, layer, online, mapServ)
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


    def get_file(self, coord, layer, online, force_update, mapServ='Google'):
        return self.tile_repository.get_file(coord, layer, online,
                                                force_update, mapServ)

    def load_pixbuf(self, coord, layer, force_update):
        return self.tile_repository.load_pixbuf(coord, layer, force_update)


    def completion_model(self, strAppend=''):
        store = gtk.ListStore(TYPE_STRING)
        for str in sorted(self.locations.keys()):
            iter = store.append()
            store.set(iter, 0, str + strAppend)
        return store
