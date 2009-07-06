## @package mapPixBuf
# Get pixbuf from files

import gtk
from mapConst import *


def missing():
    try:
        pix_missing = gtk.gdk.pixbuf_new_from_file('missing.png')
    except Exception:
        pix_missing = gtk.gdk.pixbuf_new_from_data('\255\255\255' * 100000,
            gtk.gdk.COLORSPACE_RGB, False, 8,
            TILES_WIDTH, TILES_HEIGHT, TILES_HEIGHT * 3)
    return pix_missing

def cross():
    try:
        pix_cross = gtk.gdk.pixbuf_new_from_file('cross.png')
    except Exception:
        pix_cross = gtk.gdk.pixbuf_new_from_data('\255\255\255' * 1000,
            gtk.gdk.COLORSPACE_RGB, False, 8, 12, 12, 12 * 3)
    return pix_cross

