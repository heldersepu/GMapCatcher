# -*- coding: utf-8 -*-
## @package gmapcatcher.mapConf
# Read and write to the configuration file

import os
import ConfigParser
import fileUtils
from mapConst import *
from mapUtils import str_to_tuple

## Class used to read and save the configuration values
class MapConf():
    config_path = None

    ## Returns the Path to the configuration file
    def get_configpath(self):
        # the config file must be found at DEFAULT_PATH
        configpath = DEFAULT_PATH
        fileUtils.check_dir(configpath)
        configpath = os.path.join(configpath, 'gmapcatcher.conf')
        return configpath

    ## Initialise all variables.
    #  If the file does not exit it will be created
    def __init__(self, configpath=None):
        if configpath is None:
            self.config_path = self.get_configpath()
        else:
            self.config_path = configpath
        self.read()
        if not os.path.exists(self.config_path):
            self.write()

    ## Write the configuration to the given file
    def write(self):
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
        config.set(SECTION_INIT, 'gps_increment', self.gps_increment)
        config.set(SECTION_INIT, 'map_service', self.map_service)
        config.set(SECTION_INIT, 'version_url', self.version_url)
        config.set(SECTION_INIT, 'check_for_updates', self.check_for_updates)
        config.set(SECTION_INIT, 'gps_mode', self.gps_mode)
        config.set(SECTION_INIT, 'cloudmade_styleid', self.cloudMade_styleID)
        config.set(SECTION_INIT, 'cloudmade_api', self.cloudMade_API)
        config.set(SECTION_INIT, 'language', self.language)
        config.set(SECTION_INIT, 'oneDirPerMap', self.oneDirPerMap)
        config.set(SECTION_INIT, 'status_location', self.status_location)
        config.set(SECTION_INIT, 'save_at_close', int(self.save_at_close))
        config.set(SECTION_INIT, 'save_layer', self.save_layer)
        config.set(SECTION_INIT, 'save_hlocation', self.save_hlocation)
        config.set(SECTION_INIT, 'save_vlocation', self.save_vlocation)
        config.set(SECTION_INIT, 'save_width', self.save_width)
        config.set(SECTION_INIT, 'save_height', self.save_height)
        config.set(SECTION_INIT, 'scale_visible', int(self.scale_visible))
        config.set(SECTION_INIT, 'auto_refresh', self.auto_refresh)
        config.set(SECTION_INIT, 'force_update_days', self.force_update_days)
        config.set(SECTION_INIT, 'google_src', self.google_src)
        config.set(SECTION_INIT, 'match_func', self.match_func)
        config.set(SECTION_INIT, 'show_marker_name', int(self.show_marker_name))
        config.set(SECTION_INIT, 'marker_font_color', self.marker_font_color)        
        config.set(SECTION_INIT, 'marker_font_desc', self.marker_font_desc)        

        configfile = open(self.config_path, 'wb')
        config.write(configfile)

    ## Reads the configuration from a given file
    def read(self):
        def read_config(keyOption, defaultValue, castFunction):
            try:
                strValue = config.get(SECTION_INIT, keyOption)
                return castFunction(strValue)
            except Exception:
                return defaultValue

        config = ConfigParser.RawConfigParser()
        config.read(self.config_path)

        ## Initial window width, default is 550
        self.init_width = read_config('width', 550, int)
        ## Initial window height, default is 450
        self.init_height = read_config('height', 450, int)
        ## Initial map zoom, default is MAP_MAX_ZOOM_LEVEL-1
        self.init_zoom = read_config('zoom', MAP_MAX_ZOOM_LEVEL-1, int)
        ## Initial map center, default is ((1,0), (9,200))
        self.init_center = read_config('center', ((1,0),(9,200)), str_to_tuple)

        ## Directory path to the map images, default is "userProfile" folder
        self.init_path = DEFAULT_PATH
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
        ## default increment for gps track saving
        self.gps_increment = read_config('gps_increment', GPS_INCREMENT, int)
        ## Map service to get images, default is Yahoo
        self.map_service = read_config('map_service', MAP_SERVERS[YAHOO], str)
        ## URL with the latest version used for the notification updates.
        self.version_url = read_config('version_url',
            'http://gmapcatcher.googlecode.com/svn/wiki/version.wiki', str)
        ## Whether or not to check for updates, default is True (1)
        self.check_for_updates = read_config('check_for_updates', 1, int)
        ## Initial GPS mode, default is GPS_DISABLED
        self.gps_mode = read_config('gps_mode', GPS_DISABLED, int)
        ## Initial style ID for the CloudMade maps
        self.cloudMade_styleID = read_config('cloudmade_styleid', 1, int)
        ## cloudMade API key
        self.cloudMade_API = read_config('cloudmade_api', '333d990d389d5e65a7714dd738b2fc77', str)
        ## language setting, default is 'en'
        self.language = read_config('language', 'en', str)
        ## oneDirPerMap setting, default is False
        self.oneDirPerMap = read_config('oneDirPerMap', 0, int)
        ## status setting, default is STATUS_NONE
        self.status_location = read_config('status_location', 0, int)
        ## save width/height/layer/location at close, default is SAVE_AT_CLOSE
        self.save_at_close = read_config('save_at_close', 1, int)
        ## layer when saved at close
        self.save_layer = read_config('save_layer', LAYER_MAP, int)
        ## location when saved at close
        self.save_hlocation = read_config('save_hlocation', 0, int)
        self.save_vlocation = read_config('save_vlocation', 0, int)
        ## width when saved at close
        self.save_width = read_config('save_width', 550, int)
        ## height when saved at close
        self.save_height = read_config('save_height', 450, int)
        ## should scale be visible
        self.scale_visible = read_config('scale_visible', 1, int)
        ## auto-refresh frequency in miliseconds
        self.auto_refresh = read_config('auto_refresh', 0, int)
        ## Amount of days used when user selects the Force Update
        self.force_update_days = read_config('force_update_days', 1, int)
        ## Part of the URL that is used to get the google tiles
        self.google_src = read_config('google_src', '', str)
        ## The match function to be used in the auto-completion of the entry
        self.match_func = read_config('match_func', ENTRY_SUB_MENU[0], str)
        ## Show the name/description of the marker in the map
        self.show_marker_name = read_config('show_marker_name', 0, int)
        ## The font color for the name of the marker
        self.marker_font_color = read_config('marker_font_color', '#00CCCC', str)
        ## The font Description for the marker "sans bold 12"
        ## http://www.pygtk.org/docs/pygtk/class-pangofontdescription.html
        self.marker_font_desc = read_config('marker_font_desc', 'normal', str)

    ## Write the configuration to the default file
    def save(self):
        self.write()
