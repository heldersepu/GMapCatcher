## @package src.googleMaps
# All the interaction with google.com

import os
import re
import gtk
import sys
import urllib
import openanything
import fileUtils
import tilesreposfs
import openStreetMaps

from mapConst import *
from gobject import TYPE_STRING

## All the interaction with Google maps.
#  Other map services can be added see def get_url_from_coord
class GoogleMaps:

    # coord = (lat, lng, zoom_level)

    @staticmethod
    def set_zoom(intZoom):
        if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
            return intZoom
        else:
            return 10


    ## Parse maps.google.com/maps.
    #  google always change this page and map api, we use a specific
    #  method to do the parser work.
    #  the return value is a url pattern like this:
    #  http://mt%d.google.com/vt/lyrs=t@110&hl=en&x=%i&y=%i&z=%i
    def parse_start_page(self, layer, html):
        # first, we check the uniform url pattern.
        # after Oct. 10, 2009, google use a uniform url:
        #
        # http://mt%d.google.com/vt/lyrs=??@110&hl=en&x=%i&y=%i&z=%i
        #
        # to fetch map, satellite and terrain tiles, where
        # ?? is 'm' for map, 's' for satellite and 't' for terrain.
        # google also use an 'h' layer for its route and labels.
        #
        # although google actually use
        #
        # http://mt0.google.com/vt/v=w2p.110&hl=en&x=%i&y=%i&z=%i
        #
        # for terrain, the uniform URL pattern works.
        # we first check the existance of the uniform URL pattern,
        # if not, we fall back to the old method.

        # check for pattern:
        # 'http://mt[0-9].google.com/vt/lyrs'

        upattern = 'http://mt[0-9].google.com/vt/lyrs\\\\x3dm@([0-9]+)'
        p = re.compile(upattern)
        m = p.search(html)

        ## if exist, we use upattern to form the retval
        if m:
            head_str = 'http://mt%d.google.com/vt/lyrs='
            layer_str = layer + '@' + m.group(1)
            match_str = '&hl=en&x=%i&y=%i&zoom=%i'
            retval = head_str + layer_str + match_str
            return retval;


        # if doesn't exist, we fall back to old method

        # List of patterns add more as needed
        paList = ['http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v=([a-z0-9.]+)&',
                  'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]lyrs=([a-z@0-9.]+)&',
                  'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v\\\\x3d([a-z0-9.]+)\\\\x26']
        for srtPattern in paList:
            p = re.compile(srtPattern)
            m = p.search(html)
            if m: break
        if not m:
            print "Cannot parse result"
            return None

        return 'http://%s%%d.google.com/%s/v=%s&hl=en&x=%%i&y=%%i&zoom=%%i' % tuple(m.groups())

    ## Returns a template URL for the GoogleMaps
    def layer_url_template(self, layer, online):
        if layer not in self.known_layers:
            self.version_string=None
            if not online:
                return None
            map_server_query = ["", "h", "p"]
            layers_name = ["m", "s", "t"]

            oa = openanything.fetch(
                'http://maps.google.com/maps?t=' + map_server_query[layer])

            if oa['status'] != 200:
                print "Trying to fetch http://maps.google.com/maps but failed"
                return None
            html = oa['data']

            self.known_layers[layer] = self.parse_start_page(layers_name[layer], html)
        return self.known_layers[layer]

    ## Returns the URL to the GoogleMaps tile
    def get_url(self, counter, coord, layer, online):
        template = self.layer_url_template(layer, online)
        if template:
            return template % (counter, coord[0], coord[1], coord[2])

    def read_locations(self):
        self.locations = fileUtils.read_file('location', self.locationpath)

    def write_locations(self):
        fileUtils.write_file('location', self.locationpath, self.locations)

    def __init__(self, configpath=None):
        configpath = os.path.expanduser(configpath or DEFAULT_PATH)
        self.mt_counter=0
        self.configpath = fileUtils.check_dir(configpath)
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.known_layers = {}
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
        print 'downloading the following location:', location
        try:
            oa = openanything.fetch( 'http://maps.google.com/maps?q=' +
                urllib.quote_plus(location) )
        except Exception:
            return 'error=Can not connect to http://maps.google.com'
        if oa['status']!=200:
            return 'error=Can not connect to http://maps.google.com'

        m = 0
        html = oa['data']
        if html.find('We could not understand the location') < 0:
            # List of patterns to look for the location name
            paList = ['laddr:"([^"]+)"',
                      'daddr:"([^"]+)"']
            for srtPattern in paList:
                p = re.compile(srtPattern)
                m = p.search(html)
                if m: break

        if m:
            location = m.group(1)
        else:
            return 'error=Location %s not found' % location

        # List of patterns to look for the latitude & longitude
        paList = ['center:{lat:([0-9.-]+),lng:([0-9.-]+)}.*zoom:([0-9.-]+)',
                  'markers:.*lat:([0-9.-]+),lng:([0-9.-]+).*laddr:',
                  'dtlsUrl:.*x26sll=([0-9.-]+),([0-9.-]+).*x26sspn']

        for srtPattern in paList:
            p = re.compile(srtPattern)
            m = p.search(html)
            if m: break

        if m:
            lat, lng = float(m.group(1)), float(m.group(2))
            zoom = 10
            if m.group(0).find('zoom:') != -1:
                zoom = self.set_zoom(MAP_MAX_ZOOM_LEVEL - int(m.group(3)))
            else:
                p = re.compile('center:.*zoom:([0-9.-]+).*mapType:')
                m = p.search(html)
                if m:
                    zoom = self.set_zoom(MAP_MAX_ZOOM_LEVEL - int(m.group(1)))
            location = unicode(location, errors='ignore')
            self.locations[location] = (lat, lng, zoom)
            self.write_locations()
            return location
        else:
            return 'error=Unable to get latitude and longitude of %s ' % location

    ## Get the URL for the given coordinates
    # In this function we point to the proper map service
    def get_url_from_coord(self, coord, layer, online, mapServ):
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        if mapServ == MAP_SERVERS[OSM] and (layer == LAYER_MAP):
            return openStreetMaps.get_url(self.mt_counter, coord)
        else:
            return self.get_url(self.mt_counter, coord, layer, online)

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
