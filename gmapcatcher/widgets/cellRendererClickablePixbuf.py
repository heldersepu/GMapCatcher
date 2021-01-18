# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.cellRendererClickablePixbuf
# A window to add or remove markers.

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class CellRendererClickablePixbuf(gtk.CellRendererPixbuf):
    __gsignals__ = {'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,))}
    def __init__(self):
        gtk.CellRendererPixbuf.__init__(self)
        self.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)

    def do_activate(self, event, widget, path, background_area, cell_area, flags):
        self.emit('clicked', path)