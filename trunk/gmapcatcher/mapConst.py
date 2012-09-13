# -*- coding: utf-8 -*-
## @package gmapcatcher.mapConst
# Place to keep all constants

from changeableConst import *
import os

NAME = "GMapCatcher"
VERSION = "0.7.7.2"
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
YANDEX = 8
SEZNAM = 9
SEZNAM_HIKING = 10
SEZNAM_CYCLO = 11
SEZNAM_HIST = 12
STAMEN = 13
REFUGES = 14

MAP_SERVERS = [
    "Google", "OpenStreetMap", "CloudMade", "Yahoo",
    "InformationFreeway", "OpenCycleMap", "Google Map Maker",
    "Virtual Earth", "Yandex",
    "Seznam", "Seznam Turistická", "Seznam Cyklo", "Seznam Historická",
    "Stamen", "Refuges Europe"
]

LAYER_MAP = 0
LAYER_SAT = 1
LAYER_TER = 2
LAYER_HYB = 3
LAYER_NAMES = ["Map", "Satellite", "Terrain", "Hybrid"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles", "hyb_tiles"]

#If layers are added / removed - change the decision making in mapServices.get_url_from_coord()
# name of the layer service is created as: serviceName + layerName

# ID should be renamed to "layerType", its no longer an ID (after update from end of april 2010)
# IDM stands for numerical ID of map (used previously by ID), used as map ID in sqlite3 repository
# same as "layerDir" for filesystem repos types.

FIRST_LAYER_ID = 0
MAP_SERVICES = [
    {"ID": LAYER_MAP, "TextID": "gmap",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "tiles",     "layerName": LAYER_NAMES[LAYER_MAP] },
    {"ID": LAYER_SAT, "TextID": "gsat",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "sat_tiles", "layerName": LAYER_NAMES[LAYER_SAT] },
    {"ID": LAYER_TER, "TextID": "gter",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "ter_tiles", "layerName": LAYER_NAMES[LAYER_TER] },
    {"ID": LAYER_HYB, "TextID": "ghyb",  "serviceName":MAP_SERVERS[GOOGLE],
            "layerDir": "hyb_tiles", "layerName": LAYER_NAMES[LAYER_HYB]},

    {"ID": LAYER_MAP, "TextID": "ymap",  "serviceName":MAP_SERVERS[YAHOO],
            "layerDir": "yahoomap", "layerName": LAYER_NAMES[LAYER_MAP] },
    {"ID": LAYER_SAT, "TextID": "yter",  "serviceName":MAP_SERVERS[YAHOO],
            "layerDir": "yahooter", "layerName": LAYER_NAMES[LAYER_SAT] },
    {"ID": LAYER_HYB, "TextID": "yhyb",  "serviceName":MAP_SERVERS[YAHOO],
            "layerDir": "yahoohyb", "layerName": LAYER_NAMES[LAYER_HYB] },

    {"ID": LAYER_MAP, "TextID": "vemap", "serviceName":MAP_SERVERS[VIRTUAL_EARTH],
            "layerDir": "vemap",    "layerName": LAYER_NAMES[LAYER_MAP] },
    {"ID": LAYER_SAT, "TextID": "vesat", "serviceName":MAP_SERVERS[VIRTUAL_EARTH],
            "layerDir": "vesat",    "layerName": LAYER_NAMES[LAYER_SAT] },
    {"ID": LAYER_TER, "TextID": "veter", "serviceName":MAP_SERVERS[VIRTUAL_EARTH],
            "layerDir": "veter",    "layerName": LAYER_NAMES[LAYER_TER] },

    {"ID": LAYER_MAP, "TextID": "osmmap", "serviceName":MAP_SERVERS[OSM],
            "layerDir": "osmTiles", "layerName": ""},
    {"ID": LAYER_MAP, "TextID": "cmmap",  "serviceName":MAP_SERVERS[CLOUDMADE],
            "layerDir": "cloudmadeTiles", "layerName": "" },
    {"ID": LAYER_MAP, "TextID": "ifwmap", "serviceName":MAP_SERVERS[INFO_FREEWAY],
            "layerDir": "ifwTiles", "layerName": "" },
    {"ID": LAYER_MAP, "TextID": "ocmmap", "serviceName":MAP_SERVERS[OPENCYCLEMAP],
            "layerDir": "ocmTiles", "layerName": ""},
    {"ID": LAYER_MAP, "TextID": "gmmmap", "serviceName":MAP_SERVERS[GOOGLE_MAKER],
            "layerDir": "gmmTiles", "layerName": "" },
    {"ID": LAYER_MAP, "TextID": "yandexmap", "serviceName":MAP_SERVERS[YANDEX],
            "layerDir": "yandexTiles", "layerName": "" },
    #Seznam.cz base
    {"ID": LAYER_MAP, "TextID": "seznam_base", "serviceName": MAP_SERVERS[SEZNAM],
            "layerDir": "seznambase", "layerName": "Mapa" },
    {"ID": LAYER_SAT, "TextID": "seznam_satellite", "serviceName":MAP_SERVERS[SEZNAM],
            "layerDir": "seznamsat", "layerName": "Letecká" },
    {"ID": LAYER_TER, "TextID": "seznam_terrain", "serviceName": MAP_SERVERS[SEZNAM],
            "layerDir": "seznamter", "layerName": "Stínování" },
    {"ID": LAYER_HYB, "TextID": "seznam_hybrid", "serviceName": MAP_SERVERS[SEZNAM],
            "layerDir": "seznamhybrid", "layerName": "Popisy" },
    #Seznam.cz hiking
    # it seems that hybrid layers work only with satelitte maps, that's why the map seznam_hiking
    # is marked as satellite - I want to combine it with layer seznam_hiking_routes
    {"ID": LAYER_SAT, "TextID": "seznam_hiking", "serviceName": MAP_SERVERS[SEZNAM_HIKING],
            "layerDir": "seznamhiking", "layerName": "Mapa" },
    {"ID": LAYER_TER, "TextID": "seznam_terrain", "serviceName": MAP_SERVERS[SEZNAM_HIKING],
            "layerDir": "seznamter", "layerName": "Stínování" },
    {"ID": LAYER_HYB, "TextID": "seznam_hiking_routes", "serviceName": MAP_SERVERS[SEZNAM_HIKING],
            "layerDir": "seznamhikingroutes", "layerName": "Trasy" },
    #Seznam.cz cyclo
    # it seems that hybrid layers work only with satelitte maps, that's why the map seznam_cyclo
    # is marked as satellite - I want to combine it with layer seznam_cyclo_routes
    {"ID": LAYER_SAT, "TextID": "seznam_cyclo", "serviceName": MAP_SERVERS[SEZNAM_CYCLO],
            "layerDir": "seznamcyclo", "layerName": "Mapa" },
    {"ID": LAYER_TER, "TextID": "seznam_terrain", "serviceName": MAP_SERVERS[SEZNAM_CYCLO],
            "layerDir": "seznamter", "layerName": "Stínování" },
    {"ID": LAYER_HYB, "TextID": "seznam_cyclo_routes", "serviceName": MAP_SERVERS[SEZNAM_CYCLO],
            "layerDir": "seznamcycloroutes", "layerName": "Trasy" },
    #Seznam.cz historical
    # it seems that hybrid layers work only with satelitte maps, that's why the map seznam_hist
    # is marked as satellite - I want to combine it with layer seznam_hybrid
    {"ID": LAYER_SAT, "TextID": "seznam_hist", "serviceName": MAP_SERVERS[SEZNAM_HIST],
            "layerDir": "seznamhist", "layerName": "Mapa" },
    {"ID": LAYER_TER, "TextID": "seznam_terrain", "serviceName": MAP_SERVERS[SEZNAM_HIST],
            "layerDir": "seznamter", "layerName": "Stínování" },
    {"ID": LAYER_HYB, "TextID": "seznam_hybrid", "serviceName": MAP_SERVERS[SEZNAM_HIST],
            "layerDir": "seznamhybrid", "layerName": "Popisy" },
    # Stamen map
    {"ID": LAYER_MAP, "TextID": "stamen_toner",  "serviceName":MAP_SERVERS[STAMEN],
            "layerDir": "toner",     "layerName": "Toner" },
    {"ID": LAYER_SAT, "TextID": "stamen_water",  "serviceName":MAP_SERVERS[STAMEN],
            "layerDir": "watercolor", "layerName": "Watercolor" },
    {"ID": LAYER_TER, "TextID": "stamen_terrain",  "serviceName":MAP_SERVERS[STAMEN],
            "layerDir": "terrain", "layerName": "Terrain" },
    # Refuges.info
    {"ID": LAYER_MAP, "TextID": "refhyk",  "serviceName":MAP_SERVERS[REFUGES],
            "layerDir": "hiking",     "layerName": "Combined" },
    {"ID": LAYER_SAT, "TextID": "refter",  "serviceName":MAP_SERVERS[REFUGES],
            "layerDir": "relief", "layerName": LAYER_NAMES[LAYER_TER] },
    {"ID": LAYER_HYB, "TextID": "refonlyhyk",  "serviceName":MAP_SERVERS[REFUGES],
            "layerDir": "hiking_without_contours", "layerName": LAYER_NAMES[LAYER_HYB]},
    # OpenSeaMap
    {"ID": LAYER_MAP, "TextID": "openstreetmap",  "serviceName":MAP_SERVERS[OPENSEAMAP],
            "layerDir": "openseamap_map", "layerName": LAYER_NAMES[LAYER_MAP]},
    {"ID": LAYER_HYB, "TextID": "openseamap",  "serviceName":MAP_SERVERS[OPENSEAMAP],
            "layerDir": "openseamap_hybrid", "layerName": LAYER_NAMES[LAYER_HYB]},
]
HYB_SAT_LAYER_OFFSETS = {
    "Google": 2,
    "Yahoo": 1,
    MAP_SERVERS[SEZNAM]: 2,
    MAP_SERVERS[SEZNAM_HIKING]: 2,
    MAP_SERVERS[SEZNAM_CYCLO]: 2,
    MAP_SERVERS[SEZNAM_HIST]: 2,
    MAP_SERVERS[REFUGES]: 2,
    MAP_SERVERS[OPENSEAMAP]: 2
}
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
REPOS_TYPE_MGMAPS = 2
REPOS_TYPE_OSM = 3
REPOS_TYPE_RMAPS = 4
REPOS_TYPE = ["Files", "SQLite3", "MGMaps", "OSM", "RMaps"]
DEFAULT_REPOS_TYPE = 0
SQLITE3_REPOSITORY_FILE = "tilerepository.db"
RMAPS_REPOSITORY_FILE_FORMAT = "tile-%s.sqlitedb"

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
GPS_TIMEOUT = 4
GPS_NAMES = ["GPS Disabled", "GPS Marker", "GPS Center",
             "GPS on Screen", "GPS Timeout"]

# default distance - fraction of deg - for gps track increment
GPS_INCREMENT = 0.001

SECTION_INIT  = 'init'
R_EARTH = 6371.

USER_PATH = os.path.expanduser("~")
DEFAULT_PATH = os.path.join(USER_PATH, ".GMapCatcher")

LANGUAGES = ["en", "es" ,"zh"]

STARTS_WITH = 0
ENDS_WITH = 1
CONTAINS = 2
REGULAR_EXPRESSION = 3
ENTRY_SUB_MENU = ['Starts With...', 'Ends With...',
        'Contains...', 'Regular Expression...']
