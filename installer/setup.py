# -*- coding: utf-8 -*-
## @package setup
# Setup file used to build the Windows Installer

from distutils.core import setup
from src.mapConst import *
import os

if os.name == "posix":
    ico = "images/map.png"
    setup(
        name = NAME,
        description = 'Offline Map Viewer',
        version = VERSION,
        url = WEB_ADDRESS,
        data_files = [('share/doc/mapcatcher', ['README', 'Changelog']),
                    ('share/applications', ['gmapcatcher.desktop'])
        ],
        scripts = ['mapcatcher']
    )
else:
    import py2exe
    setup(
        name = NAME,
        description = 'Offline Google Map Viewer',
        version = VERSION,
        url = WEB_ADDRESS,
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
        data_files = ['Changelog', 'README']
    )
