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
                    map(lambda(thestr): "images/" + thestr, os.listdir('images')))
        ],
        scripts = ['mapcatcher', 'mapdownloader'],
        packages = ['gmapcatcher', 'gmapcatcher.mapServers',
                    'gmapcatcher.tilesRepo', 'gmapcatcher.widgets',
                    'gmapcatcher.gpxpy', 'gmapcatcher.gps']
    )
else:
    import py2exe
    DLL_EXCLUDES = [ 'libgdk-win32-2.0-0.dll',
                 'libgobject-2.0-0.dll',
                 'libgdk_pixbuf-2.0-0.dll',
                 'KERNELBASE.dll',
                 'MSIMG32.dll',
                 'NSI.dll',
                 'USP10.dll',
                 'intl.dll',
                 'freetype6.dll',
                 'libcairo-2.dll',
                 'libexpat-1.dll',
                 'libglib-2.0-0.dll',
                 'libgmodule-2.0-0.dll',
                 'libpango-1.0-0.dll',
                 'DNSAPI.dll',
                 'API-MS-Win-Core-SysInfo-L1-1-0.dll',
                 'API-MS-Win-Core-Misc-L1-1-0.dll',
                 'API-MS-Win-Core-IO-L1-1-0.dll',
                 'API-MS-Win-Core-File-L1-1-0.dll',
                 'API-MS-Win-Core-Debug-L1-1-0.dll',
                 'API-MS-Win-Core-Handle-L1-1-0.dll',
                 'API-MS-Win-Core-Localization-L1-1-0.dll',
                 'API-MS-Win-Core-Profile-L1-1-0.dll',
                 'API-MS-Win-Core-Heap-L1-1-0.dll',
                 'API-MS-Win-Core-Synch-L1-1-0.dll',
                 'API-MS-Win-Core-String-L1-1-0.dll',
                 'API-MS-Win-Core-DelayLoad-L1-1-0.dll',
                 'API-MS-Win-Core-LibraryLoader-L1-1-0.dll',
                 'API-MS-Win-Core-ErrorHandling-L1-1-0.dll',
                 'API-MS-Win-Core-ProcessThreads-L1-1-0.dll',
                 'API-MS-Win-Core-ProcessEnvironment-L1-1-0.dll',
                 'API-MS-Win-Core-LocalRegistry-L1-1-0.dll',
                 'w9xpopen.exe'] # is not excluded for some reasion
    setup(
        name = NAME,
        description = 'Offline Map Viewer',
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
                'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
                'dll_excludes': DLL_EXCLUDES,
            }
        },
        data_files = ['changelog', 'README']
    )
