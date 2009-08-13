## @package src.mapConst
# Place to keep all constants

NAME = "GMapCatcher"
VERSION = "0.1.1.0"
VERSION_NAME = ""

GOOGLE = 0
OSM = 1
MAP_SERVERS = ["Google", "OpenStreetMap"]

MAP_MAX_ZOOM_LEVEL = 17
MAP_MIN_ZOOM_LEVEL = -2
TILES_WIDTH = 256
TILES_HEIGHT = 256
NR_MTS = 4
SEPARATOR = "\t"
TOOLS_MENU = ["Settings", "Edit locations", "Edit markers",
              "Change Theme", "GPS Options"]

LAYER_MAP = 0
LAYER_SATELLITE = 1
LAYER_TERRAIN = 2
LAYER_NAMES = ["Map", "Satellite", "Terrain"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles"]

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
