import pygtk
pygtk.require('2.0')
import gtk
import fileUtils
from mapConst import *

class TreeView():

    def __read_file(self, strFilePath):
        return fileUtils.read_file('location',strFilePath)

    def __write_file(self, strFilePath):
        locations = {}
        for row in self.liststore:
            locations[row[0]] = (float(row[1]), float(row[2]), int(row[3]))
        fileUtils.write_file('location',strFilePath, locations)

    def __cell_edited(self, cell, row, new_text, model, col):
        try:
            if col == 0:
                model[row][col] = new_text
            elif col == 3:
                model[row][col] = int(new_text)
            else:
                model[row][col] = float(new_text)
        except Exception:
            pass

    def show(self, filePath):
        locations = self.__read_file(filePath)

        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(str, float, float, int)

        # create the TreeView using liststore
        myTree = gtk.TreeView(self.liststore)

        # add rows with text
        for strLoc in locations.keys():
            self.liststore.append([strLoc , locations[strLoc][0],
                                locations[strLoc][1], locations[strLoc][2]])

        strCols = ['Location', 'Latitude', 'Longitude', 'Zoom']
        for intPos in range(len(strCols)):
            # Create a CellRenderers to render the data
            cell = gtk.CellRendererText()
            # Allow Cells to be editable
            cell.set_property('editable', True)
            cell.connect('edited', self.__cell_edited, self.liststore, intPos)
            # Create the TreeViewColumns to display the data
            tvcolumn = gtk.TreeViewColumn(strCols[intPos])
            myTree.append_column(tvcolumn)
            tvcolumn.pack_start(cell, True)
            tvcolumn.set_attributes(cell, text=intPos)
            tvcolumn.set_sort_column_id(intPos)
            tvcolumn.set_resizable(True)
            if intPos == 0:
                tvcolumn.set_expand(True)
            else:
                tvcolumn.set_min_width(75)

        # make myTree searchable by location
        myTree.set_search_column(0)
        self.liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)

        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(myTree)
        return scrolledwindow

class MainWindow:

    def __create_notebook(self, filePath):
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show()

        self.show_tabs = True
        self.show_border = True
        myTree = TreeView()

        # Append pages to the notebook
        for str in TOOLS_MENU:
            frame = gtk.Frame()
            frame.set_border_width(10)
            frame.set_size_request(100, 75)
            if str in [TOOLS_MENU[1], TOOLS_MENU[2]]:
                frame.add(myTree.show(filePath +'/'+ str[5:]))
            else:
                frame.add(gtk.Label(str + ' coming soon!! '))
            label = gtk.Label(str)
            notebook.append_page(frame, label)
        # Set what page to start at
        return notebook

    def __init__(self, parent, configpath, start_page):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_border_width(10)
        win.set_transient_for(parent)
        win.set_size_request(600, 400)
        win.set_destroy_with_parent(True)
        win.set_title(" GMapCatcher Tools ")

        myNotebook = self.__create_notebook(configpath)
        win.add(myNotebook)
        win.show_all()
        myNotebook.set_current_page(start_page)

def main(parent, configpath, start_page):
    MainWindow(parent, configpath, start_page)

if __name__ == "__main__":
    main()
