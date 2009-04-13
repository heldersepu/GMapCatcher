"""
interface like classe.
Implementer of the repository engine has to implement this methods.
"""

import os
import sys
import gtk
import gtk.gdk
import googleMaps
import traceback

class TilesRepos:
    
    def __init__(self, gm, params):
        pass

    def finish(self):
        pass

    def get_tile_pixbuf(self, zoom_level, coord, online, force_update ):
        pass