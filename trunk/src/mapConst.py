# -*- coding: utf-8 -*-
## @package src.mapConst
# Place to keep all constants

NAME = "GMapCatcher"
VERSION = "0.7.1.0"
VERSION_NAME = ""
WEB_ADDRESS = "http://code.google.com/p/gmapcatcher/"

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

#element of the array "ID" is constant and is associated with the layer. Never change it.
# order in the comboBox is given by the order of the lines.
#If wants to change the order - move lines, but don't change "ID".
#If layers are added / removed - change the decision making in mapServices.get_url_from_coord()
# name of the lauer service is created as: serviceName + layerName
FIRST_LAYER_ID = 0
MAP_SERVICES = [
    {"ID": 0, "TextID": "gmap",   "serviceName":"Google",             "layerDir": "tiles", "layerName": "Map" },
    {"ID": 1, "TextID": "gsat",   "serviceName":"Google",             "layerDir": "sat_tiles", "layerName": "Satellite" },
    {"ID": 2, "TextID": "gter",   "serviceName":"Google",             "layerDir": "ter_tiles", "layerName": "Terrain" },
 	{"ID": 3, "TextID": "ghyb",   "serviceName":"Google",             "layerDir": "hyb_tiles", "layerName": "Hybrid"},
    {"ID": 0, "TextID": "ymap",   "serviceName":"Yahoo",              "layerDir": "yahoomap", "layerName": "Map" },
    {"ID": 1, "TextID": "yter",   "serviceName":"Yahoo",              "layerDir": "yahooter", "layerName": "Satellite" },
    {"ID": 0, "TextID": "vemap",  "serviceName":"Virtual Earth",      "layerDir": "vemap", "layerName": "Map" },
    {"ID": 1, "TextID": "vesat",  "serviceName":"Virtual Earth",      "layerDir": "vesat", "layerName": "Satellite" },
    {"ID": 2, "TextID": "veter",  "serviceName":"Virtual Earth",      "layerDir": "veter", "layerName": "Terrain" },
    {"ID": 0, "TextID": "osmmap", "serviceName":"OpenStreetMap",      "layerDir": "osmtiles", "layerName": ""},
    {"ID": 0, "TextID": "cmmap",  "serviceName":"CloudMade",          "layerDir": "cloudmatetiles", "layerName": "" },
    {"ID": 0, "TextID": "ifwmap", "serviceName":"InformationFreeway", "layerDir": "ifwtiles", "layerName": "" },
    {"ID": 0, "TextID": "ocmmap", "serviceName":"OpenCycleMap",       "layerDir": "ocmtiles", "layerName": ""},
    {"ID": 0, "TextID": "gmmmap", "serviceName":"Google Map Maker",   "layerDir": "gmmtiles", "layerName": "" }
               ]

NO_BULK_DOWN = ["OpenStreetMap", "OpenCycleMap"]

LAYER_MAP = 0
LAYER_SATELLITE = 1
LAYER_TERRAIN = 2
LAYER_HYBRID = 3
LAYER_NAMES = ["Map", "Satellite", "Terrain", "Hybrid"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles", "hyb_tiles"]

MAP_MAX_ZOOM_LEVEL = 17
MAP_MIN_ZOOM_LEVEL = -2
TILES_WIDTH = 256
TILES_HEIGHT = 256
NR_MTS = 4
SEPARATOR = "\t"
TOOLS_MENU = ["Settings", "Edit locations", "Edit markers",
              "Change Theme", "GPS Options"]

ZOOM_IN = 0
ZOOM_OUT = 1
CENTER_MAP = 2
RESET = 3
BATCH_DOWN = 5
EXPORT_MAP = 6
ADD_MARKER = 7
DA_MENU = ["Zoom In", "Zoom Out", "Center map here",
        "Reset", "", "Batch Download", "Export Map", "Add Marker"]

ROPES_TYPE_FILES = 0
ROPES_TYPE_SQLITE3 = 1
REPOS_TYPE = ["Files", "SQLite3"]
DEFAULT_REPOS_TYPE = 0
SQLITE3_REPOSITORY_FILE = "tilerepository.db"


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
