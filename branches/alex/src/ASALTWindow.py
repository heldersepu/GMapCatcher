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
        visible = self.get_visible_rect()
	max_y_pos = visible.y + visible.height
	last_line_pos = sum(self.get_line_yrange(textbuffer.get_end_iter()))
	
	if last_line_pos > max_y_pos:
	        print "Line not visible"
	        self.scroll_to_iter(textbuffer.get_end_iter(), .0)
	else:
                print "Line visible" 
        
        
        
        #if(self.get_cursor_visible == False):
        #    print "cursor not visible"
        #    self.scroll_to_iter(textbuffer.get_end_iter(), .0)
        
        #self.scroll_to_iter(textbuffer.get_end_iter(), .0) 


class ASALTWindow(gtk.Window):
    loop = 0
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
            self.textview.append_text("Vehicle status updates go here!\n")

            sw.add(self.textview)
            vbox.pack_start(sw)
            return _frame(" Console ", vbox)


        def _buttons(strFolder):
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)

	    self.cb_dropmarker = gtk.CheckButton("_Loop Path")
	    self.cb_dropmarker.set_active(False)
	    self.cb_dropmarker.connect('clicked',self.set_loop)
            hbbox.pack_start(self.cb_dropmarker)

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

    def set_loop(self,w):
        if(self.loop ==1):
           self.loop = 0
           self.textview.append_text("path will NOT loop\n")
        else:
           self.loop = 1
           self.textview.append_text("path will now loop forever\n")
        print "loop =",self.loop


    def cancel(self,w):
        self.textview.append_text("cancel!\n")
        print "cancel!"

    def on_delete(self,*params):
        return False
