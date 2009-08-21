## @package src.widMyGPS
# Change Theme widget used to change the GTK theme.
# Displayed inside a tab in MapTools.

import gtk
import fileUtils
from mapConst import *
from customWidgets import _myEntry, _SpinBtn, _frame, lbl


class MyGPS():

    ## All the buttons at the bottom
    def __action_buttons(self, conf):
        def btn_revert_clicked(button, conf):
            self.e_gps_updt_rate.set_text(str(conf.gps_update_rate))
            self.s_gps_max_zoom.set_value(conf.max_gps_zoom)
            self.cmb_gps_mode.set_active(conf.gps_mode)

        def btn_save_clicked(button, conf):
            conf.gps_update_rate = self.e_gps_updt_rate.get_text()
            conf.max_gps_zoom = self.s_gps_max_zoom.get_value_as_int()
            conf.gps_mode = self.cmb_gps_mode.self.cmb_service.get_active()
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
    def gps_updt_rate(self, gps_update_rate):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Here you can change the GPS update rate: "))
        self.e_gps_updt_rate = _myEntry(str(gps_update_rate), 4, False)
        hbox.pack_start(self.e_gps_updt_rate)
        return _frame(" GPS Update Rate ", hbox)

    ## Option to change the GPS max zoom
    def gps_max_zoom(self, max_gps_zoom):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Here you can set the maximum zoom for the GPS: "))
        self.s_gps_max_zoom = _SpinBtn(max_gps_zoom,
                MAP_MIN_ZOOM_LEVEL, MAP_MAX_ZOOM_LEVEL-1)
        hbox.pack_start(self.s_gps_max_zoom)
        return _frame(" GPS Max Zoom ", hbox)

    ## ComboBox to change the GPS mode
    def gps_mode_combo(self, gps_mode):
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl("Select your initial GPS mode: "))
        self.cmb_gps_mode = gtk.combo_box_new_text()
        for strMode in GPS_NAMES:
            self.cmb_gps_mode.append_text(strMode)
        self.cmb_gps_mode.set_active(gps_mode)
        hbox.pack_start(self.cmb_gps_mode)
        return _frame(" GPS Mode ", hbox)

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
        #vbox.pack_start(_frame(" Available themes ", hbox), False)
        vbox.pack_start(inner_box(), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        buttons = self.__action_buttons(conf)
        hpaned.pack2(buttons, False, False)
        return hpaned

