## @package src.widUploadsettings
# GPS widget used to modify some GPS settings
# Displayed inside a tab in MapTools.

import gtk
import os
import pygtk
import fileUtils
from mapConst import *
from customWidgets import _myEntry, _SpinBtn, _frame, lbl, FolderChooser, FileChooser

## This widget lets the user change GPS settings
class Uploadsettings():
    ## All the buttons at the bottom
    uploadfile = False
    def __action_buttons(self, conf):
        def btn_revert_clicked(button, conf):
            self.e_upload_file.set_text(str(conf.upload_file))
            #self.radio_timeout.set_value(conf.query_timeout)
            #self.query_interval.set_active(conf.update_interval)

        def btn_save_clicked(button, conf):
			conf.upload_file = (self.entry_custom_path.get_text().lower()).strip()
			conf.init_path = conf.upload_file
			print (conf.upload_file)
			print (conf.init_path)
       #     if( os.pathsep == ';' ):
        #       # we have windows OS, filesystem is case insensitive
         #       newPath = (self.entry_custom_path.get_text().lower()).strip()
          #      oldPath = conf.init_path.lower().strip()
           # else:
            #    newPath = (self.entry_custom_path.get_text()).strip()
             #   oldPath = conf.init_path.strip()
                
   #         if newPath != "" and newPath != "none":
                #if strTemp != (conf.init_path.lower()).strip():
    #            if newPath != oldPath:
     #              	conf.init_path = self.entry_custom_path.get_text()
      #     	else:
       #    		conf.init_path = None
			conf.save()

        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', btn_revert_clicked, conf)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', btn_save_clicked, conf)
        bbox.add(button)
        return bbox
        
   # def custom_path(conf):

    ## Option to change the GPS update rate
    def upload_file(self, conf):
    
    	def get_folder(button):
    		folderName = FileChooser(os.path.expanduser(USER_PATH))
    		if folderName:
    			self.entry_custom_path.set_text(folderName)
    				
   	def set_folder(button):
    		self.entry_custom_path.set_text(os.path.join(os.path.expanduser(USER_PATH)))
    
        hbox = gtk.HBox(False, 15)
        hbox.pack_start(lbl("Upload File: "))
        self.e_upload_file = gtk.Entry()
        self.e_upload_file.set_text(os.path.expanduser(USER_PATH))
        self.entry_custom_path = self.e_upload_file
        button = gtk.Button(" ... ")
        button.connect('clicked', get_folder)
        hbox.pack_start(self.e_upload_file)

        hbox.pack_start(button, False)
#        print Uploadsettings.uploadfile
        return _frame(" Upload File ", hbox)
        
   		

        
    def get_file(self, widget):
    
    	strFileName = False
       	dialog = gtk.FileChooserDialog("Open..",
	                               None,
	                               gtk.FILE_CHOOSER_ACTION_OPEN,
	                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
	                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
       	dialog.set_default_response(gtk.RESPONSE_OK)

	# filter = gtk.FileFilter()
	# filter.set_name("All files")
	# filter.add_pattern("*")
	# dialog.add_filter(filter)

       	filter = gtk.FileFilter()
       	filter.set_name("csv files")
       	filter.add_pattern("*.csv")
       	dialog.add_filter(filter)
	
       	response = dialog.run()
       	if response == gtk.RESPONSE_OK:
       	    print dialog.get_filename(), 'selected'
       	    strFileName = dialog.get_filename()
       	    print strFileName.get_text()
       	elif response == gtk.RESPONSE_CANCEL:
        	print 'Closed, no files selected'
    	    
       	dialog.destroy()
       	return strFileName 

    ## Put all the GPS Widgets together
    def show(self, conf):
        def inner_box():
            vbox = gtk.VBox(False, 15)
            vbox.pack_start(self.upload_file(conf.upload_file))
            hbox = gtk.HBox(False, 15)
            hbox.set_border_width(20)
            hbox.pack_start(vbox)
            return hbox

        vbox = gtk.VBox(False, 10)
        vbox.set_border_width(10)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select new theme and restart GMapCatcher."))
        self.cmb_themes = gtk.combo_box_new_text()

        hbox.pack_start(self.cmb_themes)
        #vbox.pack_start(_frame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        buttons = self.__action_buttons(conf)
        hpaned.pack2(buttons, False, False)
        return hpaned

