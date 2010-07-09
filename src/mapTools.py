# -*- coding: utf-8 -*-
## @package src.mapTools
# The tools widget, items are displayed in multiple tabs.

import pygtk
pygtk.require('2.0')
import gtk
import widTreeView
import widMySettings
import widChangeTheme
import widMyGPS
from mapConst import *


class MapTools():

    def __create_notebook(self, parent):
        filePath = parent.ctx_map.configpath
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show()

        myTree = widTreeView.TreeView()
        mySett = widMySettings.MySettings()
        myTheme = widChangeTheme.ChangeTheme()
        myGPS = widMyGPS.MyGPS()

        # Append pages to the notebook
        for str in TOOLS_MENU:
            frame = gtk.Frame()
            frame.set_border_width(10)
            frame.set_size_request(100, 75)
            if str in [TOOLS_MENU[1], TOOLS_MENU[2]]:
                frame.add(
                    myTree.show(str[5:-1], filePath +'/'+ str[5:], parent)
                )
            elif str == TOOLS_MENU[0]:
                frame.add(mySett.show(parent))
            elif str == TOOLS_MENU[3]:
                frame.add(myTheme.show(parent.conf))
            elif str == TOOLS_MENU[4]:
                frame.add(myGPS.show(parent.conf))
            else:
                frame.add(gtk.Label(str + ' coming soon!! '))
            label = gtk.Label(str)
            notebook.append_page(frame, label)
        # Set what page to start at
        return notebook

    def __init__(self, parent, start_page):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_border_width(10)
        win.set_transient_for(parent)
        win.set_size_request(650, 400)
        win.set_destroy_with_parent(True)
        win.set_title(" GMapCatcher Tools ")
        win.connect('key-press-event', self.key_press_event, win)

        myNotebook = self.__create_notebook(parent)
        win.add(myNotebook)
        win.show_all()
        myNotebook.set_current_page(start_page)

    def key_press_event(self, widget, event, window):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [87, 119]:
            # W = 87,119
            window.destroy()


def main(parent, start_page):
    MapTools(parent, start_page)

