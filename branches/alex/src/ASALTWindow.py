## @package src.DLWindow
# Widget that allows Download of entire locations

import pygtk
pygtk.require('2.0')
import gtk

from customWidgets import _SpinBtn, _myEntry, _frame, lbl, FileChooser

import mapUtils
import mapServices
from mapConst import *
from gtkThread import *
from os.path import join, isdir


class ASALTWindow(gtk.Window):

    def __init__(self, layer, init_path, mapServ, styleID):

        def _zoom(zoom0, zoom1):
            out_hbox = gtk.HBox(False, 50)
            out_hbox.set_border_width(10)
            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("min:"), False)
            self.s_zoom0 = _SpinBtn(zoom0)
            self.s_zoom0.set_digits(0)
            in_hbox.pack_start(self.s_zoom0)
            out_hbox.pack_start(in_hbox)

            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("max:"), False)
            self.s_zoom1 = _SpinBtn(zoom1)
            self.s_zoom1.set_digits(0)
            in_hbox.pack_start(self.s_zoom1)
            out_hbox.pack_start(in_hbox)
            hbox = gtk.HBox()
            hbox.set_border_width(10)
            hbox.pack_start(_frame(" Zoom ", out_hbox, 0))
            return hbox

        def _console():
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("latitude:"))
            
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("longitude:"))
            
            vbox.pack_start(hbox)
            return _frame(" Console ", vbox)

        def _area():
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("width:"))
            #self.e_kmx = _myEntry("%.6g" % kmx, 10, False)
            #hbox.pack_start(self.e_kmx, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("height:"))
            #self.e_kmy = _myEntry("%.6g" % kmy, 10, False)
            #hbox.pack_start(self.e_kmy, False)
            vbox.pack_start(hbox)
            return _frame(" Area (km) ", vbox)

        def _buttons(strFolder):
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)

	    gtk.stock_add([(gtk.STOCK_APPLY, "_Transmit Path", 0, 0, "")])	
            self.b_download = gtk.Button(stock=gtk.STOCK_APPLY)
            self.b_download.connect('clicked', self.transmit)
            hbbox.pack_start(self.b_download)

            hbox = gtk.HBox()
            

            self.b_cancel = gtk.Button(stock='gtk-cancel')
            self.b_cancel.connect('clicked', self.cancel)
            self.b_cancel.set_sensitive(True)

            hbbox.pack_start(self.b_cancel)
            return hbbox

        fldDown = join(init_path, 'asalt')
        self.mapService = mapServ
        self.styleID = styleID

        self.layer = layer
        gtk.Window.__init__(self)


        vbox = gtk.VBox(False)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_console())
        vbox.pack_start(hbox)
        
        vbox.pack_start(_buttons(fldDown))

        
        self.add(vbox)

        self.set_title("ASALT Vehicle Control")
        self.set_border_width(10)

        self.complete=[]
        self.processing=False
        self.gmap=None
        self.downloader=None
        self.connect('delete-event', self.on_delete)
        self.show_all()



    def transmit(self,w):
        print "transmitting!"

    def do_open(self):
        print "opening!"
        
    def cancel(self,w):
        print "cancel!"
        
        
    def on_delete(self,*params):
        return False    