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
        configpath = os.path.join(configpath, 'AleppoMap.conf')
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
        config.set(SECTION_INIT, 'version_url', self.version_url)
        config.set(SECTION_INIT, 'check_for_updates', self.check_for_updates)
        config.set(SECTION_INIT, 'oneDirPerMap', self.oneDirPerMap)
        config.set(SECTION_INIT, 'statusbar_type', self.statusbar_type)
        config.set(SECTION_INIT, 'save_at_close', int(self.save_at_close))
        config.set(SECTION_INIT, 'save_layer', self.save_layer)
        config.set(SECTION_INIT, 'save_hlocation', self.save_hlocation)
        config.set(SECTION_INIT, 'save_vlocation', self.save_vlocation)
        config.set(SECTION_INIT, 'save_width', self.save_width)
        config.set(SECTION_INIT, 'save_height', self.save_height)
        config.set(SECTION_INIT, 'match_func', self.match_func)
        config.set(SECTION_INIT, 'hide_map_servers', self.hide_map_servers)
        config.set(SECTION_INIT, 'units', self.units)
        config.set(SECTION_INIT, 'start_offline', self.start_offline)
        config.set(SECTION_INIT, 'limited', self.limited)

        config.add_section(SECTION_MAP)
        config.set(SECTION_MAP, 'zoom', self.init_zoom)
        config.set(SECTION_MAP, 'max_zoom', self.max_zoom)
        config.set(SECTION_MAP, 'min_zoom', self.min_zoom)
        config.set(SECTION_MAP, 'language', self.language)
        config.set(SECTION_MAP, 'center', self.init_center)
        config.set(SECTION_MAP, 'show_cross', self.show_cross)
        config.set(SECTION_MAP, 'map_service', self.map_service)
        config.set(SECTION_MAP, 'cloudmade_api', self.cloudMade_API)
        config.set(SECTION_MAP, 'cloudmade_styleid', self.cloudMade_styleID)
        config.set(SECTION_MAP, 'scale_visible', int(self.scale_visible))
        config.set(SECTION_MAP, 'force_update_days', self.force_update_days)
        config.set(SECTION_MAP, 'auto_refresh', self.auto_refresh)
        config.set(SECTION_MAP, 'google_src', self.google_src)
        config.set(SECTION_MAP, 'show_marker_name', int(self.show_marker_name))
        config.set(SECTION_MAP, 'marker_font_color', self.marker_font_color)
        config.set(SECTION_MAP, 'marker_font_desc', self.marker_font_desc)
        config.set(SECTION_MAP, 'maxthreads', self.maxthreads)
        config.set(SECTION_MAP, 'overlay_delay', self.overlay_delay)
        config.set(SECTION_MAP, 'opacity', self.opacity)
        config.set(SECTION_MAP, 'draw_track_start_end', self.draw_track_start_end)

        config.add_section(SECTION_GPS)
        config.set(SECTION_GPS, 'max_gps_zoom', self.max_gps_zoom)
        config.set(SECTION_GPS, 'gps_update_rate', self.gps_update_rate)
        config.set(SECTION_GPS, 'gps_increment', self.gps_increment)
        config.set(SECTION_GPS, 'gps_type', self.gps_type)
        config.set(SECTION_GPS, 'gps_track', self.gps_track)
        config.set(SECTION_GPS, 'gps_track_interval', self.gps_track_interval)
        config.set(SECTION_GPS, 'gps_track_width', self.gps_track_width)
        config.set(SECTION_GPS, 'gps_serial_port', self.gps_serial_port)
        config.set(SECTION_GPS, 'gps_serial_baudrate', self.gps_serial_baudrate)
        config.set(SECTION_GPS, 'gps_mode', self.gps_mode)

        config.add_section(SECTION_AGENT)
        config.set(SECTION_AGENT, 'name', self.name)
        config.set(SECTION_AGENT, 'version', self.version)
        config.set(SECTION_AGENT, 'web_address', self.web_address)

        configfile = open(self.config_path, 'wb')
        config.write(configfile)

    ## Reads the configuration from a given file
    def read(self):
        def read_config(keyOption, defaultValue, castFunction, section=SECTION_INIT):
            try:
                strValue = config.get(section, keyOption)
                return castFunction(strValue)
            except Exception:
                return defaultValue

        config = ConfigParser.RawConfigParser()
        config.read(self.config_path)

        ## Initial window width, default is 550
        self.init_width = read_config('width', 780, int)
        ## Initial window height, default is 450
        self.init_height = read_config('height', 600, int)

        ## Directory path to the map images, default is "userProfile" folder
        self.init_path = DEFAULT_PATH
        strPath = read_config('path', self.init_path, str)
        if not strPath.strip().lower() in ['none', '']:
            strPath = fileUtils.check_dir(strPath)
            if os.path.isdir(strPath):
                self.init_path = strPath

        ## Repository type - filebased / sqlite3
        self.repository_type = read_config('repository_type', 0, int)
        ## URL with the latest version used for the notification updates.
        self.version_url = read_config('version_url', '', str)
        ## Whether or not to check for updates, default is True (1)
        self.check_for_updates = read_config('check_for_updates', 0, int)
        ## oneDirPerMap setting, default is False
        self.oneDirPerMap = read_config('oneDirPerMap', 0, int)
        ## Statusbar type, default is STATUS_NONE
        self.statusbar_type = read_config('statusbar_type', STATUS_MOUSE, int)
        ## save width/height/layer/location at close, default is SAVE_AT_CLOSE
        self.save_at_close = read_config('save_at_close', 1, int)
        ## layer when saved at close
        self.save_layer = read_config('save_layer', LAYER_SAT, int)
        ## location when saved at close
        self.save_hlocation = read_config('save_hlocation', 0, int)
        self.save_vlocation = read_config('save_vlocation', 0, int)
        ## width when saved at close
        self.save_width = read_config('save_width', 780, int)
        ## height when saved at close
        self.save_height = read_config('save_height', 600, int)
        ## The match function to be used in the auto-completion of the entry
        self.match_func = read_config('match_func', ENTRY_SUB_MENU[0], str)
        ## List of map servers to hide
        self.hide_map_servers = read_config('hide_map_servers', '0,3,16,18,19,20', str)
        ## Speed and distance units (default km / km/h)
        self.units = read_config('units', 0, int)
        ## Start offline (default = Yes)
        self.start_offline = read_config('start_offline', 1, int)
        ## limited capabilities (default = No)
        self.limited = read_config('limited', 1, int)

        ## Initial map zoom, default is MAP_MAX_ZOOM_LEVEL-2
        self.init_zoom = read_config('zoom', 6, int, SECTION_MAP)
        ## language setting, default is 'en'
        self.language = read_config('language', 'en', str, SECTION_MAP)
        ## Initial map center, default is ((1, 1), (210, 170))
        self.init_center = read_config('center', ((1222, 831), (152, 33)), str_to_tuple, SECTION_MAP)
        ## Show a small cross in the center of the map, default is False (0)
        self.show_cross = read_config('show_cross', 0, int, SECTION_MAP)
        ## Map service to get images, default is Nokia
        self.map_service = read_config('map_service', MAP_SERVERS[NOKIA], str, SECTION_MAP)
        ## cloudMade API key
        self.cloudMade_API = read_config('cloudmade_api', '', str, SECTION_MAP)
        ## Initial style ID for the CloudMade maps
        self.cloudMade_styleID = read_config('cloudmade_styleid', 1, int, SECTION_MAP)
        ## Visibility of the scale
        self.scale_visible = read_config('scale_visible', 1, int, SECTION_MAP)
        ## Amount of days used when user selects the Force Update
        self.force_update_days = read_config('force_update_days', 1, int, SECTION_MAP)
        ## auto-refresh frequency in miliseconds
        self.auto_refresh = read_config('auto_refresh', 0, int, SECTION_MAP)
        ## Part of the URL that is used to get the google tiles
        self.google_src = read_config('google_src', '', str, SECTION_MAP)
        ## Show the name/description of the marker in the map
        self.show_marker_name = read_config('show_marker_name', 0, int, SECTION_MAP)
        ## The font color for the name of the marker
        self.marker_font_color = read_config('marker_font_color', '#00CCCC', str, SECTION_MAP)
        ## The font Description for the marker "sans bold 12"
        ## http://www.pygtk.org/docs/pygtk/class-pangofontdescription.html
        self.marker_font_desc = read_config('marker_font_desc', 'normal', str, SECTION_MAP)
        ## Maximum number of threads to download maps
        self.maxthreads = read_config('maxthreads', 4, int, SECTION_MAP)
        ## Time delay before drawing the map overlay
        self.overlay_delay = read_config('overlay_delay', 0.1, float, SECTION_MAP)
        ## Initial map opacity
        self.opacity = read_config('opacity', 0.0, float, SECTION_MAP)
        ## Initial map opacity
        self.draw_track_start_end = read_config('draw_track_start_end', 0, int, SECTION_MAP)
        self.max_zoom = read_config('max_zoom', MAP_MAX_ZOOM_LEVEL - 2, int, SECTION_MAP)
        self.min_zoom = read_config('min_zoom', MAP_MIN_ZOOM_LEVEL, int, SECTION_MAP)

        ## How often is the GPS updated, default is 1 second
        self.gps_update_rate = read_config('gps_update_rate', 1.0, float, SECTION_GPS)
        ## default increment for gps track saving
        self.gps_increment = read_config('gps_increment', GPS_INCREMENT, int, SECTION_GPS)
        ## GPS-type, GPSd (0) or serial (1), default is GPSd
        self.gps_type = read_config('gps_type', 1, int, SECTION_GPS)
        ## Draw GPS-track, default is 1 (True)
        self.gps_track = read_config('gps_track', 0, int, SECTION_GPS)
        ## GPS-track "interval" in meters, default is 50m
        self.gps_track_interval = read_config('gps_track_interval', 50, int, SECTION_GPS)
        ## GPS-track width, default is 2px
        self.gps_track_width = read_config('gps_track_width', 2, int, SECTION_GPS)
        ## GPS serial port, default is 'none'
        self.gps_serial_port = read_config('gps_serial_port', 'COM5', str, SECTION_GPS)
        ## GPS serial baudrate, default is 9600
        self.gps_serial_baudrate = read_config('gps_serial_baudrate', 9600, int, SECTION_GPS)
        ## Initial GPS mode, default is GPS_DISABLED
        self.gps_mode = read_config('gps_mode', GPS_MARKER, int, SECTION_GPS)
        ## Maximum zoom to show the GPS, default is 16
        self.max_gps_zoom = read_config('max_gps_zoom', 16, int, SECTION_GPS)

        ## User agent name
        self.name = read_config('name', 'Aleppo', str, SECTION_AGENT)
        ## User agent version
        self.version = read_config('version', VERSION, str, SECTION_AGENT)
        ## User agent webaddress
        self.web_address = read_config('web_address', 'http://www.aleppoltd.com/', str, SECTION_AGENT)

    ## Write the configuration to the default file
    def save(self):
        self.write()

    ## Write the configuration to the default file
    def get_layer_dir(self, layer):
        if self.oneDirPerMap:
            return os.path.join(self.map_service, LAYER_DIRS[layer])
        else:
            return LAYER_DIRS[layer]
