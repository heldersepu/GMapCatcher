# -*- coding: utf-8 -*-
## @package gmapcatcher.mapConst
# Place to keep all constants

from changeableConst import *

NAME = "GMapCatcher"
VERSION = "0.7.5.0"
VERSION_NAME = ""
WEB_ADDRESS = "http://code.google.com/p/gmapcatcher/"
# add real names here! :-)
AUTHORS = ["\"pi3orama\"", "Helder Sepulveda", "Maxim Razin", 
           "Mark Benjamin", "\"standa31415\"", "\"strombom\"",
           "\"sirknottalot\"", "\"kevlo\"", "\"mrducat\"",
           "\"bthipavo\"", "\"tatlicioglu\"", 
           "\"ahmeterdincyilmaz\"", "\"serkan.cm\"",
           "\"hk_tmp\""]

GOOGLE = 0
OSM = 1
CLOUDMADE = 2
YAHOO = 3
INFO_FREEWAY = 4
OPENCYCLEMAP = 5
GOOGLE_MAKER = 6
VIRTUAL_EARTH = 7
MAP_SERVERS = ["Google", "OpenStreetMap", "CloudMade", "Yahoo",
               "InformationFreeway", "OpenCycleMap", "Google Map Maker",
               "Virtual Earth"]

LAYER_MAP = 0
LAYER_SATELLITE = 1
LAYER_TERRAIN = 2
LAYER_HYBRID = 3
LAYER_NAMES = ["Map", "Satellite", "Terrain", "Hybrid"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles", "hyb_tiles"]

#element of the array "ID" is constant and is associated with the layer. Never change it.
# order in the comboBox is given by the order of the lines.
#If wants to change the order - move lines, but don't change "ID".
#If layers are added / removed - change the decision making in mapServices.get_url_from_coord()
# name of the layer service is created as: serviceName + layerName
FIRST_LAYER_ID = 0
MAP_SERVICES = [
    {"ID": LAYER_MAP,       "TextID": "gmap",  "serviceName":MAP_SERVERS[GOOGLE], 
            "layerDir": "tiles",     "layerName": LAYER_NAMES[LAYER_MAP] },
    {"ID": LAYER_SATELLITE, "TextID": "gsat",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "sat_tiles", "layerName": LAYER_NAMES[LAYER_SATELLITE] },
    {"ID": LAYER_TERRAIN,   "TextID": "gter",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "ter_tiles", "layerName": LAYER_NAMES[LAYER_TERRAIN] },
    {"ID": LAYER_HYBRID,    "TextID": "ghyb",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "hyb_tiles", "layerName": LAYER_NAMES[LAYER_HYBRID]},
			
    {"ID": LAYER_MAP,       "TextID": "ymap",  "serviceName":MAP_SERVERS[YAHOO],
            "layerDir": "yahoomap", "layerName": LAYER_NAMES[LAYER_MAP] },
    {"ID": LAYER_SATELLITE, "TextID": "yter",  "serviceName":MAP_SERVERS[YAHOO],
            "layerDir": "yahooter", "layerName": LAYER_NAMES[LAYER_SATELLITE] },
    {"ID": LAYER_HYBRID,    "TextID": "yhyb",  "serviceName":MAP_SERVERS[YAHOO],
            "layerDir": "yahoohyb", "layerName": LAYER_NAMES[LAYER_HYBRID] },
			
    {"ID": LAYER_MAP,       "TextID": "vemap", "serviceName":MAP_SERVERS[VIRTUAL_EARTH],
            "layerDir": "vemap",    "layerName": LAYER_NAMES[LAYER_MAP] },
    {"ID": LAYER_SATELLITE, "TextID": "vesat", "serviceName":MAP_SERVERS[VIRTUAL_EARTH],
            "layerDir": "vesat",    "layerName": LAYER_NAMES[LAYER_SATELLITE] },
    {"ID": LAYER_TERRAIN,   "TextID": "veter", "serviceName":MAP_SERVERS[VIRTUAL_EARTH],
            "layerDir": "veter",    "layerName": LAYER_NAMES[LAYER_TERRAIN] },
			
    {"ID": LAYER_MAP,       "TextID": "osmmap", "serviceName":MAP_SERVERS[OSM],
            "layerDir": "osmTiles", "layerName": ""},
    {"ID": LAYER_MAP,       "TextID": "cmmap",  "serviceName":MAP_SERVERS[CLOUDMADE],
            "layerDir": "cloudmadeTiles", "layerName": "" },
    {"ID": LAYER_MAP,       "TextID": "ifwmap", "serviceName":MAP_SERVERS[INFO_FREEWAY],
            "layerDir": "ifwTiles", "layerName": "" },
    {"ID": LAYER_MAP,       "TextID": "ocmmap", "serviceName":MAP_SERVERS[OPENCYCLEMAP],
            "layerDir": "ocmTiles", "layerName": ""},
    {"ID": LAYER_MAP,       "TextID": "gmmmap", "serviceName":MAP_SERVERS[GOOGLE_MAKER],
            "layerDir": "gmmTiles", "layerName": "" }
]
HYB_SAT_LAYER_OFFSETS = {"Google": 2, "Yahoo": 1}
NO_BULK_DOWN = ["Google", "OpenStreetMap", "OpenCycleMap"]
NO_GPS = ["Yahoo"]
NON_ONEDIR_COMBO_INDICES = {}

for name in MAP_SERVERS:
    thelist = []
    for el in MAP_SERVICES:
        if el['serviceName'] == name:
            thelist.append(el["ID"])
    NON_ONEDIR_COMBO_INDICES[name] = thelist[:]

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
DA_MENU = ["Zoom In", "Zoom Out", "Center map here", "Reset", 
        "", "Batch Download", "Export Map", "Add Marker",
        "", "Copy Location", "Copy GPS"]

REPOS_TYPE_FILES = 0
REPOS_TYPE_SQLITE3 = 1
REPOS_TYPE = ["Files", "SQLite3"]
DEFAULT_REPOS_TYPE = 0
SQLITE3_REPOSITORY_FILE = "tilerepository.db"

STATUS_DEFAULT = 0
STATUS_NONE = 0
STATUS_GPS = 1
STATUS_MOUSE = 2
STATUS_TYPE = ["None", "GPS", "Mouse"]

GPS_IMG_SIZE = (48, 48)

GPS_DISABLED = 0
GPS_MARKER = 1
GPS_CENTER = 2
GPS_ON_SCREEN = 3
GPS_NAMES = ["GPS Disabled", "GPS Marker", "GPS Center", "GPS on Screen"]

SECTION_INIT  = 'init'
R_EARTH = 6371.
USER_PATH = "~"
TILES_PATH = ".googlemaps"
DEFAULT_PATH = USER_PATH + "/" + TILES_PATH

LANGUAGES = ["en", "zh"]
