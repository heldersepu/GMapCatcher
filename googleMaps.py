import os
import re
import gtk
import sys
import urllib
import openanything
import fileUtils
import tilesreposfs

from time import time
from mapConst import *
from threading import Lock
from gobject import TYPE_STRING

class GoogleMaps:

    # coord = (lat, lng, zoom_level, map_layer_type)
    map_server_query=["","h","p"]

    def set_zoom(self, intZoom):
        if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
            return intZoom
        else:
            return 10

    def switch_layer(self,new_layer,online):
        if self.layer==new_layer and (not online or self.version_string!=None):
            return True
        self.layer=new_layer
        if new_layer not in self.known_layers:
            self.version_string=None
            if not online:
                return True
            try: 
                oa = openanything.fetch('http://maps.google.com/maps?t=' + \
                                        self.map_server_query[new_layer])
            except Exception:
                print "Can not open http://maps.google.com/maps"
                return False
            if oa['status'] != 200:
                print "Trying to fetch http://maps.google.com/maps but failed"
                return False
            html=oa['data']
            p=re.compile(
                'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v=([a-z0-9.]+)&')
            m=p.search(html)
            if not m:
                print "Cannot parse result"
                return False
            self.known_layers[new_layer]=tuple(m.groups())
        self.mt_prefix,self.mt_suffix,self.version_string=self.known_layers[new_layer]
        return True
    
    def read_locations(self):
        self.locations = fileUtils.read_file('location', self.locationpath)

    def write_locations(self):
        fileUtils.write_file('location', self.locationpath, self.locations)

    def __init__(self, layer=LAYER_MAP, configpath=None):
        configpath = os.path.expanduser(configpath or "~/.googlemaps")
        self.lock = Lock()
        self.mt_counter=0
        self.configpath = fileUtils.check_dir(configpath)
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.layer = None
        self.known_layers = {}
        self.locations = {}
        self.switch_layer(layer,False)

        self.tilesrepos = tilesreposfs.TilesReposFS( self, (os.path.join(self.configpath, 'tiles'),) )

        if (os.path.exists(self.locationpath)):
            self.read_locations()
        else:
            self.write_locations()

    def finish(self):
        """what to do when application is going down"""
        self.tilesrepos.finish()

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

        html = oa['data']
        p = re.compile('laddr:"([^"]+)"')
        m = p.search(html)
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

    def get_tile_from_url(self, coord):
        href = 'http://%s%i.google.com/%s/v=%s&hl=en&x=%i&y=%i&zoom=%i' % (
                self.mt_prefix,
                self.mt_counter,
                self.mt_suffix,
                self.version_string,
                coord[0],
                coord[1], coord[2])
        self.mt_counter += 1
        self.mt_counter = self.mt_counter % NR_MTS
        try:
            print 'downloading:', href
            oa = openanything.fetch(href)
                
        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]

        if oa['status']==200:
            return oa
        else:
            raise RuntimeError, ("HTTP Reponse is: " + str(oa['status']),)
    

    def get_tile_pixbuf(self, coord, online, force_update):
        return self.tilesrepos.get_tile_pixbuf(coord, online, force_update )

    def completion_model(self,strAppend=''):
        store = gtk.ListStore(TYPE_STRING)
        for str in sorted(self.locations.keys()):
            iter = store.append()
            store.set(iter, 0, str + strAppend)
        return store
