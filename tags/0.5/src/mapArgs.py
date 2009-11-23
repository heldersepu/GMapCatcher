## @package src.mapArgs
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
    layer = LAYER_MAP

    def print_help(self):
        print ' '
        print 'Download all maps of given location with one command'
        print ' '
        print 'OPTIONS'
        print '  --location=   location to download'
        print '  --latitude=   Latitude of the location '
        print '  --longitude=  Longitude of the location'
        print ' '
        print '  --map         Retrieve map images (default)'
        print '  --satellite   Retrieve satellite images'
        print '  --terrain     Retrieve terrain images'
        print ' '
        print '  --latrange=   Latitude Range to get    (default = %f)' % self.lat_range
        print '  --lngrange=   Longitude Range to get   (default = %f)' % self.lng_range
        print '  --max-zoom=   Maximum Zoom   (default = %d)' % self.max_zl
        print '  --min-zoom=   Minimum Zoom   (default = %d)' % self.min_zl
        print '  --threads=    Number of threads   (default = %d)' % self.nr_threads
        print '  --full-range  Sets lat, lng to (0, 0) and range to the Max,'
        print '                very useful to download maps of entire world'
        print ' '
        print 'SAMPLE USAGE'
        print '  download.py --location="Paris, France"'
        print '  download.py --min-zoom=13 --full-range'
        print '  download.py --latitude=37.979180 --longitude=23.716647'

    def __init__(self, arrArgs):
        if len(arrArgs) > 1:
            for arg in arrArgs[1:]:
                if arg.startswith('--'):
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
                    elif arg.startswith('--latrange='):
                        self.lat_range = float(arg[11:])
                    elif arg.startswith('--lngrange='):
                        self.lng_range = float(arg[11:])
                    elif arg.startswith('--threads='):
                        self.nr_threads = int(arg[10:])
                    elif arg.startswith('--satellite'):
                        self.layer = LAYER_SATELLITE
                    elif arg.startswith('--terrain'):
                        self.layer = LAYER_TERRAIN
                    elif arg.startswith('--full-range'):
                        self.location = "Whole World"
                        self.lng = 0
                        self.lat = 0
                        self.lat_range = 85
                        self.lng_range = 179
