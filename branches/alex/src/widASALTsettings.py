## @package src.widASALTsettings
# GPS widget used to modify some GPS settings
# Displayed inside a tab in MapTools.

import gtk
import fileUtils
from mapConst import *
from customWidgets import _myEntry, _SpinBtn, _frame, lbl

## This widget lets the user change GPS settings
class ASALTsettings():
    ## All the buttons at the bottom
    def __action_buttons(self, conf):
        def btn_revert_clicked(button, conf):
            self.e_serial_port.set_text(str(conf.serial_port))
            self.radio_timeout.set_value(conf.query_timeout)
            self.query_interval.set_active(conf.update_interval)

        def btn_save_clicked(button, conf):
            conf.serial_port = self.e_serial_port.get_text()
            conf.baud_rate = int(self.e_serial_baud.get_text())
            conf.query_timeout = int(self.e_radio_timeout.get_text())
            conf.update_interval = int(self.e_query_interval.get_text())
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

    ## Option to change the GPS update rate
    def serial_port(self, serial_port):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Set Serial Port: "))
        self.e_serial_port = gtk.Entry()
        self.e_serial_port.set_text(serial_port)
        hbox.pack_start(self.e_serial_port)
        return _frame(" Serial Port ", hbox)
    
    ## Option to change the GPS update rate
    def serial_baud(self, serial_baud):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Set Serial Baud Rate: "))
        self.e_serial_baud = _myEntry(str(serial_baud), 6, False)
        hbox.pack_start(self.e_serial_baud)
        return _frame(" Baud Rate ", hbox)    

    def radio_timeout(self, radio_timeout):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Set the Radio Timeout in Seconds: "))
        self.e_radio_timeout = _myEntry(str(radio_timeout), 6, False)
        hbox.pack_start(self.e_radio_timeout)
        return _frame(" Radio Timeout ", hbox)    

    def query_interval(self, query_interval):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Set the Status Query interval in Seconds: "))
        self.e_query_interval = _myEntry(str(query_interval), 6, False)
        hbox.pack_start(self.e_query_interval)
        return _frame(" Query Interval ", hbox)   

    ## Put all the GPS Widgets together
    def show(self, conf):
        def inner_box():
            vbox = gtk.VBox(False, 10)
            vbox.pack_start(self.serial_port(conf.serial_port))
            vbox.pack_start(self.serial_baud(conf.baud_rate))
            vbox.pack_start(self.radio_timeout(conf.query_timeout))
            vbox.pack_start(self.query_interval(conf.update_interval))
            hbox = gtk.HBox(False, 10)
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

