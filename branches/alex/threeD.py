## @package src.widASALTsettings
# GPS widget used to modify some GPS settings
# Displayed inside a tab in MapTools.

import gtk
import src.fileUtils
from src.customWidgets import _myEntry, _SpinBtn, _frame, lbl


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
        def inner_box():
            vbox = gtk.VBox(False, 10)
            vbox.pack_start(self.serial_port())
            hbox = gtk.HBox(False, 10)
            hbox.set_border_width(20)
            hbox.pack_start(vbox)
            return hbox

        vbox = gtk.VBox(False, 10)
        #hbox.pack_start(self.cmb_themes)
        #vbox.pack_start(_frame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        return hpaned

