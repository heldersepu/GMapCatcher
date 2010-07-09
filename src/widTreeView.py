# -*- coding: utf-8 -*-
## @package src.widTreeView
# TreeView widget used to display the list of the locations.
# Displayed inside a tab in MapTools.

import gtk
import fileUtils
from mapConst import *

## This widget allows the user to modify the locations and markers
class TreeView():

    ## Appends items to a list from the given file
    def __read_file(self, strInfo, strFilePath, listStore):
        locations = fileUtils.read_file(strInfo, strFilePath)
        # add rows with text
        if locations:
            for strLoc in locations.keys():
                listStore.append([strLoc , locations[strLoc][0],
                                  locations[strLoc][1], locations[strLoc][2]])
        return listStore

    ## Writes a given list to the file
    def __write_file(self, strInfo, strFilePath, listStore):
        locations = {}
        for row in listStore:
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
    def btn_add_clicked(self, button, listStore, myTree):
        strName = ' New'
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        for row in listStore:
            if row[0] == strName:
                strName = strName + "1"
            elif row[0][0] > strName[0]:
                break
        iter = listStore.append([strName, 0, 0, MAP_MAX_ZOOM_LEVEL - 2])
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.change_selection(myTree, listStore.get_path(iter))

    ## Remove selected row from the list
    def btn_remove_clicked(self, button, listStore, myTree):
        treeSelection = myTree.get_selection()
        model, iter = treeSelection.get_selected()
        if iter:
            intPath = listStore.get_path(iter)
            listStore.remove(iter)
            if model.get_iter_first():
                self.change_selection(myTree, intPath)

    ## Reload the list from the file
    def btn_revert_clicked(self, button, strInfo, filePath, listStore, myTree):
        listStore.clear()
        myTree.set_model(self.__read_file(strInfo, filePath, listStore))
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        myTree.grab_focus()

    ## Save the curent list to the file
    def btn_save_clicked(self, button, strInfo, filePath, listStore, parent):
        self.__write_file(strInfo, filePath, listStore)
        parent.marker.refresh()
        parent.drawing_area.repaint()

    ## All the buttons below the list
    def __action_buttons(self, strInfo, filePath, listStore, myTree, parent):
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_ADD)
        button.connect('clicked', self.btn_add_clicked, listStore, myTree)
        bbox.add(button)

        gtk.stock_add([(gtk.STOCK_REMOVE, "_Delete", 0, 0, "")])
        button = gtk.Button(stock=gtk.STOCK_REMOVE)
        button.connect('clicked', self.btn_remove_clicked, listStore, myTree)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', self.btn_revert_clicked,
                        strInfo, filePath, listStore, myTree)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', self.btn_save_clicked,
                        strInfo, filePath, listStore, parent)
        bbox.add(button)
        return bbox

    ## Handle the delete key
    def key_press_tree(self, w, event, *args):
        if event.keyval == 65535:
            self.btn_remove_clicked(None, args[0], w)
            return True
        elif len(args) == 4:
            return self.key_press(w, event, args[0], args[1], args[2], args[3])
        return False
            
    def key_press(self, w, event, *args):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [83, 115]:
            # S = 83, 115
            self.btn_save_clicked(0, args[0], args[1], args[2], args[3])
        return False

    ## Put all the TreeView Widgets together
    def show(self, strInfo, filePath, parent):
        # create a listStore with one string column to use as the model
        listStore = gtk.ListStore(str, str, str, int)

        # create the TreeView using listStore
        myTree = gtk.TreeView(self.__read_file(strInfo, filePath, listStore))
        myTree.connect("key-press-event", self.key_press_tree, listStore)

        strCols = ['Location', 'Latitude', 'Longitude', 'Zoom']
        for intPos in range(len(strCols)):
            # Create a CellRenderers to render the data
            cell = gtk.CellRendererText()
            # Allow Cells to be editable
            cell.set_property('editable', True)
            cell.connect('edited', self.__cell_edited, listStore, intPos)
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
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)

        hpaned = gtk.VPaned()
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(myTree)
        hpaned.pack1(scrolledwindow, True, True)

        buttons = self.__action_buttons(strInfo, filePath,
                                        listStore, myTree, parent)
        hpaned.connect('key-press-event', self.key_press, strInfo, filePath,
                       listStore, parent)
        hpaned.pack2(buttons, False, False)
        return hpaned

