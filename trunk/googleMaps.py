import os
import re
import gtk
import sys
import urllib
import openanything
import fileUtils

from time import time
from mapConst import *
from threading import Lock
from gobject import TYPE_STRING

class GoogleMaps:

    # coord = (lat, lng, zoom_level)
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
        self.tilespath=os.path.join(self.configpath,LAYER_DIRS[new_layer])
        fileUtils.check_dir(self.tilespath)
        if new_layer not in self.known_layers:
            self.version_string=None
            if not online:
                return True
            oa = openanything.fetch(
                'http://maps.google.com/maps?t='+self.map_server_query[new_layer])
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
        if not self.switch_layer(self.layer,online):
            return False

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
            if oa['status']==200:
                file = open( filename, 'wb' )
                file.write( oa['data'] )
                file.close()
                return True
        except KeyboardInterrupt:
            raise
        except:
            print '\tdownload failed -', sys.exc_info()[0]
        return False

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

        if (os.path.exists(self.locationpath)):
            self.read_locations()
        else:
            self.write_locations()

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


    def coord_to_path(self, coord):
        self.lock.acquire()
        ## at most 1024 files in one dir
        ## We only have 2 levels for one axis
        path = fileUtils.check_dir(self.tilespath, '%d' % coord[2])
        path = fileUtils.check_dir(path, "%d" % (coord[0] / 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[0] % 1024))
        path = fileUtils.check_dir(path, "%d" % (coord[1] / 1024))
        self.lock.release()
        return os.path.join(path, "%d.png" % (coord[1] % 1024))

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

    def get_tile_pixbuf(self, coord, online, force_update):
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

    def completion_model(self,strAppend=''):
        store = gtk.ListStore(TYPE_STRING)
        for str in sorted(self.locations.keys()):
            iter = store.append()
            store.set(iter, 0, str + strAppend)
        return store
