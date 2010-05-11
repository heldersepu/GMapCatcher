## @package src.mapTools
# The tools widget, items are displayed in multiple tabs.

import pygtk
pygtk.require('2.0')
import gtk
#import widTreeView
#import widMySettings
#import widChangeTheme
#import widMyGPS
#import widASALTsettings
#import widUploadsettings
import maps
from src.mapConst import *


class mainMapTools():



    def __create_notebook(self, parent):
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show()
        self.show_tabs = True
        self.show_border = True

#        myTree = widTreeView.TreeView()
#        mySett = widMySettings.MySettings()
#        myTheme = widChangeTheme.ChangeTheme()
#        myGPS = widMyGPS.MyGPS()
#        myASALT = widASALTsettings.ASALTsettings()
        mymaps = maps.MainWindow()

        # Append pages to the notebook
        for str in MAINTOOLS_MENU:
            frame = gtk.Frame()
            frame.set_border_width(10)
            frame.set_size_request(100, 75)
#            if str in [TOOLS_MENU[1], TOOLS_MENU[2]]:
#                frame.add(
#                    myTree.show(str[5:-1], filePath +'/'+ str[5:], parent)
#                )
            if str == MAINTOOLS_MENU[0]:
                frame.add(mymaps.show(parent))
#            elif str == TOOLS_MENU[3]:
#                frame.add(myTheme.show(parent.conf))
            else:
                frame.add(gtk.Label(str + ' coming soon!! '))
            label = gtk.Label(str)
            notebook.append_page(frame, label)
        # Set what page to start at
        return notebook

    def __init__(self, parent):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_border_width(10)
       # win.set_transient_for(parent)
        win.set_size_request(720, 400)
        win.set_destroy_with_parent(True)
        win.set_title(" GMapCatcher ")

        myNotebook = self.__create_notebook(parent)
        win.add(myNotebook)
        win.show_all()
        myNotebook.set_current_page(0)

def main():
    mainMapTools(parent)

if __name__ == "__main__":
    main()