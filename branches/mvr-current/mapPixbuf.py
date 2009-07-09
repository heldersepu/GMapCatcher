## @package mapPixBuf
# Get the Pixbuf from image files.
#

import gtk
from mapConst import *

## Get the Pixbuf from missing.png
def missing():
    try:
        pix_missing = gtk.gdk.pixbuf_new_from_file('images\missing.png')
    except Exception:
        pix_missing = gtk.gdk.pixbuf_new_from_data('\255\255\255' * 100000,
            gtk.gdk.COLORSPACE_RGB, False, 8,
            TILES_WIDTH, TILES_HEIGHT, TILES_HEIGHT * 3)
    return pix_missing

## Get the Pixbuf from cross.png
def cross():
    try:
        pix_cross = gtk.gdk.pixbuf_new_from_file('images\cross.png')
    except Exception:
        pix_cross = gtk.gdk.pixbuf_new_from_data(
            ('\255\255\255' * 4 + '\0\0\255' * 4 + '\255\255\255' * 4) * 4 +
            ('\0\0\255' * 12) * 4 +
            ('\255\255\255' * 4 + '\0\0\255' * 4 + '\255\255\255' * 4) * 4,
            gtk.gdk.COLORSPACE_RGB, False, 8, 12, 12, 12 * 3)
    return pix_cross

## Get the Pixbuf from the given image.
# This is used in myToolTip
def getImage(filename):
    try:
        pix_buf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 56, 56)
    except Exception:
        pix_buf = gtk.gdk.pixbuf_new_from_data(
            ('\255\0\0' * 18 + '\0\0\255' * 20 + '\255\0\0' * 18) * 18 +
            ('\0\0\255' * 56) * 20 +
            ('\255\0\0' * 18 + '\0\0\255' * 20 + '\255\0\0' * 18) * 18,
            gtk.gdk.COLORSPACE_RGB, False, 8, 56, 56, 56 * 3)
    return pix_buf
