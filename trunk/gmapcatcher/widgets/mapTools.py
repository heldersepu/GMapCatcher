# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.mapTools
# The tools widget, items are displayed in multiple tabs.

import pygtk
pygtk.require('2.0')
import gtk
import widTreeView
import widMySettings
import widChangeTheme
import widMyGPS
from gmapcatcher.mapConst import *


class mapTools(gtk.Window):

    def __create_notebook(self, parent):
        filePath = parent.ctx_map.configpath
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show()

        myTree = widTreeView.TreeView()
        mySett = widMySettings.MySettings()
        myTheme = widChangeTheme.ChangeTheme(parent)
        myGPS = widMyGPS.MyGPS()

        # Append pages to the notebook
        for str in TOOLS_MENU:
            if str != "":
                frame = gtk.Frame()
                frame.set_border_width(10)
                frame.set_size_request(100, 75)
                if str in [TOOLS_MENU[1], TOOLS_MENU[2]]:
                    frame.add(
                        myTree.show(str[5:-1], filePath + '/' + str[5:], parent)
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

    def __init__(self, mapsObj, start_page):
        gtk.Window.__init__(self)
        self.set_border_width(10)
        # self.set_transient_for(mapsObj)
        self.set_size_request(600, 480)
        self.set_destroy_with_parent(True)
        self.set_title(" GMapCatcher Tools ")
        self.connect('key-press-event', self.key_press_event, self)
        self.connect('delete-event', self.on_delete)
        self.mapsObj = mapsObj

        self.myNotebook = self.__create_notebook(mapsObj)
        self.add(self.myNotebook)
        self.show_all()
        self.myNotebook.set_current_page(start_page)

    def on_delete(self, widget, event):
        self.mapsObj.settingsw = None

    def key_press_event(self, widget, event, window):
        # W = 87,119; Esc = 65307
        if event.keyval == 65307 or \
                (event.state & gtk.gdk.CONTROL_MASK) != 0 and \
                event.keyval in [87, 119]:
            self.mapsObj.settingsw = None
            window.destroy()
