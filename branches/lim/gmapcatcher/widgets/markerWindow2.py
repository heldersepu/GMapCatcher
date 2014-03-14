# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.markerWindow2
# A window to add or remove markers.

import pygtk
pygtk.require('2.0')
import gtk
import mapPixbuf
from cellRendererClickablePixbuf import CellRendererClickablePixbuf


class markerWindow2(gtk.Window):

    def refresh_parent(self):
        self.prnt.marker.refresh()
        self.prnt.drawing_area.repaint()

    def btn_done(self, w):
        self.destroy()

    ## All the buttons below the items
    def __action_buttons(self):
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_EDGE)       
        button = gtk.Button('_Done')
        button.set_size_request(34, 35)
        button.connect('clicked', self.btn_done)
        bbox.add(button)
        hbox = gtk.HBox()
        hbox.pack_start(bbox,padding=10)
        return hbox


    def __top_right(self):
        vbox = gtk.VBox(False,10)
        hbox1 = gtk.HBox(False,10)
        hbox1.add(gtk.Button('Hello World'))
        hbox1.add(gtk.Button('Hello World'))
        hbox1.add(gtk.Button('Hello World'))
        
        hbox2 = gtk.HBox(False,10)
        hbox2.add(gtk.Button('Hello World'))
        hbox2.add(gtk.Button('Hello World'))
        hbox2.add(gtk.Button('Hello World'))
        vbox.add(hbox1)
        vbox.add(hbox2)
        box = gtk.VBox(False,10)
        box.set_border_width(10)
        box.add(vbox)
        return box
        
    def __top_frame(self):
        listStore = gtk.ListStore(gtk.gdk.Pixbuf)
        listStore.append([mapPixbuf.marker_pixbuf(self.marker)])
        myTree = gtk.TreeView(listStore)

        cell = CellRendererClickablePixbuf()
        tvcolumn = gtk.TreeViewColumn('', cell)
        tvcolumn.set_attributes(cell, pixbuf=0)
        myTree.append_column(tvcolumn)
        tvcolumn.set_expand(True)
        treeSel = myTree.get_selection()
        treeSel.set_mode(gtk.SELECTION_NONE)
        myTree.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        frame = gtk.Frame()
        frame.set_border_width(10)
        frame.add(myTree)
        hbox = gtk.HBox(False,10)
        hbox.add(frame)
        hbox.add(self.__top_right())
        return hbox

    def __controls(self):
        vbox = gtk.VBox(False)
        hpaned = gtk.VPaned()        
        frame = gtk.Frame()
        frame.add(self.__top_frame())
        hpaned.pack1(frame, True, True)
        hpaned.pack2(self.__action_buttons(), False, False)
        vbox.pack_start(hpaned)
        self.hpaned = hpaned
        return vbox

    def __init__(self, parent, coords, marker):
        gtk.Window.__init__(self)
        self.set_border_width(10)
        self.prnt = parent
        self.coords = coords
        self.marker = marker
        self.set_transient_for(parent)
        self.set_size_request(500, 180)
        self.set_destroy_with_parent(True)
        self.set_title(" Markers ")
        self.connect('key-press-event', self.key_press_event, self)
        self.connect('delete-event', self.on_delete)
        frame = gtk.Frame()
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(5)
        vbox.pack_start(self.__controls())
        frame.add(vbox)
        self.add(frame)
        self.set_border_width(2)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_decorated(False)
        self.show_all()
        self.hpaned.grab_focus()

    def on_delete(self, *args):
        self.hide()
        return False

    def key_press_event(self, widget, event, window):
        # W = 87,119; Esc = 65307
        if event.keyval == 65307 or \
                (event.state & gtk.gdk.CONTROL_MASK) != 0 and \
                event.keyval in [87, 119]:
            window.destroy()

def main():
    gtk.gdk.threads_init()
    markerWindow2(None, [10,10,2], "m_red.png")
    gtk.threads_enter()
    gtk.main()
    gtk.threads_leave()
if __name__ == "__main__":
    main()