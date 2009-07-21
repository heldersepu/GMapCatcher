## @package src.mapTools
# The tools widget, items are displayed in multiple tabs.

import pygtk
pygtk.require('2.0')
import gtk
import mapTreeView
import mapMySettings
import mapChangeTheme
from mapConst import *


class MainWindow():

    def __create_notebook(self, parent):
        filePath = parent.ctx_map.configpath
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show()

        myTree = mapTreeView.TreeView()
        mySett = mapMySettings.MySettings()
        myTheme = mapChangeTheme.ChangeTheme()

        # Append pages to the notebook
        for str in TOOLS_MENU:
            frame = gtk.Frame()
            frame.set_border_width(10)
            frame.set_size_request(100, 75)
            if str in [TOOLS_MENU[1], TOOLS_MENU[2]]:
                frame.add(myTree.show(str[5:-1], filePath +'/'+ str[5:]))
            elif str == TOOLS_MENU[0]:
                frame.add(mySett.show(parent))
            elif str == TOOLS_MENU[3]:
                frame.add(myTheme.show(parent.conf))
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
        win.set_size_request(600, 400)
        win.set_destroy_with_parent(True)
        win.set_title(" GMapCatcher Tools ")

        myNotebook = self.__create_notebook(parent)
        win.add(myNotebook)
        win.show_all()
        myNotebook.set_current_page(start_page)

def main(parent, start_page):
    MainWindow(parent, start_page)

if __name__ == "__main__":
    main()
