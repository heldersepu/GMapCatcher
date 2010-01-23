## @package src.ASALTWindow
# Widget that for the ASALT vehicle

import pygtk
pygtk.require('2.0')
import gtk

from customWidgets import _SpinBtn, _myEntry, _frame, lbl, FileChooser
from os.path import join, isdir


class TextViewConsole(gtk.TextView):
    def __init__(self):
        super(TextViewConsole, self).__init__()
        self.set_editable(False)

    def append_text(self, strText):
        textbuffer = self.get_buffer()
        textbuffer.insert_at_cursor(strText)


class ASALTWindow(gtk.Window):

    def __init__(self, layer, init_path, mapServ, styleID):

        def _console():
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)

            #hbox.pack_start(lbl("latitude:"))
            #vbox.pack_start(hbox)
            #hbox = gtk.HBox(False, 10)
            #hbox.pack_start(lbl("longitude:"))
            #vbox.pack_start(hbox)

            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.textview = TextViewConsole()
            self.textview.append_text("AKFYAH!\n")

            sw.add(self.textview)
            vbox.pack_start(sw)
            return _frame(" Console ", vbox)


        def _buttons(strFolder):
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)

            gtk.stock_add([(gtk.STOCK_APPLY, "_Transmit Path", 0, 0, "")])
            self.b_download = gtk.Button(stock=gtk.STOCK_APPLY)
            self.b_download.connect('clicked', self.transmit)
            hbbox.pack_start(self.b_download)

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
        self.textview.append_text("transmitting!\n")
        print "transmitting!"

    def do_open(self):
        self.textview.append_text("opening!\n")
        print "opening!"

    def cancel(self,w):
        self.textview.append_text("cancel!\n")
        print "cancel!"

    def on_delete(self,*params):
        return False
