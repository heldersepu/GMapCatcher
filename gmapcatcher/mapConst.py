# -*- coding: utf-8 -*-
## @package gmapcatcher.mapConst
# Place to keep all constants

import os
import locale

NAME = "GMapCatcher"
VERSION = "0.8.0.2"
VERSION_NAME = ""
WEB_ADDRESS = "http://GMapCatcher.GoogleCode.com"

GOOGLE = 0
OSM = 1
CLOUDMADE = 2
YAHOO = 3
INFO_FREEWAY = 4
OPENCYCLEMAP = 5
GOOGLE_MAKER = 6
VIRTUAL_EARTH = 7
YANDEX = 8
SEZNAM = 9
SEZNAM_HIKING = 10
SEZNAM_CYCLO = 11
SEZNAM_HIST = 12
STAMEN = 13
REFUGES = 14
OPENSEAMAP = 15
ENIRO = 16
NOKIA = 17
SKYVECTOR_WORLD_VFR = 18
SKYVECTOR_WORLD_LO = 19
SKYVECTOR_WORLD_HI = 20
MAPS_FOR_FREE = 21

MAP_SERVERS = [
    "Google", "OpenStreetMap", "CloudMade", "Yahoo",
    "InformationFreeway", "OpenCycleMap", "Google Map Maker",
    "Virtual Earth", "Yandex",
    "Seznam", "Seznam Turistická", "Seznam Cyklo", "Seznam Historická",
    "Stamen", "Refuges Europe", "OpenSeaMap", "Eniro", "Nokia",
    "SkyVector World VFR", "SkyVector World Lo", "SkyVector World Hi", 
    "Maps-For-Free"
]

