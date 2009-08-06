## @package src.mapPixbuf
# Get the Pixbuf from image files.
#

import os
import gtk
from mapConst import *

## Get the Pixbuf from missing.png
def missing():
    try:
        pix_missing = gtk.gdk.pixbuf_new_from_file(os.path.join('images', 'missing.png'))
    except Exception:
        pix_missing = gtk.gdk.pixbuf_new_from_data('\255\255\255' * 100000,
            gtk.gdk.COLORSPACE_RGB, False, 8,
            TILES_WIDTH, TILES_HEIGHT, TILES_HEIGHT * 3)
    return pix_missing

## Get the Pixbuf from cross.png
def cross():
    try:
        pix_cross = gtk.gdk.pixbuf_new_from_file(os.path.join('images', 'cross.png'))
    except Exception:
        pix_cross = gtk.gdk.pixbuf_new_from_data(
            ('\255\255\255' * 4 + '\0\0\255' * 4 + '\255\255\255' * 4) * 4 +
            ('\0\0\255' * 12) * 4 +
            ('\255\255\255' * 4 + '\0\0\255' * 4 + '\255\255\255' * 4) * 4,
            gtk.gdk.COLORSPACE_RGB, False, 8, 12, 12, 12 * 3)
    return pix_cross

## Get the Pixbuf from the given image.
# This is used in myToolTip
def getImage(filename, intWidth=56, intHeight=56):
    try:
        pix_buf = gtk.gdk.pixbuf_new_from_file_at_size(filename, intWidth, intHeight)
    except Exception:
        wCo = int(intWidth / 3)
        wMe = intWidth - 2 * wCo
        hCo = int(intHeight / 3)
        hMe = intHeight - 2 * wCo
        pix_buf = gtk.gdk.pixbuf_new_from_data(
            ('\255\0\0' * wCo + '\0\0\255' * wMe + '\255\0\0' * wCo) * hCo +
            ('\0\0\255' * intWidth) * hMe +
            ('\255\0\0' * wCo + '\0\0\255' * wMe + '\255\0\0' * wCo) * hCo,
            gtk.gdk.COLORSPACE_RGB, False, 8, intWidth, intHeight, intHeight * 3)
    return pix_buf
