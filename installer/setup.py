# -*- coding: utf-8 -*-
## @package setup
# Setup file used to build the Windows Installer

from distutils.core import setup
from src.mapConst import *
import os

if os.name == "posix":
    ico = "images/map.png"
    theoptions = None
    thedatafiles = [('share/doc/mapcatcher', ['README', 'Changelog'])]
else:
    ico = "images\maps.ico"
    import py2exe
    theoptions = {
        'py2exe': {
            'packages':'encodings',
            'includes': 'cairo, pango, pangocairo, atk, gobject',
            }
        }
    thedatafiles = ['Changelog', 'README']

setup(
    name = NAME,
    description = 'Offline Google Map Viewer',
    version = VERSION,
    url = WEB_ADDRESS,

    windows = [
                  {
                      'script': 'maps.py',
                      'icon_resources': [(1, ico)],
                  }
              ],

    options = theoptions,

    data_files = thedatafiles
)
