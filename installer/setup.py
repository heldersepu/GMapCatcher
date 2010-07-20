# -*- coding: utf-8 -*-
## @package setup
# Setup file used to build the Installers

from distutils.core import setup
from gmapcatcher.mapConst import *
import os

if os.name == "posix":
    ico = "images/map.png"
    setup(
        name = NAME,
        description = 'Offline Map Viewer',
        version = VERSION,
        url = WEB_ADDRESS,
        data_files = [('share/doc/mapcatcher', ['README', 'changelog']),
                    ('share/applications', ['gmapcatcher.desktop']),
                    ('share/man/man1', 
                        ['man/mapcatcher.1.gz', 'man/mapdownloader.1.gz']),
                    ('share/pixmaps', ['images/mapcatcher.png']),
                    ('share/pixmaps/gmapcatcher',
                    # TODO
                    # change detection of png images to programmatical
                        ['images/downloading.png', 'images/map.png',
                        'images/marker.png', 'images/marker1.png',
                        'images/marker_gps.png', 'images/missing.png'])
        ],
        scripts = ['mapcatcher', 'mapdownloader'],
        packages = ['gmapcatcher', 'gmapcatcher.mapServers', 
                    'gmapcatcher.pyGPSD', 'gmapcatcher.pyGPSD.nmea',
                    'gmapcatcher.pyGPSD.nmea.serial']
    )
else:
    import py2exe
    setup(
        name = NAME,
        description = 'Offline Google Map Viewer',
        version = VERSION,
        url = WEB_ADDRESS,
        console = ['download.py'],
        windows = [{
            'script': 'maps.py',
            'icon_resources': [(1, "images\maps.ico")],
        }],
        options = {
            'py2exe': {
                'packages':'encodings',
                'includes': 'cairo, pango, pangocairo, atk, gobject',
            }
        },
        data_files = ['changelog', 'README']
    )
