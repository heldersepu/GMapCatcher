## @package src.mapConf
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
        config.add_section(SECTION_INIT)
        if self.init_path:
            config.set(SECTION_INIT, 'path', self.init_path)
        config.set(SECTION_INIT, 'repository_type', self.repository_type)
        config.set(SECTION_INIT, 'width', self.init_width)
        config.set(SECTION_INIT, 'height', self.init_height)
        config.set(SECTION_INIT, 'zoom', self.init_zoom)
        config.set(SECTION_INIT, 'center', self.init_center)
        config.set(SECTION_INIT, 'gps_update_rate', self.gps_update_rate)
        config.set(SECTION_INIT, 'show_cross', self.show_cross)
        config.set(SECTION_INIT, 'max_gps_zoom', self.max_gps_zoom)
        config.set(SECTION_INIT, 'map_service', self.map_service)
        config.set(SECTION_INIT, 'version_url', self.version_url)
        config.set(SECTION_INIT, 'check_for_updates', self.check_for_updates)
        config.set(SECTION_INIT, 'gps_mode', self.gps_mode)
        config.set(SECTION_INIT, 'cloudmade_styleid', self.cloudMade_styleID)

        configfile = open(configpath, 'wb')
        config.write(configfile)

    ## Reads the configuration from a given file
    def read(self, configpath):
        def read_config(keyOption, defaultValue, castFunction):
            try:
                strValue = config.get(SECTION_INIT, keyOption)
                return castFunction(strValue)
            except Exception:
                return defaultValue

        config = ConfigParser.RawConfigParser()
        config.read(configpath)

        ## Initial window width, default is 550
        self.init_width = read_config('width', 550, int)
        ## Initial window height, default is 450
        self.init_height = read_config('height', 450, int)
        ## Initial map zoom, default is MAP_MAX_ZOOM_LEVEL-1
        self.init_zoom = read_config('zoom', MAP_MAX_ZOOM_LEVEL-1, int)
        ## Initial map center, default is ((1,0), (9,200))
        self.init_center = read_config('center', ((1,0),(9,200)), str_to_tuple)

        ## Directory path to the map images, default is "userProfile" folder
        self.init_path = os.path.join(os.path.expanduser(USER_PATH), TILES_PATH)
        strPath = read_config('path', self.init_path, str)
        if not strPath.strip().lower() in ['none', '']:
            strPath = fileUtils.check_dir(strPath)
            if os.path.isdir(strPath):
                self.init_path = strPath

        ## Repository type - filebased / sqlite3
        self.repository_type =  read_config('repository_type', 0, int)

        ## How often is the GPS updated, default is 1 second
        self.gps_update_rate = read_config('gps_update_rate', 1.0, float)
        ## Show a small cross in the center of the map, default is False (0)
        self.show_cross = read_config('show_cross', 0, int)
        ## Maximum zoom to show the GPS, default is 16
        self.max_gps_zoom = read_config('max_gps_zoom', 16, int)
        ## Map service to get images, default is Google
        self.map_service = read_config('map_service', MAP_SERVERS[GOOGLE], str)
        ## URL with the latest version used for the notification updates.
        self.version_url = read_config('version_url',
            'http://gmapcatcher.googlecode.com/svn/wiki/version.wiki', str)
        ## Whether or not to check for updates, default is True (1)
        self.check_for_updates = read_config('check_for_updates', 1, int)
        ## Initial GPS mode, default is GPS_DISABLED
        self.gps_mode = read_config('gps_mode', GPS_DISABLED, int)
        ## Initial style ID for the CloudMade maps
        self.cloudMade_styleID = read_config('cloudmade_styleid', 1, int)

    ## Write the configuration to the default file
    def save(self):
        configpath = self.get_configpath()
        self.write(configpath)

