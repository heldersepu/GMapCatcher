# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.mapHideMapServers
# Window to display a list of map servers.

import pygtk
pygtk.require('2.0')
import gtk
from mapConst import *
from widMapServers import WidMapServers


class MapHideMapServers():

    def __frame(self, conf):
        myTree = WidMapServers()
        frame = gtk.Frame()
        frame.set_border_width(10)
        frame.set_size_request(100, 75)
        frame.add(myTree.show(conf))
        return frame

    def __init__(self, parent):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_border_width(10)
        win.set_transient_for(parent)
        win.set_size_request(490, 320)
        win.set_destroy_with_parent(True)
        win.set_title(" GMapCatcher Map Servers ")
        win.connect('key-press-event', self.key_press_event, win)
        win.set_keep_above(True)

        frame = self.__frame(parent.conf)
        win.add(frame)
        win.show_all()

    def key_press_event(self, widget, event, window):
        # W = 87,119; Esc = 65307
        if event.keyval == 65307 or \
                (event.state & gtk.gdk.CONTROL_MASK) != 0 and \
                event.keyval in [87, 119]:
            window.destroy()

def main(parent):
    MapHideMapServers(parent)
