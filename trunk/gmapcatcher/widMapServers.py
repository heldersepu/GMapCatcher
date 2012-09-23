# -*- coding: utf-8 -*-
## @package gmapcatcher.widMapServers
# Widget used to display the list of the MapServers
# Displayed inside MapHideMapServers.

from mapConst import *
import gtk


## This widget allows the user to modify visible map services
class WidMapServers():

    ## Appends items to a list from the given file
    def load(self, button, listStore):
        listStore.clear()
        bad_map_servers = self.conf.hide_map_servers.split(',')
        # add rows with text
        for intPos in range(len(MAP_SERVERS)):
            listStore.append([intPos, MAP_SERVERS[intPos], int(not str(intPos) in bad_map_servers)])
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        return listStore    

    ## Handle the 'edited' event of the cells
    def __cell_edited(self, cell, row, new_text, model, col):
        try:
            if col == 0:
                model[row][col] = new_text
            else:
                model[row][col] = int(new_text)
        except Exception:
            pass

    ## Save the curent list to the file
    def btn_save_clicked(self, button, listStore):
        strList = ''
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        for row in listStore:
            if row[2] == 0:
                strList += str(row[0]) + ','
        self.conf.hide_map_servers = strList
        self.conf.save()

    ## All the buttons below the list
    def __action_buttons(self, listStore):
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', self.load, listStore)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', self.btn_save_clicked, listStore)
        bbox.add(button)
        return bbox


    ## Put all the Widgets together
    def show(self, conf):
        self.conf = conf
        # create a listStore with one string column to use as the model
        listStore = gtk.ListStore(int, str, int)
        # create the TreeView using listStore
        myTree = gtk.TreeView(self.load(None, listStore))

        strCols = ['ID', 'Map Name', 'Status']
        for intPos in range(len(strCols)):
            # Create a CellRenderers to render the data
            cell = gtk.CellRendererText()
            # Allow Cells to be editable
            cell.connect('edited', self.__cell_edited, listStore, intPos)
            cell.set_property('editable', intPos > 1)
            # Create the TreeViewColumns to display the data
            tvcolumn = gtk.TreeViewColumn(strCols[intPos])
            myTree.append_column(tvcolumn)
            tvcolumn.pack_start(cell, True)
            tvcolumn.set_attributes(cell, text=intPos)
            tvcolumn.set_sort_column_id(intPos)
            tvcolumn.set_resizable(True)
            tvcolumn.set_expand(intPos == 1)

        # make myTree searchable by Map Name
        myTree.set_search_column(1)
        listStore.set_sort_column_id(0, gtk.SORT_ASCENDING)

        hpaned = gtk.VPaned()
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(myTree)
        hpaned.pack1(scrolledwindow, True, True)
        buttons = self.__action_buttons(listStore)
        hpaned.pack2(buttons, False, False)
        return hpaned
