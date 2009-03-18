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
    locations = {}
    mt_counter = 0
    version_string = None
    html_data = ""
    show_sat = False

    # Set variables to Satellite or Maps
    def get_maps(self, doMaps=True):
        goog = '.google.com/'
        if doMaps:
            self.fetchURL = 'http://mt[0-9]'+goog+'mt.*w([0-9].[0-9][0-9])'
            self.getFileURL = 'http://mt%i'+goog+'mt?n=404&v=w%s&hl'
            self.tiles = 'tiles'
            self.default_version_string = '2.92'
        else:
            self.fetchURL = 'http://khm[0-9]'+goog+'kh.....d([0-9][0-9])'
            self.getFileURL = 'http://khm%i'+goog+'kh?v=%s&hl'
            self.tiles = 'sat_tiles'
            self.default_version_string = '37'
        self.getFileURL += '=en&x=%i&y=%i&zoom=%i'
        self.tilespath = fileUtils.check_dir(self.configpath, self.tiles)
        self.version_string = self.fetch_version_string()

    def set_zoom(self, intZoom):
        if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
            return intZoom
        else:
            return 10

    def fetch_version_string(self):
        self.version_string = self.default_version_string
        if self.html_data == "":
            oa = openanything.fetch( 'http://maps.google.com/maps')
            if oa['status'] != 200:
                print "Trying fetch http://maps.google.com/maps but failed"
            else:
                self.html_data = oa['data']
        if self.html_data != "":
            p = re.compile(self.fetchURL)
            m = p.search(self.html_data)
            if m:
                self.version_string = m.group(1)
            else:
                print "!@@# Unable to fetch version string"
        return self.version_string

    def get_png_file(self, coord, filename, online, force_update):
        # remove tile only when online
        if (os.path.isfile(filename) and force_update and online):
            # Don't remove old tile unless it is downloaded more
            # than 24 hours ago (24h * 3600s) = 86400
            if (int(time() - os.path.getmtime(filename)) > 86400):
                os.remove(filename)

        if os.path.isfile(filename):
            return True
        else:
            if not online:
                return False

        if self.version_string == None:
            self.version_string = self.fetch_version_string()

        href = self.getFileURL \
                % (self.mt_counter, self.version_string,
                   coord[0], coord[1], coord[2])
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

    def __init__(self):
        self.lock = Lock()
        self.configpath = \
            fileUtils.check_dir(os.path.expanduser("~/.googlemaps"))
        self.locationpath = os.path.join(self.configpath, 'locations')
        self.get_maps(True)
        self.show_sat = \
            os.path.isdir(os.path.join(self.configpath, 'sat_tiles'))

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
            self.html_data = html
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
