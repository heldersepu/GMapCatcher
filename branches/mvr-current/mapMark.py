## @package mapMark
# Read and Write the locations of the Markers

import os
import re
import gtk
import fileUtils
import mapPixbuf
from mapConst import *

class MyMarkers:
    # coord = (lat, lng, zoom_level)
    positions = {}

    def read_markers(self):
        self.positions = fileUtils.read_file('marker', self.markerpath)

    def write_markers(self):
        fileUtils.write_file('marker', self.markerpath, self.positions)

    def __init__(self, configpath=None):
        self.configpath = os.path.expanduser(configpath or DEFAULT_PATH)
        self.markerpath = os.path.join(self.configpath, 'markers')

        if not os.path.isdir(self.configpath):
            os.mkdir(self.configpath)

        if (os.path.exists(self.markerpath)):
            self.read_markers()
        else:
            self.write_markers()

    def get_markers(self):
        return self.positions

    def get_pixDim(self, zl):
        maxZoom = MAP_MAX_ZOOM_LEVEL - 2
        if zl >= maxZoom :
            return 56
        elif zl <= 1:
            return 256
        else:
            return 56 + int((maxZoom - zl) * 15)
    
    def get_marker_pixbuf(self, zl):
        pixDim = self.get_pixDim(zl)
        return mapPixbuf.getImage('images\marker.png', pixDim, pixDim)
