## @package setup
# Setup file used to build the Windows Installer

from distutils.core import setup
from src.mapConst import *
import py2exe

setup(
    name = NAME,
    description = 'Offline Google Map Viewer',
    version = VERSION,
    url = WEB_ADDRESS,

    windows = [
                  {
                      'script': 'maps.py',
                      'icon_resources': [(1, "images\maps.ico")],
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gobject',
                  }
              },

    data_files = ['Changelog', 'README']
)
