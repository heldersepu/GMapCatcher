## @package src.widASALTsettings
# GPS widget used to modify some GPS settings
# Displayed inside a tab in MapTools.

import gtk
import os
import src.fileUtils
from src.customWidgets import _myEntry, _SpinBtn, _frame, lbl
from numpy import *
from src.mapConf import MapConf 
import Gnuplot, Gnuplot.funcutils
import math


## This widget lets the user change GPS settings
class threeD():
    ## All the buttons at the bottom


    ## Option to change the GPS update rate
    def serial_port(self):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("3D Plot: "))
        self.e_serial_port = gtk.Entry()
        hbox.pack_start(self.e_serial_port)
        return _frame(" 3D Plot ", hbox)
    

    ## Put all the GPS Widgets together
    def show(self):
	
        self.conf = MapConf()
        print "file name is"
        print self.conf.upload_file
        print "got it"
        self.localP = os.path.expanduser(self.conf.init_path or DEFAULT_PATH)

        new_file =os.path.join(self.localP, 'new_file.dat')
        print "this is the DAT FILE"
        print new_file

	
        self.conf = MapConf()
        ifile = self.conf.upload_file
		
        def inner_box():
            vbox = gtk.VBox(False, 10)
            vbox.pack_start(self.serial_port())
            hbox = gtk.HBox(False, 10)
            hbox.set_border_width(20)
            hbox.pack_start(vbox)
            return hbox


        g = Gnuplot.Gnuplot() #!! Won't be able to use 'with' in python 2.6?
        g('set terminal png')
        g('set output "new_file.png"')
        g('splot "new_file.dat" with lines')
        g.reset()


        image = gtk.Image()
        image.set_from_file('new_file.png')
        image.show()
       
	   
        vbox = gtk.VBox(False, 10)
        #hbox.pack_start(self.cmb_themes)
        #vbox.pack_start(_frame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        hpaned.pack2(image, True, True)
        return hpaned

