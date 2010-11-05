# -*- coding: utf-8 -*-
## @package gmapcatcher.widMyGPS
# GPS widget used to modify some GPS settings
# Displayed inside a tab in MapTools.

from mapConst import *
if not IS_GTK:
    raise Exception('gtk module', __file__)

import gtk
import logging
log = logging.getLogger(__name__)
import fileUtils
from customWidgets import myEntry, SpinBtn, myFrame, lbl

## This widget lets the user change GPS settings
class MyGPS():
    ## All the buttons at the bottom
    def btn_save_clicked(self, button, conf):
        conf.gps_update_rate = self.e_gps_updt_rate.get_text()
        conf.max_gps_zoom = self.s_gps_max_zoom.get_value_as_int()
        conf.gps_mode = self.cmb_gps_mode.get_active()
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
        hbox.pack_start(lbl("Here you can change the GPS update rate: "))
        self.e_gps_updt_rate = myEntry(str(gps_update_rate), 4, False)
        hbox.pack_start(self.e_gps_updt_rate)
        return myFrame(" GPS Update Rate ", hbox)

    ## Option to change the GPS max zoom
    def gps_max_zoom(self, max_gps_zoom):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Here you can set the maximum zoom for the GPS: "))
        self.s_gps_max_zoom = SpinBtn(max_gps_zoom,
                MAP_MIN_ZOOM_LEVEL, MAP_MAX_ZOOM_LEVEL-1)
        hbox.pack_start(self.s_gps_max_zoom)
        return myFrame(" GPS Max Zoom ", hbox)

    ## ComboBox to change the GPS mode
    def gps_mode_combo(self, gps_mode):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select your initial GPS mode: "))
        self.cmb_gps_mode = gtk.combo_box_new_text()
        for strMode in GPS_NAMES:
            self.cmb_gps_mode.append_text(strMode)
        self.cmb_gps_mode.set_active(gps_mode)
        hbox.pack_start(self.cmb_gps_mode)
        return myFrame(" GPS Mode ", hbox)

    def key_press(self, widget, event, conf):
        if (event.state & gtk.gdk.CONTROL_MASK) != 0 and event.keyval in [83, 115]:
            # S = 83, 115
            self.btn_save_clicked(0, conf)

    ## Put all the GPS Widgets together
    def show(self, conf):
        def inner_box():
            vbox = gtk.VBox(False, 10)
            vbox.pack_start(self.gps_updt_rate(conf.gps_update_rate))
            vbox.pack_start(self.gps_max_zoom(conf.max_gps_zoom))
            vbox.pack_start(self.gps_mode_combo(conf.gps_mode))
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
        #vbox.pack_start(myFrame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        buttons = self.__action_buttons(conf)
        hpaned.pack2(buttons, False, False)
        hpaned.connect('key-press-event', self.key_press, conf)
        return hpaned

