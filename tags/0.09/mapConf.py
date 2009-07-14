## @package mapConf
# Read and write to the configuration file

import os
import ConfigParser
import fileUtils
from mapConst import *
from mapUtils import str_to_tuple

## Class used to read and save the configuration values
class MapConf():

    ## Returns the Path to the configuration file
    def get_configpath(self):
        # the config file most be in the DEFAULT_PATH
        configpath = os.path.expanduser(DEFAULT_PATH)
        fileUtils.check_dir(configpath)
        configpath = os.path.join(configpath, 'gmapcatcher.conf')
        return configpath

    ## Initialise all variables.
    #  If the file does not exit it will be created
    def __init__(self):
        configpath = self.get_configpath()
        self.read(configpath)
        if not os.path.exists(configpath):
            self.write(configpath)

    ## Write the configuration to the given file
    def write(self, configpath):
        config = ConfigParser.RawConfigParser()
        strSection = 'init'
        config.add_section(strSection)
        if self.init_path:
            config.set(strSection, 'path', self.init_path)
        config.set(strSection, 'width', self.init_width)
        config.set(strSection, 'height', self.init_height)
        config.set(strSection, 'zoom', self.init_zoom)
        config.set(strSection, 'center', self.init_center)
        config.set(strSection, 'gps_update_rate', self.gps_update_rate)
        config.set(strSection, 'show_cross', self.show_cross)
        config.set(strSection, 'max_gps_zoom', self.max_gps_zoom)

        configfile = open(configpath, 'wb')
        config.write(configfile)

    ## Reads the configuration from a given file
    def read(self, configpath):
        def read_config(keyOption, defaultValue, castFunction):
            try:
                strValue = config.get(strSection, keyOption)
                return castFunction(strValue)
            except Exception:
                return defaultValue

        config = ConfigParser.RawConfigParser()
        config.read(configpath)
        strSection = 'init'

        ## Initial window width, default is 450
        self.init_width = read_config('width', 450, int)
        ## Initial window height, default is 400
        self.init_height = read_config('height', 400, int)
        ## Initial map zoom, default is MAP_MAX_ZOOM_LEVEL
        self.init_zoom = read_config('zoom', MAP_MAX_ZOOM_LEVEL, int)
        ## Initial map center, default is ((0,0),(128,128))
        self.init_center = read_config('center', ((0,0),(128,128)), str_to_tuple)

        ## Directory path to the map images, default is "userProfile" folder
        self.init_path = os.path.join(os.path.expanduser(USER_PATH), TILES_PATH)
        strPath = read_config('path', self.init_path, str)
        if not strPath.strip().lower() in ['none', '']:
            strPath = fileUtils.check_dir(strPath)
            if os.path.isdir(strPath):
                self.init_path = strPath

        ## How often is the GPS updated, default is 1 second
        self.gps_update_rate = read_config('gps_update_rate', 1.0, float)
        ## Show a small cross in the center of the map, default is 0
        self.show_cross = read_config('show_cross', 0, int)
        ## Maximum zoom to show the GPS, deault is 16
        self.max_gps_zoom = read_config('max_gps_zoom', 16, int)

    ## Write the configuration to the default file
    def save(self):
        configpath = self.get_configpath()
        self.write(configpath)

