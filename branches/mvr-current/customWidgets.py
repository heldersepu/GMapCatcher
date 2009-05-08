import gtk
import fileUtils
from mapConst import *
from inputValidation import allow_only_numbers


def lbl(text):
    l = gtk.Label(text)
    l.set_justify(gtk.JUSTIFY_RIGHT)
    return l

def _frame(strName, container, spacing = 5):
    frame = gtk.Frame(strName)
    vbox = gtk.VBox(False, spacing)
    vbox.set_border_width(spacing)
    vbox.pack_start(container)
    frame.add(vbox)
    return frame

def _SpinBtn(value=0, lower=MAP_MIN_ZOOM_LEVEL,
             upper=MAP_MAX_ZOOM_LEVEL, step=1, maxChars=2):
    a_zoom = gtk.Adjustment(value, lower, upper, step)
    spin = gtk.SpinButton(a_zoom)
    spin.connect('insert-text', allow_only_numbers, maxChars)
    return spin

def _myEntry(strText, maxChars=8, isInt=True):
    myEntry = gtk.Entry()
    myEntry.set_text(strText)
    myEntry.connect('insert-text', allow_only_numbers, maxChars, isInt)
    return myEntry


class MySettings():

    def show(self, parent):
        def _size(width, height):
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("Width:"), False)
            self.s_width = _SpinBtn(width, 450, 1024, 100, 4)
            hbox.pack_start(self.s_width)

            hbox.pack_start(lbl("Height:"), False)
            self.s_height = _SpinBtn(height, 400, 768, 100, 4)
            hbox.pack_start(self.s_height)
            return _frame(" Size ", hbox)

        def _zoom(zoom):
            hbox = gtk.HBox(False, 10)
            self.s_zoom = _SpinBtn(zoom)
            hbox.pack_start(self.s_zoom, False)
            return _frame(" Zoom ", hbox)

        def _center(center):
            hbox = gtk.HBox(False, 0)
            hbox.pack_start(lbl(" (( "), False)
            self.s_center00 = _SpinBtn(center[0][0], 0, 999999, 1, 6)
            hbox.pack_start(self.s_center00, False)
            hbox.pack_start(lbl(" ,  "), False)
            self.s_center01 = _SpinBtn(center[0][1], 0, 999999, 1, 6)
            hbox.pack_start(self.s_center01, False)
            hbox.pack_start(lbl(" ), ( "), False)
            self.s_center10 = _SpinBtn(center[1][0], 0, 256, 32, 3)
            hbox.pack_start(self.s_center10, False)
            hbox.pack_start(lbl(" ,  "), False)
            self.s_center11 = _SpinBtn(center[1][1], 0, 256, 32, 3)
            hbox.pack_start(self.s_center11, False)
            hbox.pack_start(lbl(" )) "), False)
            return _frame(" Center ", hbox)

        def _action_buttons(conf):
            def btn_revert_clicked(button):
                self.s_center00.set_value(conf.init_center[0][0])
                self.s_center01.set_value(conf.init_center[0][1])
                self.s_center10.set_value(conf.init_center[1][0])
                self.s_center11.set_value(conf.init_center[1][1])

                self.s_zoom.set_value(conf.init_zoom)
                self.s_width.set_value(conf.init_width)
                self.s_height.set_value(conf.init_height)

            def btn_save_clicked(button):
                conf.init_center = ((self.s_center00.get_value_as_int()),
                                    (self.s_center01.get_value_as_int())), \
                                   ((self.s_center10.get_value_as_int()),
                                    (self.s_center11.get_value_as_int()))

                conf.init_zoom = self.s_zoom.get_value_as_int()
                conf.init_width = self.s_width.get_value_as_int()
                conf.init_height = self.s_height.get_value_as_int()
                conf.save()

            bbox = gtk.HButtonBox()
            bbox.set_layout(gtk.BUTTONBOX_END)
            bbox.set_border_width(10)
            bbox.set_spacing(60)

            button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
            button.connect('clicked', btn_revert_clicked)
            bbox.add(button)

            button = gtk.Button(stock=gtk.STOCK_SAVE)
            button.connect('clicked', btn_save_clicked)
            bbox.add(button)
            return bbox

        def btn_use_current(button, parent):
            self.s_center00.set_value(parent.center[0][0])
            self.s_center01.set_value(parent.center[0][1])
            self.s_center10.set_value(parent.center[1][0])
            self.s_center11.set_value(parent.center[1][1])
            self.s_zoom.set_value(parent.current_zoom_level)

        hpaned = gtk.VPaned()
        vbox = gtk.VBox()
        vbox.set_border_width(10)

        hbox = gtk.HBox(False, 10)
        conf = parent.conf
        hbox.pack_start(_size(conf.init_width, conf.init_height))
        hbox.pack_start(_zoom(conf.init_zoom), False)
        vbox.pack_start(hbox, False)

        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_center(conf.init_center))
        bbox = gtk.HButtonBox()
        button = gtk.Button("Use Current")
        button.connect('clicked', btn_use_current, parent)
        bbox.add(button)
        hbox.pack_start(bbox)

        vbox.pack_start(hbox, False)
        hpaned.pack1(vbox, True, True)
        hpaned.pack2(_action_buttons(conf), False, False)
        return hpaned


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
