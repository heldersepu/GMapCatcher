## @package src.ASALTWindow
# Widget that for the ASALT vehicle

import os
import pygtk
pygtk.require('2.0')
import gtk
import time
import fileUtils
import src.ASALTradio as ASALTradio
from threading import Event, Thread

from customWidgets import _SpinBtn, _myEntry, _frame, lbl, FileChooser
from os.path import join, isdir


#Auto status updater thread
class AutoUpdater(Thread):
    def __init__(self,interval,update_function):
        Thread.__init__(self)
        self.interval = interval
        self.finished = Event()
        self.update = update_function
        self.event = Event()    
    
    def run(self):
        while not self.finished.isSet():
            self.event.wait(self.interval)
            if not self.finished.isSet() and not self.event.isSet():
                #self.console.append_text("update!\n")
                self.update();

    def cancel(self):
        self.finished.set()
        self.event.set()


#Text View console where vehicle information will be printed to screen
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
	        self.scroll_to_iter(textbuffer.get_end_iter(), .0)
	

class ASALTWindow(gtk.Window):
    loop = 0
    auto_update = 0
    astlr = ASALTradio.ASALTradio()
    def __init__(self, init_path, markers, valid):
        
        def _console():
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)

            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.textview = TextViewConsole()
            self.textview.append_text("Vehicle status updates go here!\n")
            if valid is False:
               self.textview.append_text("Your selected path appears invalid, please double\n")
               self.textview.append_text("check the markers and adjust as necessary\n")
            sw.add(self.textview)
            vbox.pack_start(sw)
            return _frame(" Console ", vbox)


        def _buttons():
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)

	    self.cb_loop = gtk.CheckButton("_Loop Path")
	    self.cb_loop.set_active(False)
	    self.cb_loop.connect('clicked',self.set_loop)
            hbbox.pack_start(self.cb_loop)
            
            self.cb_auto_update = gtk.CheckButton("_Auto Update")
	    self.cb_auto_update.set_active(False)
	    self.cb_auto_update.connect('clicked',self.set_update)
            hbbox.pack_start(self.cb_auto_update)

            gtk.stock_add([(gtk.STOCK_DIALOG_QUESTION, "_Get Status", 0, 0, "")])
	    self.b_status = gtk.Button(stock=gtk.STOCK_DIALOG_QUESTION)
	    self.b_status.connect('clicked', self.get_statusW)
            hbbox.pack_start(self.b_status)


            gtk.stock_add([(gtk.STOCK_APPLY, "_Transmit Path", 0, 0, "")])
            self.b_transmit = gtk.Button(stock=gtk.STOCK_APPLY)
            self.b_transmit.connect('clicked', self.transmit, markers)
            hbbox.pack_start(self.b_transmit)

            
            return hbbox

	self.updates = []
        localPath = os.path.expanduser(init_path or DEFAULT_PATH)
        self.markerPath = os.path.join(localPath, 'asalt')
        fldDown = join(init_path, 'asalt')
	#self.statuses = fileUtils.read_asalt(self.markerPath)
	fileUtils.write_asalt(self.markerPath,self.updates)
        gtk.Window.__init__(self)
	self.set_default_size(750,366)

        vbox = gtk.VBox(False)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_console())
        vbox.pack_start(hbox)

        vbox.pack_start(_buttons(),expand=True,fill=False, padding=0)

        self.add(vbox)

        self.set_title("ASALT Vehicle Control")
        self.set_border_width(10)

        self.complete=[]
        self.connect('delete-event', self.on_delete)
        self.show_all()
        
        



    def transmit(self,w,markers):
        self.textview.append_text("transmitting!\n")
        print "transmitting!"
        self.astlr.send_float(markers,self.loop)

    def get_statusW(self,w):
	self.get_status()

    def get_status(self):
    	self.astlr.query()
    	status = "xx"
    	time.sleep(1)
    	status = self.astlr.receive_status()
    	print type(status)
    	if(isinstance(status,str)):
    	   self.textview.append_text(status)
    	else:   
	   self.textview.append_text("Lat=")
	   self.textview.append_text(str(status[0]))
	   self.textview.append_text("\nLong=")
	   self.textview.append_text(str(status[1]))
	   self.textview.append_text("\nPitch=")
	   self.textview.append_text(str(status[2]))
	   self.textview.append_text("\nRoll=")
	   self.textview.append_text(str(status[3]))
	   self.textview.append_text("\nHeading=")
	   self.textview.append_text(str(status[4]))
	   self.textview.append_text("\nStatus=")
	   self.textview.append_text(str(status[5]))
	   fileUtils.append_asalt(self.markerPath, status)
	   self.updates.append(status);
	   #print self.updates
        self.textview.append_text("\n===============================\n")


    def set_loop(self,w):
        if(self.loop ==1):
           self.loop = 0
           self.textview.append_text("path will NOT loop\n")
        else:
           self.loop = 1
           self.textview.append_text("path will now loop forever\n")
        print "loop =",self.loop

    def set_update(self,w):
    	if(self.auto_update == 1):
	   self.auto_update = 0
	   self.textview.append_text("Automatic Updates OFF\n")
	   self.auto_updater.cancel()
	else:
	   self.auto_update = 1
	   self.textview.append_text("Automatic Updates ON\n")
           self.auto_updater = AutoUpdater(2,self.get_status)
           self.auto_updater.start()	   
	   
    def get_updates(self):
        return self.updates


    def on_delete(self,*params):
    	fileUtils.write_asalt(self.markerPath,self.updates)
        return False
