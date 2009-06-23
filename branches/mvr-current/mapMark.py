## @file mapMark.py
# ToDo

import os
import re
import gtk
import fileUtils
from mapConst import *

class MyMarkers:
    # coord = (lat, lng, zoom_level)
    positions = {}
    pixbuf = None

    def read_markers(self):
        self.positions = fileUtils.read_file('marker', self.markerpath)

    def write_markers(self):
        fileUtils.write_file('marker', self.markerpath, self.positions)

    def __init__(self, configpath=None):
        self.configpath = os.path.expanduser(configpath or DEFAULT_PATH)
        self.markerpath = os.path.join(self.configpath, 'markers')
        self.pixbuf = self.get_marker_pixbuf()

        if not os.path.isdir(self.configpath):
            os.mkdir(self.configpath)

        if (os.path.exists(self.markerpath)):
            self.read_markers()
        else:
            self.write_markers()

    def get_markers(self):
        return self.positions

    def get_marker_pixbuf(self):
        filename = 'marker.png'
        if (os.path.exists(filename)):
            w = gtk.Image()
            w.set_from_file(filename)
            try:
                return w.get_pixbuf()
            except ValueError:
                print "File corrupted: %s" % filename

