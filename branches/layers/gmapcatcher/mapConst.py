# -*- coding: utf-8 -*-
## @package gmapcatcher.mapConst
# Place to keep all constants

import os

NAME = "GMapCatcher"
VERSION = "0.8.0.0"
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
OPENSEAMAP = 15
ENIRO = 16
NOKIA = 17
SKYVECTOR_WORLD_VFR = 18
SKYVECTOR_WORLD_LO = 19
SKYVECTOR_WORLD_HI = 20

MAP_SERVERS = [
    "Google", "OpenStreetMap", "CloudMade", "Yahoo",
    "InformationFreeway", "OpenCycleMap", "Google Map Maker",
    "Virtual Earth", "Yandex",
    "Seznam", "Seznam Turistická", "Seznam Cyklo", "Seznam Historická",
    "Stamen", "Refuges Europe", "OpenSeaMap", "Eniro", "Nokia",
    "SkyVector World VFR","SkyVector World Lo","SkyVector World Hi"
]

LAYER_MAP = 0
LAYER_SAT = 1
LAYER_TER = 2
LAYER_HYB = 3
LAYER_NAMES = ["Map", "Satellite", "Terrain", "Hybrid"]
LAYER_DIRS = ["tiles", "sat_tiles", "ter_tiles", "hyb_tiles"]

