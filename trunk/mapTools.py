import maps
import pygtk
pygtk.require('2.0')
import gtk
from mapConst import *

class MainWindow:

    def delete(self, widget, event=None):
        gtk.main_quit()
        return False

    def __create_notebook(self, start_page):
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show()
        
        self.show_tabs = True
        self.show_border = True

        # Append pages to the notebook
        for str in TOOLS_MENU:
            frame = gtk.Frame()
            frame.set_border_width(10)
            frame.set_size_request(100, 75)
            frame.show()

            label = gtk.Label(str)
            notebook.append_page(frame, label)

        # Set what page to start at 
        notebook.set_current_page(start_page)
        self.notebook = notebook
        return notebook

    def __init__(self, parent, start_page):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_border_width(10)
        window.set_transient_for(parent)
        window.set_size_request(600, 400)
        window.set_title(" GMapCatcher Tools ")
        window.connect("delete_event", self.delete)
        window.add(self.__create_notebook(start_page))
        window.show()
        self.window = window

def main(parent, start_page = 0):
    MainWindow(parent, start_page)
    gtk.main()

if __name__ == "__main__":
    main()
