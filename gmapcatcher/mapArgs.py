## @package gmapcatcher.mapArgs
# Parsing of the array of arguments

from mapConst import *


class MapArgs():
    max_zl = MAP_MAX_ZOOM_LEVEL
    min_zl = MAP_MIN_ZOOM_LEVEL + 4
    lng_range = 0.05
    lat_range = 0.05
    nr_threads = 5
    lat = None
    lng = None
    location = None
    gpx = None
    layer = LAYER_MAP
    width = -1
    height = -1
    map_server = VIRTUAL_EARTH
    repo_type = REPOS_TYPE_OSM

    def print_help(self):
        print ' '
        print 'Download all maps of given location with one command'
        print ' '
        print 'OPTIONS'
        print '  --location=   location to download'
        print '  --latitude=   Latitude of the location '
        print '  --longitude=  Longitude of the location'
        print '  --gpx=        GPX file with a path'
        print ' '
        print '  --map         Retrieve map images (default)'
        print '  --satellite   Retrieve satellite images'
        print '  --terrain     Retrieve terrain images'
        print '  --hybrid      Retrieve hybrid images'
        print '  --chart       Retrieve chart images'
        print '  --map-server= Name of map server to use (default = {})'.format(MAP_SERVERS[self.map_server])
        print '  --repo-type=  Name of repo type to save files as (default = {})'.format(REPOS_TYPE[self.repo_type])

        print ' '
        print '  --latrange=   Latitude Range to get    (default = %f)' % self.lat_range
        print '  --lngrange=   Longitude Range to get   (default = %f)' % self.lng_range
        print '  --height=     Height in Km (will override latrange)'
        print '  --width=      Width in Km (will override lngrange) for locations,'
        print '                and width in "tiles" for GPX paths.'
        print ' '
        print '  --max-zoom=   Maximum Zoom   (default = %d)' % self.max_zl
        print '  --min-zoom=   Minimum Zoom   (default = %d)' % self.min_zl
        print '  --threads=    Number of threads   (default = %d)' % self.nr_threads
        print '  --full-range  Sets lat, lng to (0, 0) and range to the Max,'
        print '                very useful to download maps of entire world'
        print ' '
        print 'SAMPLE USAGE'
        print '  download --location="Paris, France"'
        print '  download --min-zoom=13 --full-range'
        print '  download --latitude=37.979180 --longitude=23.716647'
        print '  download --gpx=myfile.gpx --width=2'

    def __init__(self, arrArgs=()):
        if len(arrArgs) > 1:
            for arg in arrArgs[1:]:
                if arg.startswith('--'):
                    oarg = arg  # Argument with the original case
                    arg = arg.lower()
                    if arg.startswith('--max-zoom-level='):
                        self.max_zl = int(arg[17:])
                    elif arg.startswith('--min-zoom-level='):
                        self.min_zl = int(arg[17:])
                    elif arg.startswith('--max-zoom='):
                        self.max_zl = int(arg[11:])
                    elif arg.startswith('--min-zoom='):
                        self.min_zl = int(arg[11:])
                    elif arg.startswith('--location='):
                        self.location = arg[11:]
                    elif arg.startswith('--longitude='):
                        self.lng = float(arg[12:])
                    elif arg.startswith('--latitude='):
                        self.lat = float(arg[11:])
                    elif arg.startswith('--gpx='):
                        self.gpx = oarg[6:]
                    elif arg.startswith('--latrange='):
                        self.lat_range = float(arg[11:])
                    elif arg.startswith('--lngrange='):
                        self.lng_range = float(arg[11:])
                    elif arg.startswith('--width='):
                        self.width = float(arg[8:])
                    elif arg.startswith('--height='):
                        self.height = float(arg[9:])
                    elif arg.startswith('--threads='):
                        self.nr_threads = int(arg[10:])
                    elif arg.startswith('--satellite'):
                        self.layer = LAYER_SAT
                    elif arg.startswith('--terrain'):
                        self.layer = LAYER_TER
                    elif arg.startswith('--hybrid'):
                        self.layer = LAYER_HYB
                    elif arg.startswith('--chart'):
                        self.layer = LAYER_CHA
                    elif arg.startswith('--mapid='):
                        self.layer = arg[8:]
                    elif arg.startswith('--full-range'):
                        self.location = "Whole World"
                        self.lng = 0
                        self.lat = 0
                        self.lat_range = 85
                        self.lng_range = 179
                    elif arg.startswith('--map-server='):
                        self.map_server = oarg[13:]
                        print("map server = {}".format(self.map_server))
                        print("map server idx = {}".format(MAP_SERVERS.index(self.map_server)))
                    elif arg.startswith('--repo-type='):
                        rt = oarg[12:]
                        print("repo type = {}".format(rt))
                        self.repo_type = REPOS_TYPE.index(rt)
                        print("repo type idx = {}".format(self.repo_type))
    def __str__(self):
        return ("download.py --max-zoom=%s --min-zoom=%s" +
                " --latitude=%s --longitude=%s" +
                " --width=%s --height=%s") % \
               (self.max_zl, self.min_zl,
                self.lat, self.lng,
                self.width, self.height)