FIRST_LAYER_ID = 0
MAP_SERVICES = [
    {"ID": GOOGLE,        "layers": [LAYER_MAP,LAYER_SAT,LAYER_TER,LAYER_HYB]},
    {"ID": OSM,           "layers": [LAYER_MAP]},
    {"ID": CLOUDMADE,     "layers": [LAYER_MAP]},
    {"ID": YAHOO,         "layers": [LAYER_MAP,LAYER_SAT,LAYER_HYB]},
    {"ID": INFO_FREEWAY,  "layers": [LAYER_MAP]},
    {"ID": OPENCYCLEMAP,  "layers": [LAYER_MAP]},
    {"ID": GOOGLE_MAKER,  "layers": [LAYER_MAP]},
    {"ID": VIRTUAL_EARTH, "layers": [LAYER_MAP,LAYER_SAT,LAYER_TER]},
    {"ID": YANDEX,        "layers": [LAYER_MAP]},
    {"ID": SEZNAM,        "layers": [LAYER_MAP,LAYER_SAT,LAYER_TER,LAYER_HYB]},   
    {"ID": SEZNAM_HIKING, "layers": [LAYER_SAT,LAYER_TER,LAYER_HYB]},
    {"ID": SEZNAM_CYCLO,  "layers": [LAYER_SAT,LAYER_TER,LAYER_HYB]},
    {"ID": SEZNAM_HIST,   "layers": [LAYER_SAT,LAYER_TER,LAYER_HYB]},
    {"ID": STAMEN,        "layers": [LAYER_MAP,LAYER_SAT,LAYER_TER]},
    {"ID": REFUGES,       "layers": [LAYER_MAP,LAYER_SAT,LAYER_HYB]},
    {"ID": OPENSEAMAP,    "layers": [LAYER_HYB]},
    {"ID": ENIRO,         "layers": [LAYER_MAP,LAYER_HYB]},
    {"ID": NOKIA,         "layers": [LAYER_MAP,LAYER_SAT,LAYER_TER]},
    {"ID": SKYVECTOR_WORLD_VFR,  "layers": [LAYER_MAP]},
    {"ID": SKYVECTOR_WORLD_LO,   "layers": [LAYER_MAP]},
    {"ID": SKYVECTOR_WORLD_HI,   "layers": [LAYER_MAP]},
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
R_EARTH = 6371.

USER_PATH = os.path.expanduser("~")
DEFAULT_PATH = os.path.join(USER_PATH, ".GMapCatcher")

LANGUAGES = ["en", "es", "zh"]

STARTS_WITH = 0
ENDS_WITH = 1
CONTAINS = 2
REGULAR_EXPRESSION = 3
ENTRY_SUB_MENU = ['Starts With...', 'Ends With...',
        'Contains...', 'Regular Expression...']

STRICT_LEGAL = False
WheelbarrowFull_xpm = [
    "48 48 64 1",
    "       c None",
    ".      c #DF7DCF3CC71B",
    "X      c #965875D669A6",
    "o      c #71C671C671C6",
    "O      c #A699A289A699",
    "+      c #965892489658",
    "@      c #8E38410330C2",
    "#      c #D75C7DF769A6",
    "$      c #F7DECF3CC71B",
    "%      c #96588A288E38",
    "&      c #A69992489E79",
    "*      c #8E3886178E38",
    "=      c #104008200820",
    "-      c #596510401040",
    ";      c #C71B30C230C2",
    ":      c #C71B9A699658",
    ">      c #618561856185",
    ",      c #20811C712081",
    "<      c #104000000000",
    "1      c #861720812081",
    "2      c #DF7D4D344103",
    "3      c #79E769A671C6",
    "4      c #861782078617",
    "5      c #41033CF34103",
    "6      c #000000000000",
    "7      c #49241C711040",
    "8      c #492445144924",
    "9      c #082008200820",
    "0      c #69A618611861",
    "q      c #B6DA71C65144",
    "w      c #410330C238E3",
    "e      c #CF3CBAEAB6DA",
    "r      c #71C6451430C2",
    "t      c #EFBEDB6CD75C",
    "y      c #28A208200820",
    "u      c #186110401040",
    "i      c #596528A21861",
    "p      c #71C661855965",
    "a      c #A69996589658",
    "s      c #30C228A230C2",
    "d      c #BEFBA289AEBA",
    "f      c #596545145144",
    "g      c #30C230C230C2",
    "h      c #8E3882078617",
    "j      c #208118612081",
    "k      c #38E30C300820",
    "l      c #30C2208128A2",
    "z      c #38E328A238E3",
    "x      c #514438E34924",
    "c      c #618555555965",
    "v      c #30C2208130C2",
    "b      c #38E328A230C2",
    "n      c #28A228A228A2",
    "m      c #41032CB228A2",
    "M      c #104010401040",
    "N      c #492438E34103",
    "B      c #28A2208128A2",
    "V      c #A699596538E3",
    "C      c #30C21C711040",
    "Z      c #30C218611040",
    "A      c #965865955965",
    "S      c #618534D32081",
    "D      c #38E31C711040",
    "F      c #082000000820",
    "                                                ",
    "          .XoO                                  ",
    "         +@#$%o&                                ",
    "         *=-;#::o+                              ",
    "           >,<12#:34                            ",
    "             45671#:X3                          ",
    "               +89<02qwo                        ",
    "e*                >,67;ro                       ",
    "ty>                 459@>+&&                    ",
    "$2u+                  ><ipas8*                  ",
    "%$;=*                *3:.Xa.dfg>                ",
    "Oh$;ya             *3d.a8j,Xe.d3g8+             ",
    " Oh$;ka          *3d$a8lz,,xxc:.e3g54           ",
    "  Oh$;kO       *pd$%svbzz,sxxxxfX..&wn>         ",
    "   Oh$@mO    *3dthwlsslszjzxxxxxxx3:td8M4       ",
    "    Oh$@g& *3d$XNlvvvlllm,mNwxxxxxxxfa.:,B*     ",
    "     Oh$@,Od.czlllllzlmmqV@V#V@fxxxxxxxf:%j5&   ",
    "      Oh$1hd5lllslllCCZrV#r#:#2AxxxxxxxxxcdwM*  ",
    "       OXq6c.%8vvvllZZiqqApA:mq:Xxcpcxxxxxfdc9* ",
    "        2r<6gde3bllZZrVi7S@SV77A::qApxxxxxxfdcM ",
    "        :,q-6MN.dfmZZrrSS:#riirDSAX@Af5xxxxxfevo",
    "         +A26jguXtAZZZC7iDiCCrVVii7Cmmmxxxxxx%3g",
    "          *#16jszN..3DZZZZrCVSA2rZrV7Dmmwxxxx&en",
    "           p2yFvzssXe:fCZZCiiD7iiZDiDSSZwwxx8e*>",
    "           OA1<jzxwwc:$d%NDZZZZCCCZCCZZCmxxfd.B ",
    "            3206Bwxxszx%et.eaAp77m77mmmf3&eeeg* ",
    "             @26MvzxNzvlbwfpdettttttttttt.c,n&  ",
    "             *;16=lsNwwNwgsvslbwwvccc3pcfu<o    ",
    "              p;<69BvwwsszslllbBlllllllu<5+     ",
    "              OS0y6FBlvvvzvzss,u=Blllj=54       ",
    "               c1-699Blvlllllu7k96MMMg4         ",
    "               *10y8n6FjvllllB<166668           ",
    "                S-kg+>666<M<996-y6n<8*          ",
    "                p71=4 m69996kD8Z-66698&&        ",
    "                &i0ycm6n4 ogk17,0<6666g         ",
    "                 N-k-<>     >=01-kuu666>        ",
    "                 ,6ky&      &46-10ul,66,        ",
    "                 Ou0<>       o66y<ulw<66&       ",
    "                  *kk5       >66By7=xu664       ",
    "                   <<M4      466lj<Mxu66o       ",
    "                   *>>       +66uv,zN666*       ",
    "                              566,xxj669        ",
    "                              4666FF666>        ",
    "                               >966666M         ",
    "                                oM6668+         ",
    "                                  *4            ",
    "                                                ",
    "                                                "
]