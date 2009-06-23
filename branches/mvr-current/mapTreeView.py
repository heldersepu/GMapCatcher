## @file mapTreeView.py
# ToDo

import gtk
import fileUtils
from mapConst import *


class TreeView():

    ## Appends items to a list from the given file
    def __read_file(self, strInfo, strFilePath, liststore):
        locations = fileUtils.read_file(strInfo, strFilePath)
        # add rows with text
        if locations:
            for strLoc in locations.keys():
                liststore.append([strLoc , locations[strLoc][0],
                                  locations[strLoc][1], locations[strLoc][2]])
        return liststore

    ## Writes a given list to the file
    def __write_file(self, strInfo, strFilePath, liststore):
        locations = {}
        for row in liststore:
            locations[row[0]] = (float(row[1]), float(row[2]), int(row[3]))
        fileUtils.write_file(strInfo, strFilePath, locations)

    ## Handle the 'edited' event of the cells
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

    ## Change the selection
    def change_selection(self, myTree, intPath):
        if intPath >= 0:
            myTree.set_cursor(intPath)
            myTree.grab_focus()

    ## Add a row to the list
    def btn_add_clicked(self, button, liststore, myTree):
        iter = liststore.append([' New', 0, 0, MAP_MAX_ZOOM_LEVEL - 2])
        liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.change_selection(myTree, liststore.get_path(iter))

    ## Remove selected row from the list
    def btn_remove_clicked(self, button, liststore, myTree):
        treeSelection = myTree.get_selection()
        model, iter = treeSelection.get_selected()
        if iter:
            intPath = liststore.get_path(iter)
            liststore.remove(iter)
            if model.get_iter_first():
                self.change_selection(myTree, intPath)

    ## Reload the list from the file
    def btn_revert_clicked(self, button, strInfo, filePath, liststore, myTree):
        liststore.clear()
        myTree.set_model(self.__read_file(strInfo, filePath, liststore))
        liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        myTree.grab_focus()

    ## Save the curent list to the file
    def btn_save_clicked(self, button, strInfo, filePath, liststore):
        self.__write_file(strInfo, filePath, liststore)

    ## All the buttons below the list
    def __action_buttons(self, strInfo, filePath, liststore, myTree):
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_ADD)
        button.connect('clicked', self.btn_add_clicked, liststore, myTree)
        bbox.add(button)

        gtk.stock_add([(gtk.STOCK_REMOVE, "_Delete", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_REMOVE)
        button.connect('clicked', self.btn_remove_clicked, liststore, myTree)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', self.btn_revert_clicked,
                        strInfo, filePath, liststore, myTree)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', self.btn_save_clicked,
                        strInfo, filePath, liststore)
        bbox.add(button)
        return bbox

    ## Handle the delete key
    def key_press_tree(self, w, event, liststore):
        if event.keyval == 65535:
            self.btn_remove_clicked(None, liststore, w)
            return True

    ## Put all the TreeView Widgets together
    def show(self, strInfo, filePath):
        # create a liststore with one string column to use as the model
        liststore = gtk.ListStore(str, float, float, int)

        # create the TreeView using liststore
        myTree = gtk.TreeView(self.__read_file(strInfo, filePath, liststore))
        myTree.connect("key-press-event", self.key_press_tree, liststore)

        strCols = ['Location', 'Latitude', 'Longitude', 'Zoom']
        for intPos in range(len(strCols)):
            # Create a CellRenderers to render the data
            cell = gtk.CellRendererText()
            # Allow Cells to be editable
            cell.set_property('editable', True)
            cell.connect('edited', self.__cell_edited, liststore, intPos)
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
        liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)

        hpaned = gtk.VPaned()
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(myTree)
        hpaned.pack1(scrolledwindow, True, True)

        buttons = self.__action_buttons(strInfo, filePath, liststore, myTree)
        hpaned.pack2(buttons, False, False)
        return hpaned

