import os
import ConfigParser
import mapUtils
from mapConst import *

class MapConf():

    init_width = 450
    init_height = 400
    init_zoom = MAP_MAX_ZOOM_LEVEL
    init_center = ((0,0),(128,128))

    def get_configpath(self):
        configpath = os.path.expanduser("~/.googlemaps")
        configpath = os.path.join(configpath, 'gmapcatcher.conf')
        return configpath

    def __init__(self):
        configpath = self.get_configpath()
        if os.path.exists(configpath):
            self.read(configpath)
        else:
            self.write(configpath)

    def write(self, configpath):
        config = ConfigParser.RawConfigParser()
        strSection = 'init'
        config.add_section(strSection)
        config.set(strSection, 'width', self.init_width)
        config.set(strSection, 'height', self.init_height)
        config.set(strSection, 'zoom', self.init_zoom)
        config.set(strSection, 'center', self.init_center)

        configfile = open(configpath, 'wb')
        config.write(configfile)

    def read(self, configpath):
        config = ConfigParser.RawConfigParser()
        config.read(configpath)
        strSection = 'init'
        self.init_width = config.getint(strSection, 'width')
        self.init_height = config.getint(strSection, 'height')
        self.init_zoom = config.getint(strSection, 'zoom')
        strCenter = config.get(strSection, 'center')
        self.init_center = mapUtils.str_to_tuple(strCenter)

    def save(self):
        configpath = self.get_configpath()
        self.write(configpath)

