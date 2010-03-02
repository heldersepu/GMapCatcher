## @package src.mapServices
# All the interaction with the map services

import os
import gtk
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

from mapConst import *
from threading import Timer
from gobject import TYPE_STRING

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
        print "Debug: confpath: " + configpath + ", repostype: " + str(tilerepostype)
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
        print location
        location, coord = googleMaps.search_location(location)
        print location
        if (location[:6] != "error="):
            self.locations[location] = coord
            self.write_locations()
        return location

    ## Get the URL for the given coordinates
    # In this function we point to the proper map service
    def get_url_from_coord(self, coord, layer, mapServ, styleID):
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS

        try:
            if (MAP_SERVICES[layer]["TextID"] == "gmap"):
                return googleMaps.get_url(self.mt_counter, coord, layer)
            
            elif (MAP_SERVICES[layer]["TextID"] == "gsat"):
                return googleMaps.get_url(self.mt_counter, coord, layer)
    
            elif (MAP_SERVICES[layer]["TextID"] == "gter"):
                return googleMaps.get_url(self.mt_counter, coord, layer)
            
            elif (MAP_SERVICES[layer]["TextID"] == "osmmap"):
                return openStreetMaps.get_url(self.mt_counter, coord)
    
            elif (MAP_SERVICES[layer]["TextID"] == "cmmap"):
                return cloudMade.get_url(self.mt_counter, coord, styleID)
    
            elif (MAP_SERVICES[layer]["TextID"] == "yter"):
                return yahoo.get_url(self.mt_counter, coord, layer)
    
            elif (MAP_SERVICES[layer]["TextID"] == "ifwmap"):
                return informationFreeway.get_url(self.mt_counter, coord)
    
            elif (MAP_SERVICES[layer]["TextID"] == "ocmmap"):
                return openCycleMap.get_url(self.mt_counter, coord)
    
            elif (MAP_SERVICES[layer]["TextID"] == "gmmmap"):
                return googleMapMaker.get_url(self.mt_counter, coord)
    
            elif (MAP_SERVICES[layer]["TextID"] == "veter"):
                return virtualEarth.get_url(self.mt_counter, coord, layer)

            elif (MAP_SERVICES[layer]["TextID"] == "ymap"):
                return yahoo.get_url(self.mt_counter, coord, layer)

            elif (MAP_SERVICES[layer]["TextID"] == "vemap"):
                return virtualEarth.get_url(self.mt_counter, coord, layer)

            elif (MAP_SERVICES[layer]["TextID"] == "vesat"):
                return virtualEarth.get_url(self.mt_counter, coord, layer)
    
        except KeyError:
            raise MapServException("Invalid layer ID: " + str(layer) )

    
    def get_tile_from_coord(self, coord, layer, mapServ, styleID):
        href = self.get_url_from_coord(coord, layer, mapServ, styleID)
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

    def get_tile(self, coord, layer, online, force_update,
                                mapServ='Google', styleID =1):
        return self.tile_repository.get_tile(
                    coord, layer, online, force_update, mapServ, styleID
                )

    def remove_old_tile(self, coord, layer):
        return self.tile_repository.remove_old_tile(coord, layer)

    def is_tile_in_local_repos(self, coord, layer):
        return self.tile_repository.is_tile_in_local_repos(coord, layer)


    ## Call the do_export in the tile_repository
    # Export tiles to one big map
    def do_export(self, tcoord, layer, online, mapServ, styleID, size):
        def exportThread():
            self.tile_repository.do_export(
                tcoord, layer, online, mapServ, styleID, size
            )
            print "Export completed!"
        self.exThread = Timer(0, exportThread)
        self.exThread.start()


    def load_pixbuf(self, coord, layer, force_update):
        return self.tile_repository.load_pixbuf(coord, layer, force_update)

    

    def completion_model(self, strAppend=''):
        store = gtk.ListStore(TYPE_STRING)
        for str in sorted(self.locations.keys()):
            iter = store.append()
            store.set(iter, 0, str + strAppend)
        return store
