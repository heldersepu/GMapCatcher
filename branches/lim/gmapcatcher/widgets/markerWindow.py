# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.markerWindow
# A window to add or remove markers.

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import mapPixbuf
from customMsgBox import user_confirm


class CellRendererClickablePixbuf(gtk.CellRendererPixbuf):
    __gsignals__ = {'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,))}
    def __init__(self):
        gtk.CellRendererPixbuf.__init__(self)
        self.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)

    def do_activate(self, event, widget, path, background_area, cell_area, flags):
        self.emit('clicked', path)

class markerWindow(gtk.Window):

    def refresh_parent(self):
        self.prnt.marker.refresh()
        self.prnt.drawing_area.repaint()
    
    def btn_del_all(self, w):
        confirm = user_confirm(self, 'Are you sure you want to delete all markers?')
        if confirm == gtk.RESPONSE_YES:
            self.prnt.marker.del_all()
            self.refresh_parent()
            self.destroy()
            
    def btn_del_last(self, w):
        confirm = user_confirm(self, 'Are you sure you want to delete last marker?')
        if confirm == gtk.RESPONSE_YES:
            self.prnt.marker.del_last()
            self.refresh_parent()
            self.destroy()
        
    def btn_cancel(self, w):
        self.destroy()

    ## All the buttons below the items
    def __action_buttons(self):
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_EDGE)
        hbbox = gtk.HButtonBox()
        hbbox.set_border_width(10)
        hbbox.set_spacing(60)

        button = gtk.Button('Delete _All')
        button.set_size_request(95, 35)
        button.connect('clicked', self.btn_del_all)
        hbbox.add(button)

        button = gtk.Button('Delete _Last')
        button.set_size_request(95, 35)
        button.connect('clicked', self.btn_del_last)
        hbbox.add(button)

        button = gtk.Button('_Cancel')
        button.set_size_request(34, 35)
        button.connect('clicked', self.btn_cancel)
        
        bbox.add(hbbox)
        hbbox = gtk.HButtonBox()
        hbbox.set_layout(gtk.BUTTONBOX_END)
        hbbox.add(button)       
        bbox.add(hbbox)
        hbox = gtk.HBox()
        hbox.pack_start(bbox,padding=10)
        return hbox
    
    def __cell_clicked(self, w, intRow, listStore, intCol):
        print listStore[intRow][intCol+1]
        print ""
    
    def __top_frame(self):
        pb = gtk.gdk.Pixbuf
        listStore = gtk.ListStore(pb,str, pb,str, pb,str, pb,str, pb,str)
        pb = []
        pbs = []
        for marker in mapPixbuf.getMarkers():            
            pb.append(mapPixbuf.marker_pixbuf(marker))
            pb.append(marker)
            if len(pb) == 10:
                pbs.append(pb)
                pb = []
        if len(pb) > 0:
            for i in range(10-len(pb)):
                pb.append(None)
            pbs.append(pb)
        for pb in pbs:
            listStore.append(pb)
        
        myTree = gtk.TreeView(listStore)        
        for intRow in range(5):
            cell = CellRendererClickablePixbuf()
            cell.connect('clicked', self.__cell_clicked, listStore, intRow*2)
            tvcolumn = gtk.TreeViewColumn('', cell)
            tvcolumn.set_attributes(cell, pixbuf=intRow*2)
            myTree.append_column(tvcolumn)
            tvcolumn.set_expand(True)        
        treeSel = myTree.get_selection()
        treeSel.set_mode(gtk.SELECTION_NONE)
        myTree.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        return myTree
    
    def __controls(self):        
        vbox = gtk.VBox(False)
        hpaned = gtk.VPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        sw.add(self.__top_frame())
        frame = gtk.Frame()
        frame.add(sw)
        hpaned.pack1(frame, True, True)
        hpaned.pack2(self.__action_buttons(), False, False)
        vbox.pack_start(hpaned)
        self.hpaned = hpaned
        return vbox

    def __init__(self, parent, coords):
        gtk.Window.__init__(self)
        self.set_border_width(10)
        self.prnt = parent
        self.set_transient_for(parent)
        self.set_size_request(500, 350)
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
    markerWindow()
    gtk.threads_enter()
    gtk.main()
    gtk.threads_leave()
if __name__ == "__main__":
    main()