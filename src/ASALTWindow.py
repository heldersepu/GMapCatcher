## @package src.ASALTWindow
# Widget that for the ASALT vehicle

import os
import pygtk
pygtk.require('2.0')
import gtk
import time
import fileUtils
import src.ASALTradio as ASALTradio
import widDrawingArea
from threading import Event, Thread

from customWidgets import _SpinBtn, _myEntry, _frame, lbl, FileChooser
from os.path import join, isdir


#Auto status updater thread
class AutoUpdater(Thread):
    def __init__(self,interval,update_function,):
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
    
    def __init__(self, config, markers, valid,drawing_area):
        
        def _console():
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)

            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.textview = TextViewConsole()
            self.textview.set_size_request(600, 300)
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
            #hbbox.set_size_request(200,100)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
	    vbox = gtk.VBox(False)
	    self.cb_loop = gtk.CheckButton("_Loop Path")
	    self.cb_loop.set_active(False)
	    self.cb_loop.connect('clicked',self.set_loop)
            vbox.pack_start(self.cb_loop)
            
            self.cb_auto_update = gtk.CheckButton("_Auto Update")
	    self.cb_auto_update.set_active(False)
	    self.cb_auto_update.connect('clicked',self.set_update)
            vbox.pack_start(self.cb_auto_update)
	    hbbox.pack_start(vbox)
            
            gtk.stock_add([(gtk.STOCK_STOP, "_Halt Vehicle", 0, 0, "")])
	    self.b_status = gtk.Button(stock=gtk.STOCK_STOP)
	    self.b_status.connect('clicked', self.stop_vehicle_check)
            hbbox.pack_start(self.b_status)
            
            
            gtk.stock_add([(gtk.STOCK_DIALOG_QUESTION, "_Get Status", 0, 0, "")])
	    self.b_status = gtk.Button(stock=gtk.STOCK_DIALOG_QUESTION)
	    self.b_status.connect('clicked', self.get_statusW)
            hbbox.pack_start(self.b_status)


            gtk.stock_add([(gtk.STOCK_APPLY, "_Transmit Path", 0, 0, "")])
            self.b_transmit = gtk.Button(stock=gtk.STOCK_APPLY)
            self.b_transmit.connect('clicked', self.transmit, markers)
            
            hbbox.pack_start(self.b_transmit)
            
            return hbbox
	vpane = gtk.VPaned()
	self.conf = config
	self.da = drawing_area
	self.asltr = ASALTradio.ASALTradio(self.conf)
	self.updates = []
        localPath = os.path.expanduser(self.conf.init_path or DEFAULT_PATH)
        self.asaltPath = os.path.join(localPath, 'asalt') 
        self.nogoPath = os.path.join(localPath, 'nogo') 
	#self.statuses = fileUtils.read_asalt(self.markerPath)
	fileUtils.write_asalt(self.asaltPath,self.updates)
        gtk.Window.__init__(self)
	self.set_default_size(750,366)

        vbox = gtk.VBox(False)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_console())
        vbox.pack_start(hbox)

	vpane.pack1(vbox)
        vpane.pack2(_buttons())
        
        self.add(vpane)

        self.set_title("ASALT Vehicle Control")
        self.set_border_width(10)

        self.complete=[]
        self.connect('delete-event', self.on_delete)
        self.show_all()
        
        



    def transmit(self,w,markers):
        self.textview.append_text("Transmitting markers to vehicle\n")
        self.asltr.send_float(markers,self.loop)

    def get_statusW(self,w):
	self.get_status()

    def get_status(self):
    	self.asltr.query()
    	time.sleep(1)
    	#status = self.asltr.receive_status()
    	statuses = [(36.98934567,-122.051176098,4.5234,9.2342,154.34,25698),(36.9895279812,-122.051196098,4.5234,9.2342,154.34,25698),(36.9895379812,-122.051196298,4.5234,9.2342,154.34,25698)]
    	if(isinstance(statuses,str)):
    	   self.textview.append_text(statuses)
    	else:   
	   for status in statuses:  
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
              for status_str in status[5]:
              	self.textview.append_text(status_str)
	      fileUtils.append_asalt(self.asaltPath, status)
              self.updates.append(status);
	      #print self.updates
              self.textview.append_text("\n===============================\n")
        self.da.repaint()

    def stop_vehicle(self,dialog,resp,c):
    	dialog.destroy()
	print resp
	if(resp == -9):
    		print "oops nm\n"
    	if(resp == -8):
    	        self.textview.append_text("\nHalting Vehicle!\n")
    	        self.asltr.send_stop()
    		
    		
    def stop_vehicle_check(self,w):
        dialog = gtk.MessageDialog(
	    parent         = None,
	    flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
	    type           = gtk.MESSAGE_INFO,
	    buttons        = gtk.BUTTONS_YES_NO,
	    message_format = "Are you sure you want to stop the vehicle???")
	dialog.set_title('Halt Vehicle')
        #dialog.connect('close', self.stop_vehicle,0)
        dialog.connect('response', self.stop_vehicle,1)
	dialog.run()        
        print "STOP!!!!!\n"

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
	   self.textview.append_text("updating status every ")
	   self.textview.append_text(str(self.conf.update_interval))
	   self.textview.append_text(" seconds\n")
           self.auto_updater = AutoUpdater(self.conf.update_interval,self.get_status)
           self.auto_updater.start()	   
	   
    def get_updates(self):
        return self.updates

    def get_nogo(self):
    	fileUtils.read_nogo(self.nogoPath)

    def on_delete(self,*params):
    	fileUtils.write_asalt(self.asaltPath,self.updates)
    	self.asltr.close()
        return False