LAYER_MAP = 0
LAYER_SAT = 1
LAYER_TER = 2
LAYER_HYB = 3
LAYER_CHA = 4
LAYER_NAMES = ["Map", "Satellite", "Terrain", "Hybrid", "Chart"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles", "hyb_tiles", "chart_tiles"]

FIRST_LAYER_ID = 0
MAP_SERVICES = [
    {"ID": GOOGLE,        "layers": [LAYER_MAP, LAYER_SAT, LAYER_TER, LAYER_HYB]},
    {"ID": OSM,           "layers": [LAYER_MAP]},
    {"ID": CLOUDMADE,     "layers": [LAYER_MAP]},
    {"ID": YAHOO,         "layers": [LAYER_MAP, LAYER_SAT, LAYER_HYB]},
    {"ID": INFO_FREEWAY,  "layers": [LAYER_MAP]},
    {"ID": OPENCYCLEMAP,  "layers": [LAYER_MAP]},
    {"ID": GOOGLE_MAKER,  "layers": [LAYER_MAP]},
    {"ID": VIRTUAL_EARTH, "layers": [LAYER_MAP, LAYER_SAT, LAYER_TER]},
    {"ID": YANDEX,        "layers": [LAYER_MAP]},
    {"ID": SEZNAM,        "layers": [LAYER_MAP, LAYER_SAT, LAYER_TER, LAYER_HYB]},
    {"ID": SEZNAM_HIKING, "layers": [LAYER_SAT, LAYER_TER, LAYER_HYB]},
    {"ID": SEZNAM_CYCLO,  "layers": [LAYER_SAT, LAYER_TER, LAYER_HYB]},
    {"ID": SEZNAM_HIST,   "layers": [LAYER_SAT, LAYER_TER, LAYER_HYB]},
    {"ID": STAMEN,        "layers": [LAYER_MAP, LAYER_SAT, LAYER_TER]},
    {"ID": REFUGES,       "layers": [LAYER_MAP, LAYER_SAT, LAYER_HYB]},
    {"ID": OPENSEAMAP,    "layers": [LAYER_CHA]},
    {"ID": ENIRO,         "layers": [LAYER_MAP, LAYER_SAT, LAYER_TER, LAYER_HYB, LAYER_CHA]},
    {"ID": NOKIA,         "layers": [LAYER_MAP, LAYER_SAT, LAYER_TER]},
    {"ID": SKYVECTOR_WORLD_VFR,  "layers": [LAYER_MAP]},
    {"ID": SKYVECTOR_WORLD_LO,   "layers": [LAYER_MAP]},
    {"ID": SKYVECTOR_WORLD_HI,   "layers": [LAYER_MAP]},
    {"ID": MAPS_FOR_FREE, "layers": [LAYER_TER, LAYER_HYB]},
]

NO_BULK_DOWN = ["Google", "OpenStreetMap", "OpenCycleMap"]
NO_GPS = ["Yahoo"]

MAP_MAX_ZOOM_LEVEL = 17
MAP_MIN_ZOOM_LEVEL = -2
TILES_WIDTH = 256
TILES_HEIGHT = 256
NR_MTS = 4
SEPARATOR = "\t"
TOOLS_MENU = ["Settings", "Edit locations", "Edit markers",
              "Change Theme", "GPS Options", ""]
TOOLS_MENU_PLUS_CREDITS = " About "
TOOLS_MENU_PLUS_VISUAL_DL = "Save Path Maps"

ZOOM_IN = 0
ZOOM_OUT = 1
CENTER_MAP = 2
RESET = 3
BATCH_DOWN = 5
EXPORT_MAP = 6
ADD_MARKER = 7
MOUSE_LOCATION = 9
GPS_LOCATION = 10
GPS_DIRECTIONS = 12
DA_MENU = ["Zoom In", "Zoom Out", "Center map here", "Reset",
        "", "Batch Download", "Export Map", "Add Marker",
        "", "Copy Location", "Copy GPS", "", "Directions from GPS to here"]

REPOS_TYPE_FILES = 0
REPOS_TYPE_SQLITE3 = 1
REPOS_TYPE_MGMAPS = 2
REPOS_TYPE_OSM = 3
REPOS_TYPE_RMAPS = 4
REPOS_TYPE = ["Files", "SQLite3", "MGMaps", "OSM", "RMaps"]
DEFAULT_REPOS_TYPE = 0
SQLITE3_REPOSITORY_FILE = "tilerepository.db"
RMAPS_REPOSITORY_FILE_FORMAT = "tile-%s.sqlitedb"

STATUS_NONE = 0
STATUS_GPS = 1
STATUS_MOUSE = 2
STATUS_TYPE = ["None", "GPS", "Mouse"]

GPS_IMG_SIZE = (48, 48)

GPS_DISABLED = 0
GPS_MARKER = 1
GPS_CENTER = 2
GPS_ON_SCREEN = 3
GPS_TIMEOUT = 4
GPS_NAMES = ["GPS Disabled", "GPS Marker", "GPS Center",
             "GPS on Screen", "GPS Timeout"]
TYPE_OFF = 0
TYPE_GPSD = 1
TYPE_SERIAL = 2
GPS_TYPES = ["Off", "GPSd", "Serial"]
MODE_NO_FIX = 1
MODE_2D = 2
MODE_3D = 3
# default distance - fraction of deg - for gps track increment
GPS_INCREMENT = 0.001

# Units for distance measurement and GPS speed
DISTANCE_UNITS = ['km', 'miles', 'NM']
SPEED_UNITS = ['km/h', 'mph', 'knots']
UNIT_TYPE_KM = 0
UNIT_TYPE_MILE = 1
UNIT_TYPE_NM = 2

SECTION_INIT = 'init'
SECTION_GPS = 'gps'
SECTION_MAP = 'map'
SECTION_AGENT = 'agent'
R_EARTH = 6371.

USER_PATH = unicode(os.path.expanduser("~"), locale.getpreferredencoding())
DEFAULT_PATH = os.path.join(USER_PATH, ".GMapCatcher")

LANGUAGES = ["en", "es", "zh"]

STARTS_WITH = 0
ENDS_WITH = 1
CONTAINS = 2
REGULAR_EXPRESSION = 3
ENTRY_SUB_MENU = ['Starts With...', 'Ends With...',
        'Contains...', 'Regular Expression...']

STRICT_LEGAL = False
