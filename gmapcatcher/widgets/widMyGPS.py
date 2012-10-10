# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.widMyGPS
# GPS widget used to modify some GPS settings
# Displayed inside a tab in MapTools.

import gtk
from gmapcatcher.mapConst import *
from gmapcatcher.serialGPS import serialPortScan, BAUDRATES, available as serialAvailable
from customWidgets import SpinBtn, myFrame, lbl


## This widget lets the user change GPS settings
class MyGPS(gtk.VPaned):
    ## All the buttons at the bottom
    def btn_save_clicked(self, button, conf):
        conf.gps_update_rate = self.e_gps_updt_rate.get_value()
        conf.max_gps_zoom = self.s_gps_max_zoom.get_value_as_int()
        conf.gps_mode = self.cmb_gps_mode.get_active()
        conf.gps_type = self.cmb_gps_type.get_active()
        conf.gps_track = int(self.cb_gps_track.get_active())
        conf.gps_track_width = self.sb_gps_track_width.get_value_as_int()
        conf.gps_track_interval = self.sb_gps_track_interval.get_value_as_int()
        if serialAvailable:
            conf.gps_serial_port = self.cmb_gps_serial_port.get_active_text()
            conf.gps_serial_baudrate = int(self.cmb_gps_baudrate.get_active_text())
        conf.save()

    def __action_buttons(self, conf):
        def btn_revert_clicked(button, conf):
            self.e_gps_updt_rate.set_text(str(conf.gps_update_rate))
            self.s_gps_max_zoom.set_value(conf.max_gps_zoom)
            self.cmb_gps_mode.set_active(conf.gps_mode)

        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', btn_revert_clicked, conf)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', self.btn_save_clicked, conf)
        bbox.add(button)
        return bbox

    ## Option to change the GPS update rate
    def gps_updt_rate(self, gps_update_rate):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("GPS update rate in seconds: "))
        self.e_gps_updt_rate = SpinBtn(gps_update_rate, 0.1, 100, 0.1, 5, False)
        self.e_gps_updt_rate.set_digits(1)
        hbox.pack_start(self.e_gps_updt_rate)
        return hbox

    ## Option to change the GPS max zoom
    def gps_max_zoom(self, max_gps_zoom):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Maximum zoom for GPS: "))
        self.s_gps_max_zoom = SpinBtn(max_gps_zoom,
                MAP_MIN_ZOOM_LEVEL, MAP_MAX_ZOOM_LEVEL - 1)
        hbox.pack_start(self.s_gps_max_zoom)
        return hbox

    ## ComboBox to change the GPS mode
    def gps_mode_combo(self, gps_mode):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Initial GPS mode: "))
        self.cmb_gps_mode = gtk.combo_box_new_text()
        for strMode in GPS_NAMES:
            self.cmb_gps_mode.append_text(strMode)
        self.cmb_gps_mode.set_active(gps_mode)
        hbox.pack_start(self.cmb_gps_mode)
        return hbox

    ## Changes to the gps type combo box
    def cmb_gps_changed(self, w):
        sensitive = (w.get_active() > GPS_DISABLED)
        self.boxes[1].set_sensitive(sensitive)
        self.boxes[2].set_sensitive(sensitive)
        self.boxes[3].set_sensitive(sensitive)

    ## ComboBox to change the GPS type
    def gps_type_combo(self):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("GPS type: "))
        self.cmb_gps_type = gtk.combo_box_new_text()
        for strType in GPS_TYPES:
            self.cmb_gps_type.append_text(strType)
        self.cmb_gps_type.connect('changed', self.cmb_gps_changed)
        hbox.pack_start(self.cmb_gps_type)
        return hbox

    ## Settings for GPS track:
    def gps_track_settings(self, gps_track, track_width, track_interval):
        self.cb_gps_track = gtk.CheckButton('Draw GPS track')
        self.cb_gps_track.set_active(gps_track)
        self.sb_gps_track_width = SpinBtn(track_width, 1, 20, 1, 2)
        self.sb_gps_track_interval = SpinBtn(track_interval, 1, 1000, 10, 4)

        vbox = gtk.VBox(False, 10)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(self.cb_gps_track)
        hbox.pack_start(lbl("Track width: "))
        hbox.pack_start(self.sb_gps_track_width)
        hbox.pack_start(lbl("Point interval (in meters): "))
        hbox.pack_start(self.sb_gps_track_interval)
        vbox.pack_start(hbox)
        return myFrame(" GPS track ", vbox)

    ## ComboBox to select serial port
    def gps_serial_port_combo(self, serial_port):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Serial port: "))
        self.cmb_gps_serial_port = gtk.combo_box_new_text()
        i = 0
        ports = serialPortScan()
        # Adding current port from config to the list,
        # in case the GPS just isn't currently connected, we don't want to lose it...
        if serial_port not in ports:
            ports.insert(0, serial_port)
        for strPort in ports:
            self.cmb_gps_serial_port.append_text(strPort)
            if strPort == serial_port:
                self.cmb_gps_serial_port.set_active(i)
            i += 1
        hbox.pack_start(self.cmb_gps_serial_port)
        return hbox

    ## ComboBox to change the GPS serial baudrate
    def gps_baudrate_combo(self, baudrate):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Serial port baudrate: "))
        self.cmb_gps_baudrate = gtk.combo_box_new_text()
        i = 0
        for baud in BAUDRATES:
            self.cmb_gps_baudrate.append_text(str(baud))
            if baud == baudrate:
                self.cmb_gps_baudrate.set_active(i)
            i += 1
        hbox.pack_start(self.cmb_gps_baudrate)
        return hbox

    def key_press(self, widget, event, conf):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [83, 115]:
            # S = 83, 115
            self.btn_save_clicked(0, conf)

    ## Put all the GPS Widgets together
    def show(self, conf):
        def general_gps_box():
            self.boxes = [self.gps_type_combo(), self.gps_updt_rate(conf.gps_update_rate),
                    self.gps_max_zoom(conf.max_gps_zoom), self.gps_mode_combo(conf.gps_mode)]
            vbox = gtk.VBox(False, 5)
            for box in self.boxes:
                hbox = gtk.HBox(False, 10)
                hbox.pack_start(box)
                vbox.pack_start(hbox)
            return myFrame(" GPS ", vbox)

        def gps_serial_box():
            vbox = gtk.VBox(False, 5)
            if serialAvailable:
                boxes = [self.gps_serial_port_combo(conf.gps_serial_port), self.gps_baudrate_combo(conf.gps_serial_baudrate)]
                for box in boxes:
                    hbox = gtk.HBox(False, 10)
                    hbox.pack_start(box)
                    vbox.pack_start(hbox)
            else:
                vbox.pack_start(lbl('Install python-serial to use serial GPS.'))
            return myFrame(" Serial ", vbox)

        vbox = gtk.VBox(False, 10)
        vbox.set_border_width(10)

        vbox.pack_start(general_gps_box(), False)
        vbox.pack_start(self.gps_track_settings(conf.gps_track, conf.gps_track_width, conf.gps_track_interval))
        vbox.pack_start(gps_serial_box(), False)

        self.pack1(vbox, True, True)
        buttons = self.__action_buttons(conf)
        self.pack2(buttons, False, False)
        self.connect('key-press-event', self.key_press, conf)
        self.cmb_gps_type.set_active(conf.gps_type)
        return self
